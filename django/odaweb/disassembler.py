from odaweb.utils import id_generator

__author__ = 'davis'

import re
import string
import dischunk
import time
import os
import bfd
from ofd import Ofd
from django.contrib.contenttypes.models import ContentType

from odaweb.models import (Binary, BinaryString,
                           BinaryFile, OdaMaster, OdaOptions, Comment, Label, Symbol,
                           BinaryParcel, Function)

import logging

logger = logging.getLogger(__name__)

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

class Disassembler(object):

    def __init__(self, binary):

        self.binary = binary

        self.ofd = Ofd(binary)

    @staticmethod
    def guess_bfd_arch(filename):
        ''' Returns our best guess at target (file format) and architecture '''

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

    def get_parcels_from_file(self, sections, alwaysTreatAsCode):

        parcels = []

        for sec in sections:

            if self.ofd.section_has_flags(sec,['SEC_CODE']) or alwaysTreatAsCode:
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
            parcels = self.get_parcels_from_file(self.ofd.sections, True)
            if not parcels:
                # TODO: What shoud we do if there is nothing for us to disassemble? Is this file empty?
                logger.warn("Unable to obtain data from binary file")
        else:
            parcels = self.get_parcels_from_file(self.ofd.sections_iter(['SEC_LOAD']), False)
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

            # Make a pass through the code sections to identify more symbols
            #dbParcels = BinaryParcel.objects.filter(
            #                content_type=ctype.id, object_id = self.binary.id)
            #architecture = self.binary.options.architecture
            #analyzer = analyzerFactory(architecture)
            #analyzer.analyze( self, dbParcels )
            pass



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
            s = self.ofd.get_section_from_addr(parcel.start)
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
                raw = self.ofd.bfd.raw_data(s, rounded_start, rounded_size)
                raw_lines = [raw[i:i+LINE_WIDTH] for i in range(0,len(raw),LINE_WIDTH)]
                addr = rounded_start

                for line in raw_lines:
                    if len(line)<LINE_WIDTH:
                        if parcel.end != (s.vma + s.size):
                            # Pad out the short line with bytes from the next chunk
                            pad_size = LINE_WIDTH - len(line)
                            line += self.ofd.bfd.raw_data(s, parcel.end, pad_size)
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


def copy_disassembly(from_id, from_version, owner, ip_address):

    #to_oda gets copied by setting the id to None

    to_oda = OdaMaster.objects.get(short_name = from_id, revision = from_version)
    comments = Comment.get_for_binary(to_oda.binary)
    labels = Label.get_for_binary(to_oda.binary)
    functions = Function.get_for_binary(to_oda.binary)
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

    for func in functions:
        func.id = None
        func.object_id = binary.id
        func.save()

    return to_oda

