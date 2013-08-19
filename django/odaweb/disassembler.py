__author__ = 'davis'

import re
import string
import bfd
import dischunk
import time
import os
from django.contrib.contenttypes.models import ContentType

from odaweb.models import (BinaryDisassemblySuperChunk, Binary, BinaryString,
                           BinaryFile, OdaMaster, OdaOptions, Comment,
                           BinaryDisassemblyChunk)

import logging

logger = logging.getLogger(__name__)

TARGETS_WITHOUT_CODE_SECTIONS = ['binary', 'ihex', 'srec']

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


def get_supported_archs():
    '''Return a list of all architectures supported
    '''
    supportedArchs = bfd.list_architectures()

    # Remove Problem archs
    problemArchs = ['MicroBlaze',
                    'i960:ka_sa',
                    'i960:kb_sb',
                    'r800',
                    'moxie',
                    ]

    for arch in problemArchs:
        supportedArchs.remove(arch)

    return supportedArchs

def get_supported_endians():

    endians = {
        'DEFAULT' : bfd.ENDIAN_DEFAULT,
        'LITTLE'  : bfd.ENDIAN_LITTLE,
        'BIG'     : bfd.ENDIAN_BIG
    }

    return endians


def get_platform_options(platform):
    djhtmlOpts = []
    analyzer = analyzerFactory(platform)
    if analyzer == None:
        analyzer = analyzerFactory('defaultAnalyzer')

    #print "Checking if"
    if analyzer.options:
        #print "ANalyzer",analyzer.options
        for opt in analyzer.options:
        # Form the name of the widget by stripping out options
            widgetName = opt[0].replace(' ', '')
            widgetType = ''
            if opt[2] == 'CHOICE' or opt[2] == 'BOOL':
                widgetType = 'select'
                widgetName += widgetType

            # Build the Modal
            djhtmlOpts.append((widgetName,widgetType) + opt)
            #print 'DHTML',djhtmlOpts
    return djhtmlOpts

# Returns our best guess at target (file format) and architecture
def guess_bfd_arch(filename):

    # use defaults these default when we can't detect the arch/target
    arch = 'UNKNOWN!'
    target = 'binary'
    try:
        target_archs = bfd.guess_target_arch(filename)

        # TODO: Present these options to the user and let them pick from all matching target/archs

        # for each detected target/arch
        for (t, a) in target_archs:

            # we'll set the target here even in cases where we cannot detect arch (i.e., ihex, srec)
            target = t
            if a != "UNKNOWN!":
                arch = a
                break

    except bfd.BfdFileFormatException, e:
        pass
    except Exception, e:
        pass

    return arch, target


