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

    def get_parcels(self):

        parcels = []

        for sec in self.ofd.get_loadable_sections().sections:

            is_code = self.ofd.is_code_section(sec)
            parcel = dischunk.DisParcel(sec.vma, sec.size+sec.vma, is_code)
            parcels.append(parcel)

        return parcels

    def symbols(self, start=None, end=None):
        ctype = ContentType.objects.get_for_model(self.binary)
        if start == None and end == None:
            symbols = Symbol.objects.filter(content_type=ctype.id, object_id=self.binary.id)
        elif start != None and end != None:
            symbols = Symbol.objects.filter(content_type=ctype.id, object_id=self.binary.id, offset__lte = start, offset__gt = end)

        for sym in symbols:
            sym.xrefs=set(sym.get_xrefs())

        return symbols

    def analyze(self, start, lines):

        ctype = ContentType.objects.get_for_model(self.binary)

        architecture = self.binary.options.architecture
        analyzer = analyzerFactory(architecture)

        if lines >= 0:
            parcels = BinaryParcel.objects.filter(content_type=ctype.id, object_id= self.binary.id, end__gte = start)[:]
        else:
            parcels = BinaryParcel.objects.filter(content_type=ctype.id, object_id= self.binary.id, start__lte = start)[:]

        analyzer.analyze( self, parcels, start=start, maxUnits=lines)
        sorted_du = analyzer.displayUnits.values()
        sorted_du.sort(key=lambda x: x.offset, reverse=False)
        return sorted_du

    def analyze_first_time(self):
        ctype = ContentType.objects.get_for_model(self.binary)
        parcels = BinaryParcel.objects.filter(content_type=ctype.id, object_id=self.binary.id)

        # if one parcel already exists, then we've already completed first-time analysis
        if parcels.exists():
            logger.debug('Attempted first-time analysis again!')
            parcels.delete()
            #return

        # Disassemble the entire file, one section at a time, dividing it into disassembly parcels
        parcels = self.get_parcels()
        if not parcels:
            # TODO: What shoud we do if there is nothing for us to disassemble? Is this file empty?
            logger.warn('No code sections found to disassemble')

        architecture = self.binary.options.architecture
        analyzer = analyzerFactory(architecture)
        analyzer.analyze_first_time(self, parcels)

        # Save parcels to database
        for parcel in parcels:
            p = BinaryParcel(id=None,
                start = parcel.start,
                end = parcel.end,
                is_code = parcel.is_code,
                binary=self.binary
                )
            p.set_offsetSamples(parcel.sampleOffsets)
            p.save()

        # Save symbols to database
        for symbol in analyzer.functions.values():
            s = Symbol(id=None,
                    binary=self.binary,
                    offset = symbol.offset,
                    name = symbol.name,
                    type=symbol.type)

            s.set_xrefs(symbol.xrefs)
            s.save()

    def get_text_listing(self):

        def funcFmtLine(addr, rawData, instr, abfd, sec_name):
            ret = ''
            if abfd.syms_by_addr.has_key(addr):
                ret += '\n%s:0%08x <%s>:\n' % (sec_name, addr, abfd.syms_by_addr[addr].name)
            if abfd.bpc > 1 and abfd.endian is bfd.ENDIAN_LITTLE:
                bytes = ''.join(['%02x ' % i for i in reversed(rawData)])
            else:
                bytes = ''.join(['%02x ' % i for i in rawData])

            ret += '%s:%08x %-32s %s\n' % (sec_name, addr, bytes, instr)
            return ret

        text = ''
        for sec in self.ofd.get_code_sections().sections:
            (output, _, _) = self.ofd.disassemble(sec.name, funcFmtLine=funcFmtLine, funcFmtLineArgs={ 'sec_name': sec.name})
            text += output

        return text

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
                
    def process_parcels_hex(self, parcels):
        logger.info("process_chunks_hex")
        dasm = Disassembler(self.binary)
        logger.info("got dasm")
        dasm.mk_hex_lines(parcels)


    def strings(self):
        strs = {}
        for s in self.ofd.get_loadable_sections().sections:
            print 'Section %s, base 0x%08x, size 0x%08x' % (s.name, s.vma, s.size)
            for m in re.finditer("([\t\x20-\x7e]{4,})", self.ofd.bfd.raw_data(s, s.vma, s.size)):
                strs[m.start()+s.vma] = m.group(1)
        return strs

    def find(self, bytes):

        # NOTE: This function is obnoxiously complex because we want to find sequences of bytes that span contiguous
        #       sections

        # dictionary of results with key=address value=section_name
        results = {}

        # current contiguous chunk of bytes to search within
        haystack = ''

        # last address of the chunk of bytes in haystack
        lastAddr = -1

        # first address of the chunk of bytes in haystack
        baseAddr = -1

        # sections making up haystack
        sectionGroup = []

        # make sense of the user's search pattern
        def parsePattern(pattern):
            import binascii
            if pattern.startswith('"') and pattern.endswith('"'):
                return pattern[1:-1]
            else:
                return binascii.unhexlify(pattern)

        # find the pattern in the current haystack
        def needleInHaystack(needle, haystack, baseAddr, sectionGroup, results):

            for m in re.finditer("(%s)" % re.escape(needle), haystack):

                foundAddr = baseAddr+m.start()

                for s in sectionGroup:
                    if foundAddr > s.vma and foundAddr < s.vma+s.size:
                        results[foundAddr] = s.name
                        break;

        pattern = parsePattern(bytes)

        # we only search within loadable sections
        for s in self.ofd.get_loadable_sections().sections:

            # if this section is contiguous with the previous section
            if s.vma == lastAddr:
                haystack += self.ofd.bfd.raw_data(s, s.vma, s.size)
                sectionGroup.append(s)
                lastAddr = s.vma+s.size

            # else, this section is not contiguous
            else:
                if lastAddr != -1:
                    needleInHaystack(pattern, haystack, baseAddr, sectionGroup, results)

                # start fresh
                haystack = self.ofd.bfd.raw_data(s, s.vma, s.size)
                baseAddr = s.vma
                lastAddr = s.vma+s.size
                sectionGroup = [s]

        # search the last contiguous group
        if lastAddr != -1:
            needleInHaystack(pattern, haystack, baseAddr, sectionGroup, results)

        return results

def copy_disassembly(from_id, from_version, owner, ip_address):

    #to_oda gets copied by setting the id to None

    to_oda = OdaMaster.objects.get(short_name = from_id, revision = from_version)
    comments = Comment.get_for_binary(to_oda.binary)
    labels = Label.get_for_binary(to_oda.binary)
    functions = Function.get_for_binary(to_oda.binary)
    parcels = BinaryParcel.get_for_binary(to_oda.binary)
    symbols = Symbol.get_for_binary(to_oda.binary)

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

    for comment in comments:
        comment.id = None
        comment.object_id = binary.id
        comment.save()

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

    for sym in symbols:
        sym.id = None
        sym.object_id = binary.id
        sym.save()

    return to_oda

