'''
Created on Jun 12, 2012

@author: Owner
'''

from django.utils import html

from instruction import *
import re
import branch
import bfd
import logging
import string
from oda.libs.odb.bfd.ofd import Ofd
from oda.libs.odb.structures import symbol
from oda.libs.odb.structures import branch as branch_struct
from oda.libs.odb.structures import function as function2
from oda.libs.odb.structures.c_struct import BuiltinField
from oda.libs.odb.structures import c_struct

logger = logging.getLogger(__name__)

class Function(object):
    def __init__(self, offset, name, type, xrefs):
        self.offset = offset
        self.xrefs = xrefs
        self.name = name
        self.type = type

def parseField(section_name, addr, self, displayUnits, field, prefix, byteList):

    valueStr = '0x'
    rawBytes = ''
    for i in range(field.size):
        c = byteList.pop(0)
        valueStr += "%02x" % c
        rawBytes += "%02x" % c
    du = DisplayUnit()
    insn = prefix + '.' + field.name
    du.instStr = "<insn>%s</insn>  <span class='raw'>%s</span>" % (insn, valueStr)
    du.rawBytes = rawBytes
    du.isArray = False
    du.dataSize = field.size
    du.offset = addr
    du.section_name = section_name
    displayUnits[du.offset] = du

def parseStruct(section_name, start_addr, self, displayUnits, maxLines, struct, prefix, byteList):
    addr = start_addr
    numLines = len(displayUnits)
    for field in struct.fields:
        if field.size > 0:
            if isinstance(field ,BuiltinField):
                parseField(section_name, addr, self, displayUnits, field, prefix, byteList)
            else:
                parseStruct(section_name, addr, self, displayUnits, maxLines, field.cstruct, prefix + '.' + field.name, byteList)
            addr += field.size
            numLines += 1
            if numLines == maxLines:
                break


def parseDataParcel(section_name, start_addr, end_addr, self, displayUnits, is_data, maxLines, structs=None):

    dataLen = end_addr - start_addr
    numLines = 0

    # Get the raw data from the file
    rawData = self.ofd.bfd.raw_data(self.ofd.bfd.sections[section_name], start_addr, dataLen)

    # if is_data:
    #     # TODO: Organize the data in groups of one, two, four bytes etc.,
    #     addr = start_addr
    #     for c in map(ord, rawData):
    #         du = DisplayUnit()
    #         du.offset = addr
    #         du.section_name = section_name
    #         du.rawBytes =  '%02x' % c
    #         du.isArray = False
    #         du.dataSize = 1
    #         displayUnits[du.offset] = du
    #         numLines += 1
    #
    #         addr += 1
    #
    #
    # else:
    # Undefined. Treat as single byte per line
    addr = start_addr
    byteList = map(ord, rawData)
    while len(byteList) and numLines < maxLines:
        struct_type = None
        curStruct = None
        for struct in structs:
            if addr == struct.addr:
                curStruct = struct
                struct_type = next(tmpStructType for tmpStructType in self.struct_types if tmpStructType.name == struct.struct_type)
                break

        if struct_type != None and len(byteList) >= struct_type.size and struct_type.size > 0:
            parseStruct(section_name, addr, self, displayUnits, maxLines, struct_type, curStruct.name, byteList)
            addr += struct_type.size
            numLines += len(struct_type.fields)
            if (numLines >= maxLines):
                break
        else:
            # TODO: Don't specify the css class here - it's not very classy, ha, ha
            c = byteList.pop(0)
            du = DisplayUnit()
            du.isCode = False
            du.offset = addr
            du.section_name = section_name
            du.instStr = "<insn>db</insn>  <span class='raw'>%02xh</span>" % c
            if chr(c) in string.printable:
                du.instStr += " <span class='comment'>; %s</span>" % html.escape(chr(c))
            du.rawBytes =  '%02x' % c
            du.isArray = False
            du.dataSize = 1
            addr += 1
            numLines += 1
            displayUnits[du.offset] = du


        if (numLines == maxLines):
            break

    return numLines

