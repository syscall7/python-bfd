__author__ = 'davis'

import os
import re
import string
import bfd
import dischunk
from django.contrib.contenttypes.models import ContentType

from odaweb.models import BinaryDisassemblyChunk, Binary, BinaryString, BinaryFile, OdaMaster, OdaOptions


def funcFmtAddr(bfd, addr):
    addrStr = '0x%08x' % addr
    if bfd.syms_by_addr.has_key(addr):
        addrStr += ' <%s>' % bfd.syms_by_addr[addr].name
    return addrStr

def funcFmtLine(addr, rawData, instr, abfd):
    from cStringIO import StringIO
    file_str = StringIO()
    if abfd.syms_by_addr.has_key(addr):
        file_str.write('\n0%08x <%s>:\n' % (addr, abfd.syms_by_addr[addr].name))
    if abfd.bpc > 1 and (abfd.endian is bfd.ENDIAN_LITTLE or abfd.endian is bfd.ENDIAN_DEFAULT):
        bytes = ''.join(['%02x ' % i for i in reversed(rawData)])
    else:
        bytes = ''.join(['%02x ' % i for i in rawData])

    file_str.write(' %08x %-32s %s\n' % (addr, bytes, instr))
    return file_str.getvalue()

def analyzerFactory(arch):

    # for now, ignore everything after the colon
    arch = arch.split(':')[0]
    name = 'odaweb.analyzers.'+arch
    try:
        mod = __import__(name)
    except ImportError:
        return analyzerFactory('defaultAnalyzer')

    components = name.split('.')
    for comp in components[1:]:
        mod = getattr(mod, comp)

    initFunc = getattr(mod, arch)
    obj = initFunc()

    return obj

