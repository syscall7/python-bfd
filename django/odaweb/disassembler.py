__author__ = 'davis'

import bfd
import dischunk
from django.contrib.contenttypes.models import ContentType

from odaweb.models import BinaryDisassemblyChunk, Binary, BinaryString, OdaMaster, OdaOptions


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

    def symbols(self):
        return dict(sorted(self.bfd.syms_by_addr.iteritems()))

    def get_sections_code(self):
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

        section_info = SectionInfo(filter(filter_sec_code, self.sections))

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


class JsonChunkProcessor(object):
    def __init__(self, binary):
        self.binary = binary

    def get_chunk_html(self, addr, num_chunks):
        analyzer = analyzerFactory( self.binary.options.architecture )

        ctype = ContentType.objects.get_for_model(self.binary)

        #permachunk = BinaryDisassemblyChunk.objects.filter(
        #    content_type=ctype.id, object_id = self.binary.id, start__lte = addr, end__gte = addr )[0]
        permachunks = BinaryDisassemblyChunk.objects.filter(
            content_type=ctype.id, object_id = self.binary.id)[:7]

        chunk_count = BinaryDisassemblyChunk.objects.filter(content_type=ctype.id, object_id=self.binary.id).count()

        architecture = self.binary.options.architecture

        analyzer = analyzerFactory(architecture)

        count = chunk_count
        if (chunk_count < num_chunks):
            count = chunk_count

        #start_index = permachunk.id - (DISASSEMBLY_WINDOW_SIZE_CHUNKS/2)
        #if start_index < 0:
        #   start_index = 0
        #if (start_index + count) > chunk_count:
        #    start_index = chunk_count - count
        start_index = 0
        count = 7

        return self.process_chunks(analyzer, permachunks, start_index, count)

    def process_chunks(self, analyzer, permachunks, index, count):

        # Build a list of chunks to process
        new_chunks = []

        for chunk in permachunks[index:index+count]:
            new_chunks.append( dischunk.DisChunk(chunk.start, chunk.end, chunk.bfd_lines, chunk.sec_name, chunk.is_boundary) )

        analyzer.analyze( Disassembler(self.binary), new_chunks )

        # Build a primitive object containing the list of chunk data to pass back to the client
        chunk_list = []
        for chunk in new_chunks:
            chunk_list.append ({
                'sec_name': chunk.sec_name,
                'startOffset': chunk.start,
                'endOffset': chunk.end,
                'isBoundary': chunk.is_boundary,
                'lines': chunk.lines
            })

        return analyzer.chunks, chunk_list


def create_default_view(short_name):


    options = OdaOptions(target="binary", architecture="i386")
    options.save()

    binary = BinaryString()
    binary.binary_string = ''.join('55 31 D2 89 E5 8B 45 08 56 8B 75 0C 53 8D 58 FF 0F B6 0C 16 88 4C 13 01 83 C2 01 84 C9 75 F1 5B 5E 5D C3 '.split())
    binary.options = options
    binary.save()

    oda_master = OdaMaster()
    oda_master.short_name = short_name
    oda_master.binary = binary
    oda_master.save()

    disassembler = Disassembler(oda_master.binary)
    disassembler.process_chunks()

    return oda_master