from odaweb.utils import id_generator

__author__ = 'davis'

import re
import string
import bfd
import dischunk
import time
import os
from django.contrib.contenttypes.models import ContentType

from odaweb.models import (Binary, BinaryString,
                           BinaryFile, OdaMaster, OdaOptions, Comment, Label, Symbol,
                           BinaryParcel)

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

class SectionInfo(object):
    def __init__(self, sections):
        self.sections = sections
        if len(sections):
            self.start_addr = sections[0].vma
            self.stop_addr = sections[-1].vma + sections[-1].size - 1
        else:
            self.start_addr = 0
            self.stop_addr = 0

    addr_range = property(lambda self: self.stop_addr - self.start_addr)

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
        strs = {}
        for s in self.get_loadable_sections().sections:
            print 'Section %s, base 0x%08x, size 0x%08x' % (s.name, s.vma, s.size)
            for m in re.finditer("([\t\x20-\x7e]{4,})", self.bfd.raw_data(s, s.vma, s.size)):
                strs[m.start()+s.vma] = m.group(1)

        for k,v in strs.items():
            print '0x%08x: %s' % (k, v)
        return strs

    def sections_iter(self, flags=[]):
        '''Iterate over all sections (in ascending address order) that have all give flags specified'''
        for sec in self.sections:
            sec_flags = [f.name for f in sec.flags]
            if set(flags).issubset(sec_flags):
                yield sec

    def section_has_flags(self, section, flags=[]):
        sec_flags = [f.name for f in section.flags]
        if set(flags).issubset(sec_flags):
            return True
        else:
            return False

    def disassemble(self, name, start=None, stop=None, numLines=None, funcFmtLine=None, funcFmtLineArgs=None):
        sec = self.bfd.sections[name]
        baseAddr = self.binary.options.base_address
        options = self.binary.options.get_extra_options()
        if baseAddr:
            baseAddr = int(baseAddr, 16)
            start += baseAddr
            stop += baseAddr
        # determine endianness
        endian = ({'BIG': bfd.ENDIAN_BIG,
                    'LITTLE': bfd.ENDIAN_LITTLE,
                    'DEFAULT': bfd.ENDIAN_DEFAULT})[self.binary.options.get_endian()]

        analyzer = analyzerFactory(self.binary.options.architecture)
        options = analyzer.processOptions(options)

        # force intel syntax as default for i386 arch
        if self.bfd.arch.startswith('i386') and len(options) == 0:
            options = ['intel-mnemonic']

        options_string = ",".join(options)

        dis = self.bfd.disassemble(sec, start, stop, numLines, None, funcFmtLine, funcFmtLineArgs, endian, options_string, baseAddr)
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

    def get_loadable_sections(self):

        def filter_sec_load(sec):
            return set(['SEC_LOAD']).issubset([f.name for f in sec.flags])

        # treat all sections as loaded for targets without code sections
        if self.bfd.target in TARGETS_WITHOUT_CODE_SECTIONS:
            code_sections = self.sections
        # else, only get the code sections
        else:
            code_sections = filter(filter_sec_load, self.sections)

        section_info = SectionInfo(code_sections)

        return section_info

    def get_section_from_addr(self, addr):
        for sec in self.sections:
            if addr >= sec.vma and addr < (sec.vma+sec.size):
                return sec

        return None

    def get_parcels_from_file(self, sections, alwaysTreatAsCode):

        parcels = []

        for sec in sections:

            if self.section_has_flags(sec,['SEC_CODE']) or alwaysTreatAsCode:
                is_code = True
            else:
                is_code = False

            parcel = dischunk.DisParcel(sec.vma, sec.size+sec.vma, is_code)
            parcels.append(parcel)

        return parcels

    #def get_all_parcels(self, sections, alwaysTreatAsCode):
    #
    #    parcels = []
    #
    #    for sec in sections:
    #        parcel = dischunk.DisParcel()
    #        if self.section_has_flags(sec,['SEC_CODE']) or alwaysTreatAsCode:
    #            parcel.is_code = True
    #        else:
    #            parcel.is_code = False
    #
    #        parcel.start = sec.vma
    #        parcel.end = sec.size+sec.vma
    #        parcels.append(parcel)
    #
    #    return parcels


    #def get_chunks_from_file(self, sections, alwaysTreatAsCode=False):
    #    super_chunks = []
    #    cur_super_chunk = dischunk.DisSuperChunk()
    #
    #    for sec in sections:
    #
    #        # Initialize loop variables
    #        sec_consumed = 0
    #        sec_offset_addr = sec.vma
    #
    #        while sec_consumed < sec.size:
    #
    #            chunk_size = min( cur_super_chunk.available_len(), sec.size-sec_consumed )
    #            treatAsCode = False
    #
    #            if self.section_has_flags(sec,['SEC_CODE']) or alwaysTreatAsCode:
    #                # Disassemble a chunk
    #                disassembly, next_addr, num_lines = self.disassemble(sec.name, sec_offset_addr, sec_offset_addr+chunk_size)
    #                treatAsCode = True
    #
    #                # when disassembling binaries, weird things can happen...this is one of them
    #                if next_addr <= sec_offset_addr:
    #                    break
    #
    #                # Update Size
    #                chunk_size = next_addr - sec_offset_addr
    #            else:
    #                # Pure Data or Undefined Section
    #                next_addr = sec_offset_addr+chunk_size
    #
    #            # Grow the super chunk
    #            cur_super_chunk.grow(sec.name, sec_offset_addr, chunk_size, treatAsCode)
    #
    #            # Check if we need to add another super chunk
    #            if cur_super_chunk.available_len() == 0 or chunk_size == 0:
    #                # Not enough room in the chunk to add to it
    #                #    Get a new chunk
    #                super_chunks.append(cur_super_chunk)
    #                cur_super_chunk = dischunk.DisSuperChunk()
    #
    #            # Update loop variables
    #            sec_consumed += chunk_size
    #            sec_offset_addr = next_addr
    #
    #    # Include the last chunk
    #    if len(cur_super_chunk) > 0:
    #        super_chunks.append(cur_super_chunk)
    #
    #    return super_chunks

    def process_parcels(self,alwaysTreatAsCode=False,initialPass=True):
        ctype = ContentType.objects.get_for_model(self.binary)
        BinaryParcel.objects.filter(content_type=ctype.id, object_id=self.binary.id).delete()

        # Disassemble the entire file, one section at a time, dividing it into disassembly chunks
        if alwaysTreatAsCode:
            parcels = self.get_parcels_from_file(self.sections, True)
            if not parcels:
                # TODO: What shoud we do if there is nothing for us to disassemble? Is this file empty?
                logger.warn("Unable to obtain data from binary file")
        else:
            parcels = self.get_parcels_from_file(self.sections_iter(['SEC_LOAD']), False)
            if not parcels:
                # No code section, but there could still be strings, etc.
                logger.warn('No code sections found to disassemble')

        for parcel in parcels:
            p = BinaryParcel(id=None,
                start = parcel.start,
                end = parcel.end,
                is_code = parcel.is_code,
                binary=self.binary
                )
            p.save()

        # Make the initial pass to load the database with info from the newly uploaded file
        if initialPass:

            # Grab the symbols from the object file
            symbols = self.symbols()
            for sym in symbols:
                s = Symbol(id=None,
                    offset = sym.value,
                    name = sym.name,
                    sym_type = sym.type,
                    binary=self.binary
                    )
                s.save()

            # Make a pass through the code sections to identify more symbols
            #dbParcels = BinaryParcel.objects.filter(
            #                content_type=ctype.id, object_id = self.binary.id)
            #architecture = self.binary.options.architecture
            #analyzer = analyzerFactory(architecture)
            #analyzer.analyze( self, dbParcels )



    #def process_chunks(self,alwaysTreatAsCode=False):
    #    ctype = ContentType.objects.get_for_model(self.binary)
    #    BinaryDisassemblySuperChunk.objects.filter(content_type=ctype.id, object_id=self.binary.id).delete()
    #
    #    # Disassemble the entire file, one section at a time, dividing it into disassembly chunks
    #    if alwaysTreatAsCode:
    #        super_chunks = self.get_chunks_from_file(self.sections, True)
    #        if not super_chunks:
    #            # TODO: What shoud we do if there is nothing for us to disassemble? Is this file empty?
    #            logger.warn("Unable to obtain data from binary file")
    #    else:
    #        super_chunks = self.get_chunks_from_file(self.sections_iter(['SEC_LOAD']), False)
    #        if not super_chunks:
    #            # No code section, but there could still be strings, etc.
    #            logger.warn('No code sections found to disassemble')
    #
    #    # Note the boundary chunks
    #    if super_chunks:
    #        super_chunks[0].is_boundary = True
    #        super_chunks[len(super_chunks)-1].is_boundary = True
    #
    #    #i = 0
    #    for super_chunk in super_chunks:
    #        sch = BinaryDisassemblySuperChunk(id=None,
    #            start=super_chunk.start,
    #            end=super_chunk.end,
    #            is_boundary=super_chunk.is_boundary,
    #            binary=self.binary)
    #        sch.save()
    #        for chunk in super_chunk.chunks.values():
    #            ch = BinaryDisassemblyChunk(id=None,
    #                 start=chunk.start,
    #                 end=chunk.end,
    #                 name=chunk.name,
    #                 superchunk=sch)
    #            ch.save()
    #            for parcel in chunk.parcels.values():
    #                p = BinaryParcel(id=None,
    #                    start = parcel.start,
    #                    end = parcel.end,
    #                    is_code = parcel.is_code,
    #                    chunk = ch
    #                    )
    #                p.save()
    #
    #        #i+=1

    def mk_hex_lines(self, parcels):
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

        for parcel in parcels:
            s = self.get_section_from_addr(parcel.start)
            alignment = s.vma % LINE_WIDTH
            logger.info("ALIGN: %d" % (alignment))
            # Determine if the chunk is the start of a section
            if s.vma == parcel.start:
                rounded_start = parcel.start
            else:
                # Align on the start of the section and chop off
                #  the unaligned bytes
                parcel_alignment = parcel.start % LINE_WIDTH
                if parcel_alignment > alignment:
                    rounded_start = parcel.start + LINE_WIDTH - (parcel_alignment - alignment)
                else:
                    rounded_start = parcel.start + alignment - parcel_alignment

            rounded_size = parcel.end - rounded_start
            logger.info("START: 0x%08x SIZE: 0x%08x" % (rounded_start, rounded_size))


            if rounded_size > 0:
                raw = self.bfd.raw_data(s, rounded_start, rounded_size)
                raw_lines = [raw[i:i+LINE_WIDTH] for i in range(0,len(raw),LINE_WIDTH)]
                addr = rounded_start

                for line in raw_lines:
                    if len(line)<LINE_WIDTH:
                        if parcel.end != (s.vma + s.size):
                            # Pad out the short line with bytes from the next chunk
                            pad_size = LINE_WIDTH - len(line)
                            line += self.bfd.raw_data(s, parcel.end, pad_size)
                    ascii = toAscii(line)
                    hex = toHex(line)
                    name = s.name
                    parcel.hex_lines.append((name, addr, hex, ascii))
                    addr += len(line)
                
    #def convert_to_data(self, addr):
    #    ctype = ContentType.objects.get_for_model(self.binary)

    #def get_all_superchunks(self):
    #    ctype = ContentType.objects.get_for_model(self.binary)
    #    superChunks = BinaryDisassemblySuperChunk.objects.filter(
    #        content_type=ctype.id, object_id = self.binary.id )
    #    return superChunks