class Disassembler(object):

    def __init__(self, binary):

        self.binary = binary

        self.file_handle = binary.file_handle()

        self.filename = self.file_handle.name

        self.bfd = bfd.Bfd(self.filename, binary.options.target, binary.options.architecture)

        self.sections = list(self.bfd.sections.values())

        for s in self.sections:
            for f in bfd.FLAGS:
                if f.name in s.flags:
                    setattr(self, f.name, True) # i.e, section.SEC_ALLOC = True
                else:
                    setattr(self, f.name, False) # i.e, section.SEC_ALLOC = False


    def sectionFlagsInfo(self):
        return bfd.FLAGS

    def strings(self):
        strs = []
        bin = open(self.filename, "rb").read()
        for m in re.finditer("([\t\x20-\x7e]{4,})", bin):
            strs.append((m.start(), m.group(1)))
        return strs

    def sections_iter(self, flags=[]):
        '''Iterate over all sections (in ascending address order) that have all give flags specified'''
        for sec in self.sections:
            sec_flags = [f.name for f in sec.flags]
            if set(flags).issubset(sec_flags):
                yield sec

    def disassemble(self, name, start=None, stop=None, numLines=None, endian=bfd.ENDIAN_DEFAULT, options=''):
        sec = self.bfd.sections[name]

        # this is to force the i386 strcpy example to use intel syntax...need a better solution
        if self.bfd.arch.startswith('i386') and options == '':
            options = 'intel-mnemonic'

        dis = self.bfd.disassemble(sec, start, stop, numLines, funcFmtAddr, funcFmtLine, endian, options)
        return dis

    def symbol(self, lookup):
        '''Lookup can either be address or name'''
        if type(lookup) == int:
            return bfd.syms_by_addr[lookup]
        elif type(lookup) == string:
            return bfd.syms_by_name[lookup]
        else:
            raise Exception('Can\'t lookup symbol by type %s' % type(lookup))

    def symbols(self):
        '''Returns a list of Symbols sorted by increasing address'''
        return [sym for (name, sym) in sorted(self.bfd.syms_by_name.iteritems(), key=lambda (name, sym): sym.value)]

    def get_code_sections(self):
        class SectionInfo(object):
            def __init__(self, code_sections):
                self.code_sections = code_sections
                if len(code_sections):
                    self.start_addr = code_sections[0].vma
                    self.stop_addr = code_sections[-1].vma + code_sections[-1].size
                else:
                    self.start_addr = 0
                    self.stop_addr = 0

            addr_range = property(lambda self: self.stop_addr - self.start_addr)

        def filter_sec_code(sec):
            return {'SEC_CODE'}.issubset([f.name for f in sec.flags])

        # HACK: if there's only one section, it's the .data section for raw binaries, so let's include it
        if len(self.sections) == 1 and self.sections[0].name == '.data':
            code_sections = self.sections
        # else, only get the code sections
        else:
            code_sections = filter(filter_sec_code, self.sections)

        section_info = SectionInfo(code_sections)

        return section_info

    def get_chunks_from_file(self, sections):
        chunks = []
        for sec in sections:

            # Initialize loop variables
            sec_consumed = 0
            sec_offset_addr = sec.vma

            while sec_consumed < sec.size:

                # Disassemble a chunk
                chunk_size = min( dischunk.DisChunk.MIN_CHUNK_SIZE_BYTES,sec.size-sec_consumed)
                disassembly, next_addr, num_lines = self.disassemble(sec.name, sec_offset_addr, sec_offset_addr+chunk_size)

                # Save the disassembly
                # file_str.write( disassembly )

                #print "DISASSEMBLE CHUNK:",len(chunks)

                # Save the chunk
                chunks.append( dischunk.DisChunk(sec_offset_addr, next_addr, num_lines, sec.name) )

                # Update loop variables
                sec_consumed += chunk_size
                sec_offset_addr = next_addr

        return chunks

    def process_chunks(self):
        ctype = ContentType.objects.get_for_model(self.binary)
        BinaryDisassemblyChunk.objects.filter(content_type=ctype.id, object_id=self.binary.id).delete()

        chunks = []

        # Disassemble the entire file, one section at a time, dividing it into disassembly chunks
        if self.binary.options.target == 'binary':
            chunks = self.get_chunks_from_file(self.sections)
        else:
            chunks = self.get_chunks_from_file(self.sections_iter(['SEC_CODE']))


        # Note the boundary chunks
        chunks[0].is_boundary = True
        chunks[len(chunks)-1].is_boundary = True

        i = 0
        for chunk in chunks:
            ch = BinaryDisassemblyChunk(id=None,
                sec_name=chunk.sec_name,
                start=chunk.start,
                end=chunk.end,
                bfd_lines=chunk.lines,
                is_boundary=chunk.is_boundary,
                binary=self.binary)
            ch.save()
            i+=1

    def mk_hex_lines(self, chunks):
        LINE_WIDTH = 16

        def toAscii(line):
            ascii = []
            printable = string.digits + string.letters + string.punctuation
            for c in line:
                if c in printable:
                    ascii.append(c)
                elif c == ' ':
                    ascii.append('&nbsp;')
                else:
                    ascii.append('.')

            # pad out to LINE_WIDTH
            ascii.extend(['&nbsp;']*(LINE_WIDTH-len(line)))

            return ascii

        def toHex(line):

            hex = ['%02x' % c for c in map(ord, line)]

            # pad out to LINE_WIDTH
            hex.extend(['&nbsp;&nbsp;']*(LINE_WIDTH-len(line)))

            return hex

        for chunk in chunks:
            # TODO: Deal with sections whose start address is not LINE_WIDTH aligned
            rounded_start = chunk.start & ~(LINE_WIDTH-1)
            rounded_end = chunk.end & ~(LINE_WIDTH-1)
            raw = self.bfd.raw_data(self.bfd.sections[chunk.sec_name], rounded_start, rounded_end - rounded_start)
            raw_lines = [raw[i:i+LINE_WIDTH] for i in range(0,len(raw),LINE_WIDTH)]
            addr = rounded_start
            chunk.hex_lines = []
            for line in raw_lines:
                ascii = toAscii(line)
                hex = toHex(line)
                chunk.hex_lines.append((addr, hex, ascii))
                addr += len(line)
                