def parseInstruction(addr, rawData, instr, abfd, self, displayUnits, section_name):

    du = DisplayUnit()
    du.isCode = True

    # Separate out the address
    du.offset = addr

    # Separate out the raw bytes
    if abfd.bpc > 1 and (abfd.endian is bfd.ENDIAN_LITTLE or abfd.endian is bfd.ENDIAN_DEFAULT):
        du.rawBytes = ''.join(['%02x' % i for i in reversed(rawData)])
    else:
        du.rawBytes = ''.join(['%02x' % i for i in rawData])

    # Separate out the instruction and check for errors
    du.instStr = instr.replace('<', '&lt;').replace('>', '&gt;')

    matchObj = self.errorInstRegEx.match(instr)
    if matchObj:
        du.isError = True

    # Get the Opcode
    if not du.isError:
        matchObj = self.opcodeRegEx.match(instr)
        if matchObj:
            du.opcode = matchObj.group(1)
            du.instType = self.getInstructionType(du.opcode)
            du.operands = matchObj.group(2)
            self.computeTargetAddr(du)

            # Check if we need to create a label or function
            if du.isTargetAddrValid:

                # Create a new label for branch instructions
                if du.targetAddr not in self.labels and du.instType == InstructionType.branch:
                    self.labels.append(du.targetAddr)
                elif du.instType == InstructionType.call:
                    if du.targetAddr not in self.functions:
                        self.functions[du.targetAddr] = Function(du.targetAddr, 'func_%0.8x' % (du.targetAddr), 't', set([du.offset]))
                    else:
                        # Add new cross reference to set
                        self.functions[du.targetAddr].xrefs.update([du.offset])

            if du.instType == InstructionType.call or du.instType == InstructionType.branch:

                # If the branch target address is invalid
                if du.callType == callType.direct:

                    # Invalid target address
                    if not du.isTargetAddrValid:
                        du.instStr = "%-6s <errinsn>%s</errinsn>" % (du.opcode, du.operands)

                    # Valid target address
                    else:
                        # just use the opcode, we insert the target link on the client side (i.e. call some_func)
                        du.instStr = '%-7s' % du.opcode

            # Not a call/branch
            # TODO: Look for string references
            elif False:
                # for non-branch/non-call instructions, look for a reference to a string
                for m in re.finditer('0x([0-9a-fA-F]+)', du.instStr):
                    addrRef = int(m.group(1), 16)

                    # TODO: skip address 0 for now, but address this again someday
                    if 0 == addrRef:
                        continue
                    if addrRef in self.strings:
                        rawInstrStr += '  <a href="#/view/tab-assembly/offset/%08x" class="stringref">"%s"</a>' % (addrRef, self.strings[addrRef])
                instStr += rawInstrStr

            # Check for errors
            if du.isError:
                du.instStr = "<disline addr=%x><dislineerr>     %s</dislineerr></disline>" % (du.offset,du.instStr)


    du.section_name = section_name
    displayUnits[du.offset] = du

def parseFunctionsOnly(addr, rawData, instr, abfd, self, parcel):
    ''' Disassembly line parser optimized for finding functions '''

    if self.errorInstRegEx.match(instr):
        return

    # Get the Opcode
    matchObj = self.opcodeRegEx.match(instr)
    if matchObj:
        du = DisplayUnit()
        du.offset = addr
        du.opcode = matchObj.group(1)
        du.instType = self.getInstructionType(du.opcode)
        du.operands = matchObj.group(2)
        du.isCode = True

        self.computeTargetAddr(du)

        # If we need to create a function
        if du.isTargetAddrValid and du.instType == InstructionType.call:

            # If this is a new Function
            if du.targetAddr not in self.functions:
                self.functions[du.targetAddr] = Function(du.targetAddr, 'func_%0.8x' % (du.targetAddr), 't', set([du.offset]))

            # Else, update a pre-existing Function
            else:
                # Add new cross reference to set
                self.functions[du.targetAddr].xrefs.update([du.offset])


