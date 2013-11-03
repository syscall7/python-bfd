'''
Created on Jun 12, 2012

@author: Owner
'''

from instruction import *
import re
import branch
import bfd
import logging
from odaweb.models import Label

logger = logging.getLogger(__name__)
#
#class RefUnit(object):
#    def __init__(self, name, offset):
#        self.name = name
#        self.offset = offset
#
#
#class DisplayUnit(object):
#    def __init__(self, section_name, offset, rawBytes, displayStr, branch, branch_label):
#        self.section_name = section_name
#        self.offset = offset
#        self.rawBytes = rawBytes
#        self.instStr = displayStr
#        self.branch = branch
#        self.branch_label = branch_label
#        self.isFunction= False
#        self.isBranch= False
#        self.branchRef = None
#        self.stringRef = None
#        self.crossRef = None
#        self.opcode = ''
#        self.operand = ''
#
#    def make_label_target(self, labelName):
#        self.labelName = labelName

class Function(object):
    def __init__(self, offset, name, type, xrefs):
        self.offset = offset
        self.xrefs = xrefs
        self.name = name
        self.type = type

def parseDataLine(section_name, start_addr, end_addr, self, displayUnits, is_data ):

    dataLen = end_addr - start_addr

    # Get the raw data from the file
    rawData = self.disassembler.bfd.raw_data(self.disassembler.bfd.sections[section_name], start_addr, dataLen)

    if is_data:
        # TODO: Organize the data in groups of one, two, four bytes etc.,
        addr = start_addr
        for c in map(ord, rawData):
            du = DisplayUnit()
            du.isCode = False
            du.offset = addr
            du.section_name = section_name
            du.rawBytes =  '%02x' % c
            du.isArray = False
            du.dataSize = 1
            displayUnits[du.offset] = du

            addr += 1


    else:
        # Undefined. Treat as single byte per line
        addr = start_addr
        for c in map(ord, rawData):
            du = DisplayUnit()
            du.isCode = False
            du.offset = addr
            du.section_name = section_name
            du.rawBytes =  '%02x' % c
            du.isArray = False
            du.dataSize = 1
            displayUnits[du.offset] = du

            addr += 1