class JsonChunkProcessor(object):
    def __init__(self, binary):
        self.binary = binary

    def get_parcel_from_addr(self, addr):

        ctype = ContentType.objects.get_for_model(self.binary)

        parcel = BinaryParcel.objects.filter(
            content_type=ctype.id, object_id = self.binary.id, start__gte = addr )[0]

        return parcel

    def get_all_parcels(self):

        ctype = ContentType.objects.get_for_model(self.binary)

        parcels = BinaryParcel.objects.filter(
            content_type=ctype.id, object_id = self.binary.id)

        return parcels


    #def convert_addr_to_data(self, addr):
    #
    #    parcel = self.get_parcel_from_addr(addr)
    #
    #    parcel_avail_size = parcel.end - addr
    #
    #
    #    # Check if the parcel is already data or code
    #    if parcel.is_code == True:
    #        # Convert the entire instruction to byte array
    #
    #    elif parcel.is_code == False:
    #        if ( parcel_avail_size )
    #    else:
    #        # Parcel is undefined.


    #def get_chunks_from_addr(self, addr, num_chunks):
    #    #analyzer = analyzerFactory( self.binary.options.architecture )
    #
    #    ctype = ContentType.objects.get_for_model(self.binary)
    #    afterChunks = BinaryDisassemblySuperChunk.objects.filter(
    #        content_type=ctype.id, object_id = self.binary.id, start__gte = addr )[0:num_chunks]
    #
    #    # The requested address is the center chunk. We need to get chunks
    #    #    before and after the center chunk (if possible)
    #
    #    # Chunks after an address are easier to retrieve. Retrieve the
    #    #    maximum number in case there is a shortage of chunks before
    #    #    the provided address. Include the chunk that contains the
    #    #    provided address
    #    #    Note: afterChunks does not include the center chunk
    #    afterChunks = BinaryDisassemblySuperChunk.objects.filter(
    #        content_type=ctype.id, object_id = self.binary.id, start__gte = addr )[0:num_chunks]
    #
    #    # Determine how many chunks before the address that we need to get
    #    numAfterChunks = len(afterChunks)
    #    if numAfterChunks >= (num_chunks//2):
    #        # Plenty of chunks, request the minimum beforeChunks
    #        numRequested = (num_chunks//2) + 1
    #    else:
    #        # Towards the back of the address space, or a very small file
    #        #    Request more chunks before the given address to make up
    #        #    the difference
    #        numRequested = num_chunks - numAfterChunks
    #
    #    # Get the chunks before the address (including the center chunk)
    #    beforeChunksReversed = BinaryDisassemblySuperChunk.objects.filter(
    #        content_type=ctype.id, object_id = self.binary.id, start__lt = addr ).order_by('-start')[0:numRequested]
    #
    #    # Chunks before the given chunk but in reverse order
    #    beforeChunks = list(beforeChunksReversed)
    #    beforeChunks.reverse()
    #
    #    # Get the chunks to return
    #    numBeforeChunks = len(beforeChunks)
    #    numAfterChunks = num_chunks - numBeforeChunks
    #    #print "BEFORE: %d, AFTER %d" % (numBeforeChunks,numAfterChunks)
    #    permachunks = beforeChunks + afterChunks[0:numAfterChunks]
    #
    #    return permachunks

    #def get_chunks_from_chunk(self, start, end, direction, num_chunks):
    #
    #    ctype = ContentType.objects.get_for_model(self.binary)
    #
    #    if direction == 1:
    #        # Chunks after the given chunk
    #        permachunks = BinaryDisassemblySuperChunk.objects.filter(
    #            content_type=ctype.id, object_id = self.binary.id, start__gt = start )[0:num_chunks]
    #    else:
    #        # Chunks before the given chunk
    #        permachunksReversed = BinaryDisassemblySuperChunk.objects.filter(
    #            content_type=ctype.id, object_id = self.binary.id, start__lt = start ).order_by('-start')[0:num_chunks]
    #
    #        # Chunks before the given chunk but in reverse order
    #        permachunks = list(permachunksReversed)
    #        permachunks.reverse()
    #
    #    return permachunks

    #def get_chunk_list(self, superchunks):
    #    # Build a primitive object containing the list of chunk data to pass back to the client
    #    chunk_list = []
    #    for superchunk in superchunks:
    #        chunk_list.append ({
    #            'startOffset': superchunk.start,
    #            'endOffset': superchunk.end,
    #            'isBoundary': superchunk.is_boundary,
    #            #'hex_lines' : hex_lines #chunk.hex_lines
    #        })
    #
    #    return chunk_list

    def process_parcels_disassembly(self, parcels, start=0):

        architecture = self.binary.options.architecture

        analyzer = analyzerFactory(architecture)

        dasm = Disassembler(self.binary)
        comments = Comment.get_for_binary(self.binary)
        analyzer.analyze( dasm, parcels, start=start )
        #analyzer.convertToHtmlLine(comments)

        #sortedUnits = sorted(analyzer.displayUnits, key=lambda key: analyzer.displayUnits[key])
        #sortedUnits = iter(sorted(analyzer.displayUnits.items()))
        return analyzer.displayUnits
        #self.attach_comments(self.binary)

        #for parcel in parcels:
        #    parcel.attach_comments(self.binary)
        #    parcel.attach_prototype(self.binary)
    #
    #def process_chunks_disassembly(self, superchunks):
    #
    #    architecture = self.binary.options.architecture
    #
    #    analyzer = analyzerFactory(architecture)
    #
    #    dasm = Disassembler(self.binary)
    #    analyzer.analyze( dasm, superchunks )
    #    analyzer.convertToHtmlLine()
    #
    #    for superchunk in superchunks:
    #        superchunk.attach_comments(self.binary)
    #        superchunk.attach_prototype(self.binary)

    def process_parcels_hex(self, parcels):
        logger.info("process_chunks_hex")
        dasm = Disassembler(self.binary)
        logger.info("got dasm")
        dasm.mk_hex_lines(parcels)

    #def process_chunks_hex(self, superchunks):
    #    logger.info("process_chunks_hex")
    #    dasm = Disassembler(self.binary)
    #    logger.info("got dasm")
    #    dasm.mk_hex_lines(superchunks)

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
        ),
        'labels': (
            (0x10, 'loop'),
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

def copy_disassembly(from_id, from_version, owner, ip_address):

    #to_oda gets copied by setting the id to None

    to_oda = OdaMaster.objects.get(short_name = from_id, revision = from_version)
    comments = Comment.get_for_binary(to_oda.binary)
    labels = Label.get_for_binary(to_oda.binary)
    parcels = BinaryParcel.get_for_binary(to_oda.binary)

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

    if owner.is_authenticated():
        to_oda.owner = owner


    to_oda.copy = OdaMaster.objects.get(short_name = from_id, revision = from_version)
    if to_oda.copy is None:
        to_oda.revision = 0
        to_oda.short_name = id_generator()
    else:
        if to_oda.copy.owner == owner:
            to_oda.revision = to_oda.next_revision()
        else:
            to_oda.revision = 0
            to_oda.short_name = id_generator()

    to_oda.save()

    #Disassembler(to_oda.binary).process_chunks()

    for comment in comments:
        comment.id = None
        comment.object_id = binary.id
        comment.save()

    #for superchunk in superchunks:
    #    chunks = superchunk.chunks()
    #    superchunk.id = None
    #    superchunk.object_id = binary.id
    #    superchunk.save()
    #
    #    for chunk in chunks:
    #        parcels = chunk.parcels()
    #        chunk.id = None
    #        chunk.object_id = binary.id
    #        chunk.superchunk = superchunk
    #        chunk.save()

    for parcel in parcels:
        parcel.id = None
        parcel.object_id = binary.id
        parcel.save()

    for label in labels:
        label.id = None
        label.object_id = binary.id
        label.save()

    return to_oda