class defaultAnalyzer(object):
    '''
    classdocs
    '''

    def __init__(self):

        self.rawBytes = []
        self.offset = ""
        self.offsetStr = []
        self.listing = ""
        self.branchLineHtml = ""
        self.displayUnits = {}
        self.largestInstSize = 0
        self.opcodeTypes = {}
        self.labels = []
        self.instSampleInterval = 50

        # {funcAddrA: [crossRef0, crossRef1], funcAddrB: [crossRef0, crossRef1]}
        self.functions = {}
        self.options = []
        # raw binary bytes "xx xx xx .."
        self.rawBytesRegExStr = "((?:[0-9a-f]{2} )+)" 

        self.errorInstRegExStr = "\(bad\)"

        # don't include "<symbol_name>" as part of operands
        self.opcodeRegExStr = "^(\w+)\s+([^<]+)"

    # override this in the subclass if you need to (i.e., mips)
    def processOptions(self, options):
        return options

    def displayUnitsFromParcel(self, options, parcel, start=None, end=None, maxUnits=None):
        assert(maxUnits >= 0)
        displayUnits = {}
        s = self.ofd.get_section_from_addr(parcel.vma_start)
        if start and parcel.vma_start < start:
            dis_start = start
        else:
            dis_start = parcel.vma_start

        if end:
            dis_end = end
        else:
            dis_end = parcel.vma_end

        if parcel.is_code:
            if maxUnits:
                self.ofd.disassemble(s.name, options, dis_start, dis_end,
                                              numLines = maxUnits,
                                              funcFmtLine=parseInstruction,
                                              funcFmtLineArgs={
                                                  'self': self,
                                                  'displayUnits': displayUnits,
                                                  'section_name': s.name,
                                              })
        else:
            parseDataParcel(s.name, dis_start, dis_end, self, displayUnits, False, maxUnits, parcel.structs)

        return displayUnits

    def analyze(self, odb_file, parcels=None, start=0, maxUnits=None):

        # make sure parcels are in order
        parcels.sort(key=lambda p: p.vma_start, reverse=False)

        self.odb_file = odb_file
        self.ofd = Ofd(odb_file.get_binary())
        self.instParserRegEx = re.compile(
                    # beginning of the line plus white space
                    "^\s*" +               
                    # offset, followed by white space
                    "([0-9a-f]*)\s+" +    
                    # raw binary bytes 
                    self.rawBytesRegExStr +
                    # instruction
                    "\s+(.*)$"
                    )
        
        self.errorInstRegEx = re.compile( self.errorInstRegExStr )
        
        self.opcodeRegEx = re.compile( self.opcodeRegExStr )

        # Grab the symbols and sections for convenience and performance reasons
        self.symbols = self.odb_file.get_structure_list(symbol.Symbol)

        self.struct_types = self.odb_file.get_structure_list(c_struct.CStruct)

        # Add symbols from the database to the functions list
        for f in self.odb_file.get_structure_list(function2.Function):
            self.functions[f.offset] = f

        # Make a first pass at parsing for organizing the instructions
        logger.debug("Analyze: START FIRST PASS FOR INSTRUCTIONS")

        options = self.processOptions(self.odb_file.get_binary().options.get_extra_options())

        # Filter parcels based on the provided boundaries
        if maxUnits >= 0 or maxUnits == None:
            # Getting disassembly greater than an address
            filterFunc = lambda parcel: parcel.vma_end >= start
            parcelList = parcels

            # Forwards parsing starts at a given address until we get enough units
            disEnd = None
            disStart = start

        else:
            # Note: disassembler.py prevents this case from happening.
            # TODO: To remove

            # Getting disassembly moving backwards from an address
            #  Note: Use start+1 to include the provided address in the returned disaseembly
            filterFunc = lambda parcel: parcel.vma_start < start + 1
            parcelList = reversed(parcels)

            # Backwards parsing means the provided start address is the end of disassembly
            disEnd = start+1
            disStart = None

        # Disassemble the parcel
        for parcel in filter(filterFunc,parcelList):
            dus = self.displayUnitsFromParcel( options, parcel, disStart, disEnd, maxUnits)
            self.displayUnits = dict(self.displayUnits.items() + dus.items())

            # Breakout early if we parse enough units
            if maxUnits is not None:
                if maxUnits > 0:
                    maxUnits -= len(dus.keys())
                else:
                    maxUnits += len(dus.keys())

                if maxUnits == 0:
                    break

        logger.debug("Analyze: INSTRUCTIONS POPULATED.")

        # # verify target address is at a valid instruction boundary (someday maybe we'll handle the odd case where it's not)
        # for b in self.branches:
        #     b.isTargetAddrValid = False
        #     if b.targetAddr in self.displayUnits:
        #         b.isTargetAddrValid = True
        #         break

        # Second Pass
        logger.debug("Analyze: START SECOND INSTRUCTION PASS. UNITS COUNT: %d" % (len(self.displayUnits)))

        # break up branches into sets based on function boundary
        prevFuncAddr = -1

        # sort displayUnits
        dunits = sorted(self.displayUnits.values(), key=lambda du: du.offset)

        # For now, we will ignore branching from/to other chunks of display units
        localBranches = filter(
            lambda b: (b.srcAddr > dunits[0].offset and b.srcAddr < dunits[-1].offset) and
                      (b.targetAddr > dunits[0].offset and b.targetAddr < dunits[-1].offset),
            odb_file.get_structure_list(branch_struct.Branch))

        # Get the branch lines
        if len(self.functions) > 0 and len(dunits) > 0:
            # Ignore functions outside of the display units we retrieved
            functions = filter(lambda f: f.offset > dunits[0].offset and f.offset < dunits[-1].offset, self.functions.values())
            for function in sorted(functions, key=lambda f: f.offset):
                # get all the branches between prev func and this func
                branches = [b for b in localBranches if b.targetAddr > prevFuncAddr and b.targetAddr < function.offset]

                dus = [du for du in dunits if du.offset >= prevFuncAddr and du.offset < function.offset]

                self.addBranchLinesAndLabels(dus, branches)
                prevFuncAddr = function.offset

            # now process between the last func and the end
            branches = [b for b in localBranches if b.targetAddr >= prevFuncAddr]
            dus = [du for du in dunits if du.offset >= prevFuncAddr]
            self.addBranchLinesAndLabels(dus, branches)

        else:
            self.addBranchLinesAndLabels(dunits, localBranches)

        logger.debug("Analyze: SECOND PASS COMPLETE")

    def get_text_listing(self, odb_file, parcels):

        parcels.sort()
        MAX_SEC_NAME_WIDTH = 32

        def funcFmtCode(addr, rawData, instr, abfd, sec_name):
            ret = ''
            if abfd.syms_by_addr.has_key(addr):
                ret += '\n%s:%08x <%s>:\n' % (sec_name, addr, abfd.syms_by_addr[addr].name)
            if abfd.bpc > 1 and abfd.endian is bfd.ENDIAN_LITTLE:
                bytes = ''.join(['%02x ' % i for i in reversed(rawData)])
            else:
                bytes = ''.join(['%02x ' % i for i in rawData])

            ret += '%s:%08x %-32s %s\n' % (sec_name.rjust(MAX_SEC_NAME_WIDTH, ' '), addr, bytes, instr)
            return ret

        # TODO: refactor and use parseDataParcel
        def fmtDataParcel(p):
            ret = ''
            # Get the raw data from the file
            rawData = self.ofd.bfd.raw_data(self.ofd.bfd.sections[p.sec_name], p.vma_start, p.vma_end - p.vma_start)
            i = 0
            for b in rawData:
                ret += '%s:%08x %-32s %s %s\n' % (p.sec_name.rjust(MAX_SEC_NAME_WIDTH, ' '),
                                                  p.vma_start+i,
                                                  '%02x' % ord(b),
                                                  '0x%02x' % ord(b),
                                                  '\'%s\'' % b if b in string.printable else '')
                i += 1
            return ret

        self.ofd = Ofd(odb_file.get_binary())
        options = self.processOptions(odb_file.get_binary().options.get_extra_options())
        listing = ''
        for p in parcels:
            if p.is_code:
                (output, _, _) = self.ofd.disassemble(p.sec_name, options=options, start=p.vma_start, stop=p.vma_end, funcFmtLine=funcFmtCode, funcFmtLineArgs={ 'sec_name': p.sec_name})
            else:
                output = fmtDataParcel(p)

            listing += output

        return listing

    def addBranchLinesAndLabels(self, dunits, branches):

        blf = branch.BranchLineHtmlFormatter(branches)
        for du in dunits:
            du.branch_label = blf.pushLabel()
            du.branch = blf.pushAddr(du.offset)

            if du.isTargetAddrValid:
                offset = du.targetAddr
                if du.targetAddr in self.functions:
                    du.targetRef = RefUnit(offset)
                elif du.targetAddr in self.labels:
                    du.targetRef = RefUnit(offset)

            if du.offset in self.functions:
                #unit.function = self.functions[inst.offset]
                du.isFunction = True
                du.branchRef = RefUnit(du.offset)
                for xref in sorted(self.functions[du.offset].xrefs):
                    du.crossRef.append(RefUnit( xref))

            elif du.offset in self.labels:
                du.branchRef = RefUnit(du.offset)
                du.isBranch = True

    def getInstructionType(self,opcode):
        if opcode in self.opcodeTypes:
            return self.opcodeTypes[opcode]
        return InstructionType.normal

    # override in the sub-class
    def computeTargetAddr(self,inst):
        pass

    # override in the sub-class
    def getMaxInstructionLenBytes(self):
        pass

    def makeData(self, inst):
        dataStr = ""

        # TODO: Account for endian

        if inst.dataSize == 1:
            dataStr = "0x"+inst.rawBytes
        else:
            dataStr = ""

        return dataStr

    # TODO: Find a better place for this function
    def find(self, odb_file, pattern):

        ofd = Ofd(odb_file.get_binary())

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
                try:
                    return binascii.unhexlify(pattern.replace(' ', ''))
                except TypeError:
                    # Assume this is a string to search for
                    # TODO: Throw the error and color a text box in the UI
                    return pattern
        # find the pattern in the current haystack
        def needleInHaystack(needle, haystack, baseAddr, sectionGroup, results):

            for m in re.finditer("(%s)" % re.escape(needle), haystack):

                foundAddr = baseAddr+m.start()

                for s in sectionGroup:
                    if foundAddr >= s.vma and foundAddr < s.vma+s.size:
                        results[foundAddr] = s.name
                        break;

        pattern = parsePattern(pattern)

        # we only search within loadable sections
        for s in ofd.get_loadable_sections().sections:

            # if this section is contiguous with the previous section
            if s.vma == lastAddr:
                haystack += ofd.bfd.raw_data(s, s.vma, s.size)
                sectionGroup.append(s)
                lastAddr = s.vma+s.size

            # else, this section is not contiguous
            else:
                if lastAddr != -1:
                    needleInHaystack(pattern, haystack, baseAddr, sectionGroup, results)

                # start fresh
                haystack = ofd.bfd.raw_data(s, s.vma, s.size)
                baseAddr = s.vma
                lastAddr = s.vma+s.size
                sectionGroup = [s]

        # search the last contiguous group
        if lastAddr != -1:
            needleInHaystack(pattern, haystack, baseAddr, sectionGroup, results)

        return results