def parseDisassemblyLine(addr, rawData, instr, abfd, self, displayUnits, section_name):

    du = DisplayUnit()

    # Separate out the address
    du.offset = addr

    # Separate out the raw bytes
    if abfd.bpc > 1 and (abfd.endian is bfd.ENDIAN_LITTLE or abfd.endian is bfd.ENDIAN_DEFAULT):
        du.rawBytes = ''.join(['%02x' % i for i in reversed(rawData)])
    else:
        du.rawBytes = ''.join(['%02x' % i for i in rawData])

    # Separate out the instruction and check for errors
    du.listing = instr.replace("<", "&lt;")
    du.listing = du.listing.replace(">", "&gt;")
    du.instStr = du.listing

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

            # save all branches
            if du.instType == instructionType.branch:
                self.branches.append(branch.Branch(du))

            # Check if we need to create a label or function
            if du.isTargetAddrValid:

                # Create a new label for branch instructions
                if du.targetAddr not in self.labels and du.instType == instructionType.branch:
                    self.labels.append(du.targetAddr)
                elif du.instType == instructionType.call:
                    if du.targetAddr not in self.functions:
                        self.functions[du.targetAddr] = Function(du.targetAddr, 'func_%0.8x' % (du.targetAddr), 't', set([du.offset]))
                    else:
                        # Add new cross reference to set
                        self.functions[du.targetAddr].xrefs.update([du.offset])

        du.section_name = section_name
        displayUnits[du.offset] = du


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
        self.branches = []

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

    def analyze(self, disassembler, parcels=None, start=0, onlySymbols=False):

        self.disassembler = disassembler
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
        self.symbols = self.disassembler.symbols()

        # Add preidentified symbols to the labels and functions list
        for sym in self.symbols:
            if sym.type == 'T' or sym.type == 't':
                self.functions[sym.value] = Function(sym.value, sym.name, sym.type, set())

        # Add in user-defined names from the db
        # TODO: This needs quite a bit of work
        labels = Label.get_for_binary(self.disassembler.binary)
        for label in labels:
            if label.offset in self.functions:
                self.functions[label.offset].name = label.label
            else:
                self.functions[label.offset] = Function(label.offset, label.label, 't', set())

        # Make a first pass at parsing for organizing the instructions
        logger.debug("Analyze: START FIRST PASS FOR INSTRUCTIONS")

        #self.parcels = parcels
        for parcel in parcels:
            logger.debug("PARCEL START: 0x%08x RQ START: 0x%08x" % (parcel.start,start))

            if parcel.end >= start:

                if start < parcel.end and start >= parcel.start:
                    dis_start = start
                else:
                    dis_start = parcel.start

                #if end < parcel.end:
                #    dis_end = end
                #else:
                dis_end = parcel.end

                # Convert the parcel to disassembly
                # TODO: Fix sec name
                if parcel.is_code:
                    s = self.disassembler.get_section_from_addr(parcel.start)
                    self.disassembler.disassemble(s.name, dis_start, dis_end,
                                                  funcFmtLine=parseDisassemblyLine,
                                                  funcFmtLineArgs={
                                                      'self': self,
                                                      'displayUnits': self.displayUnits,
                                                      'section_name': s.name,
                                                  })
                    #elif parcel.is_code == None:
                    #    # Defined Data
                    #    parseDataLine(s.name, parcel.start, parcel.end, self, self.displayUnits, False)
                    #elif parcel.is_code == False:
                    #    # Undefined
                    #    parseDataLine(s.name, parcel.start, parcel.end, self, self.displayUnits, True)

        # Don't need to do multiple passes just for the symbols
        if not onlySymbols:
            # Now we've got the superchunk fields populated
            logger.debug("Analyze: INSTRUCTIONS POPULATED. BRANCH COUNT: %d" % (len(self.branches)))

            # verify target address is at a valid instruction boundary (someday maybe we'll handle the odd case where it's not)
            for b in self.branches:
                b.isTargetAddrValid = False
                if b.targetAddr in self.displayUnits:
                    b.isTargetAddrValid = True
                    break

            # Second Pass
            logger.debug("Analyze: START SECOND INSTRUCTION PASS. UNITS COUNT: %d" % (len(self.displayUnits)))

            # break up branches into sets based on function boundary
            prevFuncAddr = 0

            # sort displayUnits
            dunits = sorted(self.displayUnits.values(), key=lambda du: du.offset)

            if len(self.functions) > 0:
                for function in sorted(self.functions.values(), key=lambda f: f.offset):

                    # get all the branches between prev func and this func
                    branches = [b for b in self.branches if b.targetAddr > prevFuncAddr and b.targetAddr < function.offset]

                    dus = [du for du in dunits if du.offset >= prevFuncAddr and du.offset < function.offset]

                    self.addBranchLinesAndLabels(dus, branches)
                    prevFuncAddr = function.offset
            else:
                self.addBranchLinesAndLabels(dunits, self.branches)

            logger.debug("Analyze: SECOND PASS COMPLETE")

            logger.debug("Analyze: THIRD PASS FOR DATA")

            for parcel in parcels:
                logger.debug("PARCEL START: 0x%08x" % (parcel.start))
                s = self.disassembler.get_section_from_addr(parcel.start)
                if start < parcel.end and start > parcel.start:
                    dis_start = start
                else:
                    dis_start = parcel.start

                #if end < parcel.end:
                #    dis_end = end
                #else:
                dis_end = parcel.end

                if parcel.is_code == None:
                    # Defined Data
                    parseDataLine(s.name, dis_start, dis_end, self, self.displayUnits, False)
                elif parcel.is_code == False:
                    # Undefined
                    parseDataLine(s.name, dis_start, dis_end, self, self.displayUnits, True)

            logger.debug("Analyze: THIRD PASS COMPLETE")

    def addBranchLinesAndLabels(self, dunits, branches):

        blf = branch.BranchLineHtmlFormatter(branches)
        for du in dunits:
            du.branch_label = blf.pushLabel()
            du.branch = blf.pushAddr(du.offset)

            if du.isTargetAddrValid:
                if du.targetAddr in self.functions:
                    offset = self.functions[du.targetAddr].offset
                    du.targetRef = RefUnit(self.functions[offset].name,offset)
                elif du.targetAddr in self.labels:
                    offset = self.labels[du.targetAddr].offset
                    du.targetRef = RefUnit(self.mkLabelName(offset,'loc'),offset)

            if du.offset in self.functions:
                du.make_label_target(self.functions[du.offset].name)
                #unit.function = self.functions[inst.offset]
                du.isFunction = True
                du.branchRef = RefUnit(self.functions[du.offset].name,du.offset)
                for xref in self.functions[du.offset].xrefs:
                    du.crossRef.append(RefUnit('', xref))

            elif du.offset in self.labels:
                #unit.make_label_target(self.mkLabelName(inst.offset,'loc'))
                du.branchRef = RefUnit(self.mkLabelName(du.offset,'loc'),du.offset)
                du.make_label_target('loc_0%08x' % du.offset)
                du.isBranch = True

    def getInstructionType(self,opcode):
        if opcode in self.opcodeTypes:
            return self.opcodeTypes[opcode]
        return instructionType.normal

    def computeTargetAddr(self,inst):
        pass

    def mkLabelName(self, addr, prefix):
        # Include pre-identified symbols
        if addr in self.symbols and (self.symbols[addr].type == 'T' or self.symbols[addr].type == 't'):
            return self.symbols[addr].name
        else:
            return '%s_%0.8x' % (prefix,addr)

    # Make a second pass through the instructions to create the html
    #def convertToHtmlLine(self,comments):
    #
    #    # weed out invalid branches
    #    blf = branch.BranchLineHtmlFormatter(self.branches)
    #
    #    # get all the strings (we don't need to do this unless we are creating html)
    #    self.strings = self.disassembler.strings()
    #
    #    print "INSTRUCTIONS:",len(self.displayUnits)
    #
    #    for key in sorted(self.instructions.iterkeys()):
    #        inst = self.instructions[key]
    #
    #        # Fill the rawBytes structure
    #        byteStr = re.sub(r'\s', '',inst.rawBytes)
    #
    #        if len(byteStr) > self.largestInstSize:
    #            self.largestInstSize = len(byteStr)
    #        rawBytes = "%s" % (byteStr)
    #
    #        if inst.isCode:
    #            displayStr = self.makeInstr(inst)
    #        else:
    #            displayStr = self.makeData(inst)
    #
    #        # got to get the label first, because it is based on the previous offset
    #        branchLabel = blf.pushLabel()
    #        branchLines = blf.pushAddr(inst.offset)
    #        unit = DisplayUnit(inst.name[:8], inst.offset, rawBytes, displayStr, branchLines, branchLabel)
    #
    #        if inst.offset in self.functions:
    #            unit.make_label_target(self.functions[inst.offset].name)
    #            #unit.function = self.functions[inst.offset]
    #            unit.isFunction = True
    #            unit.branchRef = RefUnit(self.functions[inst.offset].name,inst.offset)
    #
    #            #chunk.lines += 2 + len(self.functions[inst.offset].xrefs)
    #        elif inst.offset in self.labels:
    #            #unit.make_label_target(self.mkLabelName(inst.offset,'loc'))
    #            unit.branchRef = RefUnit(self.mkLabelName(inst.offset,'loc'),inst.offset)
    #            unit.isBranch = True
    #
    #
    #        self.display_units.append(unit)
    #
    #
    #    print "DISPLAY UNITS:",len(self.display_units)

    def makeInstrBranch(self, inst, labelName):
        return "%-7s<a href=\"#view/tab-assembly/offset/%08x\">%s</a>" % (inst.opcode, inst.targetAddr, labelName)

    def makeData(self, inst):
        dataStr = ""

        # TODO: Account for endian

        if inst.dataSize == 1:
            dataStr = "0x"+inst.rawBytes
        else:
            dataStr = ""

        return dataStr


    def makeInstr(self, inst):
        instStr = ""
        rawInstrStr = inst.listing
        rawInstrStr = rawInstrStr.replace("<", "&lt;");
        rawInstrStr = rawInstrStr.replace(">", "&gt;");

        if inst.instType == instructionType.call or\
           inst.instType == instructionType.branch:
            # If the branch target address is invalid
            #     TODO: Need to account for branches beyond the scope of the limited
            #        instructions considered in this chunk
            if inst.callType == callType.direct:
                if not inst.isTargetAddrValid:
                    # Bad instruction
                    instStr += "%-6s <errinsn>%s</errinsn>" % (inst.opcode, inst.operands)
                    #if inst.targetAddr in labels.containsKey(curInstr.targetAddr))
                    #    labels.remove(curInstr.targetAddr);
                else:
                    if inst.targetAddr in self.functions:
                        labelName = self.functions[inst.targetAddr].name
                    else:
                        labelName = self.mkLabelName(inst.targetAddr,'loc')
                    instStr += self.makeInstrBranch(inst, labelName)
            else:
                instStr += rawInstrStr
        else:
            # for non-branch/non-call instructions, look for a reference to a string
            for m in re.finditer('0x([0-9a-fA-F]+)', rawInstrStr):
                addrRef = int(m.group(1), 16)

                # TODO: skip address 0 for now, but address this again someday
                if 0 == addrRef:
                    continue
                if addrRef in self.strings:
                    rawInstrStr += '  <a href="#/view/tab-assembly/offset/%08x" class="stringref">"%s"</a>' % (addrRef, self.strings[addrRef])
            instStr += rawInstrStr

        # Check for errors
        if inst.isError:
            instStr = "<disline addr=%x><dislineerr>     %s</dislineerr></disline>" % (inst.offset,instStr)
        else:
            instStr = " %s" % (instStr)

        return instStr

            
                
                
        