class JsonChunkProcessor(object):
    def __init__(self, binary):
        self.binary = binary

    def get_chunks_from_addr(self, addr, num_chunks):
        analyzer = analyzerFactory( self.binary.options.architecture )

        ctype = ContentType.objects.get_for_model(self.binary)

        # The requested address is the center chunk. We need to get chunks
        #    before and after the center chunk (if possible)
        
        # Chunks after an address are easier to retrieve. Retrieve the 
        #    maximum number in case there is a shortage of chunks before 
        #    the provided address. Include the chunk that contains the 
        #    provided address
        #    Note: afterChunks does not include the center chunk
        afterChunks = BinaryDisassemblyChunk.objects.filter(
            content_type=ctype.id, object_id = self.binary.id, start__gte = addr )[0:num_chunks]
        
        # Determine how many chunks before the address that we need to get
        numAfterChunks = len(afterChunks)
        if numAfterChunks >= (num_chunks//2):
            # Plenty of chunks, request the minimum beforeChunks
            numRequested = (num_chunks//2) + 1
        else:
            # Towards the back of the address space, or a very small file
            #    Request more chunks before the given address to make up
            #    the difference
            numRequested = num_chunks - numAfterChunks
            
        # Get the chunks before the address (including the center chunk)
        beforeChunksReversed = BinaryDisassemblyChunk.objects.filter(
            content_type=ctype.id, object_id = self.binary.id, start__lt = addr ).order_by('-start')[0:numRequested]      
        
        # Chunks before the given chunk but in reverse order
        beforeChunks = list(beforeChunksReversed)
        beforeChunks.reverse()
        
        # Get the chunks to return 
        numBeforeChunks = len(beforeChunks)
        numAfterChunks = num_chunks - numBeforeChunks
        print "BEFORE: %d, AFTER %d" % (numBeforeChunks,numAfterChunks)         
        permachunks = beforeChunks + afterChunks[0:numAfterChunks]    

        architecture = self.binary.options.architecture

        analyzer = analyzerFactory(architecture)

        return self.process_chunks(analyzer, permachunks)

    def get_chunks_from_chunk(self, name, start, end, direction, num_chunks):
        analyzer = analyzerFactory( self.binary.options.architecture )

        ctype = ContentType.objects.get_for_model(self.binary)

        if direction == 1:
            # Chunks after the given chunk
            permachunks = BinaryDisassemblyChunk.objects.filter(
                content_type=ctype.id, object_id = self.binary.id, start__gt = start )[0:num_chunks]
        else:
            # Chunks before the given chunk
            permachunksReversed = BinaryDisassemblyChunk.objects.filter(
                content_type=ctype.id, object_id = self.binary.id, start__lt = start ).order_by('-start')[0:num_chunks]      
            
            # Chunks before the given chunk but in reverse order
            permachunks = list(permachunksReversed)
            permachunks.reverse()
        
        return self.process_chunks(analyzer, permachunks)

    def process_chunks(self, analyzer, permachunks):

        # Build a list of chunks to process
        new_chunks = []

        for chunk in permachunks:
            print "APPEND CHUNK 0x%x" % (chunk.start)
            new_chunks.append( dischunk.DisChunk(chunk.start, chunk.end, chunk.bfd_lines, chunk.sec_name, chunk.is_boundary) )

        dasm = Disassembler(self.binary)
        analyzer.analyze( dasm, new_chunks )
        dasm.mk_hex_lines(new_chunks)
        chunk.hex_lines = '<>'
        # Build a primitive object containing the list of chunk data to pass back to the client
        chunk_list = []
        for chunk in new_chunks:
            chunk_list.append ({
                'sec_name': chunk.sec_name,
                'startOffset': chunk.start,
                'endOffset': chunk.end,
                'isBoundary': chunk.is_boundary,
                'lines': chunk.lines,
                'hex_lines' : chunk.hex_lines
            })

        return analyzer.chunks, chunk_list


def make_examples():

    EXAMPLES_DIR = os.path.join(os.path.dirname(__file__), 'examples')
    examples = (
        {
            'short_name' : 'sha1sum',
            'binary_type' : 'file',
            'file_name' : 'sha1sum',
            'options' : OdaOptions(target="elf32-i386", architecture="i386"),
        },
        {
            'short_name' : 'sasser',
            'binary_type' : 'file',
            'file_name' : 'net-worm.win32.sasser.a',
            'options' : OdaOptions(target="elf32-i386", architecture="i386"),
        },
        {
            'short_name' : 'strcpy_x86',
            'binary_type' : 'string',
            'data' : '55 31 D2 89 E5 8B 45 08 56 8B 75 0C 53 8D 58 FF 0F B6 0C 16 88 4C 13 01 83 C2 01 84 C9 75 F1 5B 5E 5D C3 ',
            'options' : OdaOptions(target="binary", architecture="i386"),
        },
    )

    for example in examples:
        short_name = example['short_name']
        if OdaMaster.objects.filter(short_name=short_name).exists():
            print 'Example %s already exists in the database' % short_name
            continue

        print 'Adding example %s to database' % short_name

        options = example['options']
        options.save()

        if example['binary_type'] is 'file':
            f = open(os.path.join(EXAMPLES_DIR, example['file_name']),'rb')
            binary = BinaryFile.create(f, options)
            binary.save()
        elif example['binary_type'] is 'string':
            binary = BinaryString()
            binary.binary_string = ''.join(example['data'].split())
            binary.options = options
            binary.save()

        oda_master = OdaMaster(short_name = short_name, binary = binary)
        oda_master.save()

        disassembler = Disassembler(binary)
        disassembler.process_chunks()