class Disassembler(object):

    def __init__(self, binary):

        self.binary = binary

        self.bfd_file_handle = binary.file_handle()
        filename = self.bfd_file_handle.name

        self.bfd = bfd.Bfd(filename, binary.options.target, binary.options.architecture)

        self.sections = list(self.bfd.sections.values())

        for s in self.sections:
            for f in bfd.FLAGS:
                if f.name in s.flags:
                    setattr(self, f.name, True) # i.e, section.SEC_ALLOC = True
                else:
                    setattr(self, f.name, False) # i.e, section.SEC_ALLOC = False
    def __del__(self):
        if hasattr(self, 'bfd'):
            self.bfd.close()
            self.bfd_file_handle.close()
            self.bfd_file_handle.done()

    def sectionFlagsInfo(self):
        return bfd.FLAGS

    def strings(self):
        strs = []
        # Create temporary file handle to retrieve strings
        f = self.binary.file_handle()
        f.open("rb")
        bin = f.read()
        for m in re.finditer("([\t\x20-\x7e]{4,})", bin):
            strs.append((m.start(), m.group(1)))
        f.close()
        f.done()
        return strs

    def sections_iter(self, flags=[]):
        '''Iterate over all sections (in ascending address order) that have all give flags specified'''
        for sec in self.sections:
            sec_flags = [f.name for f in sec.flags]
            if set(flags).issubset(sec_flags):
                yield sec

    def disassemble(self, name, start=None, stop=None, numLines=None, funcFmtLine=None, funcFmtLineArgs=None):
        sec = self.bfd.sections[name]

        options = self.binary.options.get_extra_options()

        # determine endianness
        if 'LITTLE' in options:
            endian = bfd.ENDIAN_LITTLE
        elif 'BIG' in options:
            endian = bfd.ENDIAN_BIG
        else:
            endian = bfd.ENDIAN_DEFAULT

        # force intel syntax as default for i386 arch
        if self.bfd.arch.startswith('i386') and len(options) == 0:
            options = ['intel-mnemonic']

        options_string = ",".join(options)

        dis = self.bfd.disassemble(sec, start, stop, numLines, None, funcFmtLine, funcFmtLineArgs, endian, options_string)
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
                    self.stop_addr = code_sections[-1].vma + code_sections[-1].size - 1
                else:
                    self.start_addr = 0
                    self.stop_addr = 0

            addr_range = property(lambda self: self.stop_addr - self.start_addr)

        def filter_sec_code(sec):
            return set(['SEC_CODE']).issubset([f.name for f in sec.flags])

        # treat all sections as code for targets without code sections
        if self.bfd.target in TARGETS_WITHOUT_CODE_SECTIONS:
            code_sections = self.sections
        # else, only get the code sections
        else:
            code_sections = filter(filter_sec_code, self.sections)

        section_info = SectionInfo(code_sections)

        return section_info
    
    def get_chunks_from_file(self, sections):
        super_chunks = []
        cur_super_chunk = dischunk.DisSuperChunk()
        
        for sec in sections:

            # Initialize loop variables
            sec_consumed = 0
            sec_offset_addr = sec.vma

            while sec_consumed < sec.size:

                disassemble_size = min( cur_super_chunk.available_len(), sec.size-sec_consumed )

                # Disassemble a chunk
                disassembly, next_addr, num_lines = self.disassemble(sec.name, sec_offset_addr, sec_offset_addr+disassemble_size)

                # when disassembling binaries, weird things can happen...this is one of them
                if next_addr <= sec_offset_addr:
                    break
                
                # Update Size 
                disassemble_size = next_addr - sec_offset_addr

                # Grow the super chunk
                cur_super_chunk.grow(sec.name, sec_offset_addr, disassemble_size)

                # Check if we need to add another super chunk 
                if cur_super_chunk.available_len() == 0 or disassemble_size == 0:
                    # Not enough room in the chunk to add to it
                    #    Get a new chunk
                    super_chunks.append(cur_super_chunk)
                    cur_super_chunk = dischunk.DisSuperChunk()

                # Update loop variables
                sec_consumed += disassemble_size
                sec_offset_addr = next_addr

        # Include the last chunk
        if len(cur_super_chunk) > 0:
            super_chunks.append(cur_super_chunk)
            
        return super_chunks

    def process_chunks(self):
        ctype = ContentType.objects.get_for_model(self.binary)
        BinaryDisassemblySuperChunk.objects.filter(content_type=ctype.id, object_id=self.binary.id).delete()

        # Disassemble the entire file, one section at a time, dividing it into disassembly chunks
        if self.binary.options.target in TARGETS_WITHOUT_CODE_SECTIONS:
            super_chunks = self.get_chunks_from_file(self.sections)
            if not super_chunks:
                # TODO: What shoud we do if there is nothing for us to disassemble? Is this file empty?
                logger.warn("Unable to obtain data from binary file")
        else:
            super_chunks = self.get_chunks_from_file(self.sections_iter(['SEC_CODE']))
            if not super_chunks:
                # No code section, but there could still be strings, etc.
                logger.warn('No code sections found to disassemble')

        # Note the boundary chunks
        if super_chunks:
            super_chunks[0].is_boundary = True
            super_chunks[len(super_chunks)-1].is_boundary = True

        #i = 0
        for super_chunk in super_chunks:
            sch = BinaryDisassemblySuperChunk(id=None,
                start=super_chunk.start,
                end=super_chunk.end,
                is_boundary=super_chunk.is_boundary,
                binary=self.binary)
            sch.save()
            for chunk in super_chunk.chunks.values():
                ch = BinaryDisassemblyChunk(id=None,
                     start=chunk.start,
                     end=chunk.end,
                     name=chunk.name,
                     superchunk=sch)
                ch.save()

            #i+=1

    def mk_hex_lines(self, superchunks):
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

        for superchunk in superchunks:
            superchunk.hex_lines = []
            for chunk in superchunk.chunks():
                alignment = self.bfd.sections[chunk.name].vma % LINE_WIDTH
                logger.info("ALIGN: %d" % (alignment))
                # Determine if the chunk is the start of a section
                if self.bfd.sections[chunk.name].vma == chunk.start:
                    rounded_start = chunk.start
                else:
                    # Align on the start of the section and chop off
                    #  the unaligned bytes
                    chunk_alignment = chunk.start % LINE_WIDTH
                    if chunk_alignment > alignment:
                        rounded_start = chunk.start + LINE_WIDTH - (chunk_alignment - alignment)
                    else:
                        rounded_start = chunk.start + alignment - chunk_alignment
                
                rounded_size = chunk.end - rounded_start
                logger.info("START: 0x%08x SIZE: 0x%08x" % (rounded_start, rounded_size))
                
                
                if rounded_size > 0:
                    raw = self.bfd.raw_data(self.bfd.sections[chunk.name], rounded_start, rounded_size)
                    raw_lines = [raw[i:i+LINE_WIDTH] for i in range(0,len(raw),LINE_WIDTH)]
                    addr = rounded_start
                    
                    for line in raw_lines:
                        if len(line)<LINE_WIDTH:
                            sec = self.bfd.sections[chunk.name]
                            if chunk.end != (sec.vma + sec.size):
                                # Pad out the short line with bytes from the next chunk
                                pad_size = LINE_WIDTH - len(line)
                                line += self.bfd.raw_data(self.bfd.sections[chunk.name], chunk.end, pad_size)                                
                        ascii = toAscii(line)
                        hex = toHex(line)
                        name = chunk.name
                        superchunk.hex_lines.append((name, addr, hex, ascii))
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
        afterChunks = BinaryDisassemblySuperChunk.objects.filter(
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
        beforeChunksReversed = BinaryDisassemblySuperChunk.objects.filter(
            content_type=ctype.id, object_id = self.binary.id, start__lt = addr ).order_by('-start')[0:numRequested]      
        
        # Chunks before the given chunk but in reverse order
        beforeChunks = list(beforeChunksReversed)
        beforeChunks.reverse()
        
        # Get the chunks to return 
        numBeforeChunks = len(beforeChunks)
        numAfterChunks = num_chunks - numBeforeChunks
        #print "BEFORE: %d, AFTER %d" % (numBeforeChunks,numAfterChunks)         
        permachunks = beforeChunks + afterChunks[0:numAfterChunks]    

        return permachunks

    def get_chunks_from_chunk(self, start, end, direction, num_chunks):

        ctype = ContentType.objects.get_for_model(self.binary)

        if direction == 1:
            # Chunks after the given chunk
            permachunks = BinaryDisassemblySuperChunk.objects.filter(
                content_type=ctype.id, object_id = self.binary.id, start__gt = start )[0:num_chunks]
        else:
            # Chunks before the given chunk
            permachunksReversed = BinaryDisassemblySuperChunk.objects.filter(
                content_type=ctype.id, object_id = self.binary.id, start__lt = start ).order_by('-start')[0:num_chunks]      
            
            # Chunks before the given chunk but in reverse order
            permachunks = list(permachunksReversed)
            permachunks.reverse()
        
        return permachunks

    def get_chunk_list(self, superchunks):
        # Build a primitive object containing the list of chunk data to pass back to the client
        chunk_list = []
        for superchunk in superchunks:
            chunk_list.append ({
                'startOffset': superchunk.start,
                'endOffset': superchunk.end,
                'isBoundary': superchunk.is_boundary,
                #'hex_lines' : hex_lines #chunk.hex_lines
            })
            
        return chunk_list

    def process_chunks_disassembly(self, superchunks):

        architecture = self.binary.options.architecture

        analyzer = analyzerFactory(architecture)

        dasm = Disassembler(self.binary)
        analyzer.analyze( dasm, superchunks )
        analyzer.convertToHtmlLine()

        for superchunk in superchunks:
            superchunk.attach_comments(self.binary)
        
    def process_chunks_hex(self, superchunks):
        logger.info("process_chunks_hex")
        dasm = Disassembler(self.binary)
        logger.info("got dasm")
        dasm.mk_hex_lines(superchunks)

examples = (
    {
        'project_name' : 'strcpy (x86)',
        'short_name' : 'strcpy_x86',
        'binary_type' : 'string',
        'data' : '55 31 D2 89 E5 8B 45 08 56 8B 75 0C 53 8D 58 FF 0F B6 0C 16 88 4C 13 01 83 C2 01 84 C9 75 F1 5B 5E 5D C3 ',
        'options' : OdaOptions(target="binary", architecture="i386"),
        'comments' : (
                (0x09, 'char* src = arg[1]'),
                (0x0d, 'char* dst = arg[0]'),
                (0x10, 'char c = src[i]'),
                (0x14, 'dst[i] = c'),
                (0x18, 'i++'),
                (0x1b, 'while (c != 0)'),
        )
    },
    {
        'project_name' : 'strcpy (arm)',
        'short_name' : 'strcpy_arm',
        'binary_type' : 'string',
        'data' : '01 20 40 E2 02 20 61 E0 01 30 D1 E4 00 00 53 E3 02 30 C1 E7 FB FF FF 1A 1E FF 2F E1',
        'options' : OdaOptions(target="binary", architecture="arm"),
    },
    {
        'project_name' : 'whoami (Linux)',
        'short_name' : 'whoami',
        'binary_type' : 'file',
        'file_name' : 'whoami',
        'options' : OdaOptions(target="elf64-x86-64", architecture="i386:x86-64"),
    },
    {
        'project_name' : 'mkdir (Linux)',
        'short_name' : 'mkdir',
        'binary_type' : 'file',
        'file_name' : 'mkdir',
        'options' : OdaOptions(target="elf64-x86-64", architecture="i386:x86-64"),
        },
    {
        'project_name' : 'cat (Linux)',
        'short_name' : 'cat',
        'binary_type' : 'file',
        'file_name' : 'cat',
        'options' : OdaOptions(target="elf64-x86-64", architecture="i386:x86-64"),
        },
    {
        'project_name' : 'chown (Linux)',
        'short_name' : 'chown',
        'binary_type' : 'file',
        'file_name' : 'chown',
        'options' : OdaOptions(target="elf64-x86-64", architecture="i386:x86-64"),        },
    {
        'project_name' : 'sha1sum (Linux)',
        'short_name' : 'sha1sum',
        'binary_type' : 'file',
        'file_name' : 'sha1sum',
        'options' : OdaOptions(target="elf64-x86-64", architecture="i386:x86-64"),
    },
    #{
    #    'project_name' : 'Sasser Worm (Windows)',
    #    'short_name' : 'sasser',
    #    'binary_type' : 'file',
    #    'file_name' : 'net-worm.win32.sasser.a',
    #    'options' : OdaOptions(target="elf32-i386", architecture="i386"),
    #    },
)

def copy_disassembly(from_id, from_version, to_id, ip_address):
    to_oda = OdaMaster.objects.get(short_name = from_id, revision = from_version)
    comments = Comment.get_for_binary(to_oda.binary)

    to_oda.id = None
    to_oda.ipAddress = ip_address

    options = to_oda.binary.options
    options.id = None
    options.save()

    binary = to_oda.binary
    binary.id = None
    binary.options = options
    binary.save()

    to_oda.binary = binary
    to_oda.short_name = to_id
    to_oda.revision = 0
    to_oda.save()

    Disassembler(to_oda.binary).process_chunks()

    for comment in comments:
        comment.id = None
        comment.object_id = binary.id
        comment.save()

