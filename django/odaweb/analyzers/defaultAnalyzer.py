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

class DisplayUnit(object):
    def __init__(self, section_name, offset, rawBytes, displayStr, branch, branch_label):
        self.section_name = section_name
        self.offset = offset
        self.rawBytes = rawBytes
        self.instStr = displayStr
        self.branch = branch
        self.branch_label = branch_label

    def make_label_target(self, labelName):
        self.labelName = labelName

class Function(object):
    def __init__(self, offset, name, type, xrefs):
        self.offset = offset
        self.xrefs = xrefs
        self.name = name
        self.type = type

def parseDataLine(chunk_name, start_addr, end_addr, self, superchunk, is_data ):

    dataLen = end_addr - start_addr

    # Get the raw data from the file
    rawData = self.disassembler.bfd.raw_data(self.disassembler.bfd.sections[chunk_name], start_addr, dataLen)

    if is_data:
        # TODO: Organize the data in groups of one, two, four bytes etc.,
        addr = start_addr
        for c in map(ord, rawData):
            inst = instruction()
            inst.isCode = False
            inst.offset = addr
            inst.name = chunk_name
            inst.rawBytes =  '%02x' % c
            inst.isArray = False
            inst.dataSize = 1
            superchunk.instructions[inst.offset] = inst

            addr += 1


    else:
        # Undefined. Treat as single byte per line
        addr = start_addr
        for c in map(ord, rawData):
            inst = instruction()
            inst.isCode = False
            inst.offset = addr
            inst.name = chunk_name
            inst.rawBytes =  '%02x' % c
            inst.isArray = False
            inst.dataSize = 1
            superchunk.instructions[inst.offset] = inst

            addr += 1






def parseDisassemblyLine(addr, rawData, instr, abfd, self, superchunk, chunk_name):

    inst = instruction()

    # Separate out the address
    inst.offset = addr

    # Separate out the raw bytes
    if abfd.bpc > 1 and (abfd.endian is bfd.ENDIAN_LITTLE or abfd.endian is bfd.ENDIAN_DEFAULT):
        inst.rawBytes = ''.join(['%02x ' % i for i in reversed(rawData)])
    else:
        inst.rawBytes = ''.join(['%02x ' % i for i in rawData])

    # Separate out the instruction and check for errors
    inst.listing = instr
    matchObj = self.errorInstRegEx.match(instr)
    if matchObj:
        inst.isError = True

    # Get the Opcode
    if not inst.isError:
        matchObj = self.opcodeRegEx.match(instr)
        if matchObj:
            inst.opcode = matchObj.group(1)
            inst.instType = self.getInstructionType(inst.opcode)
            inst.operands = matchObj.group(2)
            self.computeTargetAddr(inst)

            # save all branches
            if inst.instType == instructionType.branch:
                self.branches.append(branch.Branch(inst))

            # Check if we need to create a label or function
            if inst.isTargetAddrValid:

                # Create a new label for branch instructions
                if inst.targetAddr not in self.labels and inst.instType == instructionType.branch:
                    self.labels.append(inst.targetAddr)
                elif inst.instType == instructionType.call:
                    if inst.targetAddr not in self.functions:
                        self.functions[inst.targetAddr] = Function(inst.targetAddr, 'func_%0.8x' % (inst.targetAddr), 't', set([inst.offset]))
                    else:
                        # Add new cross reference to set
                        self.functions[inst.targetAddr].xrefs.update([inst.offset])

        inst.name = chunk_name
        superchunk.instructions[inst.offset] = inst


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
        self.instructions = {}
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

    def analyze(self, disassembler, superchunks=None):

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
        self.superchunks = superchunks
        for superchunk in self.superchunks:
            superchunk.instructions = {}
            for chunk in superchunk.chunks():
                for parcel in chunk.parcels():
                    logger.debug("PARCEL START: 0x%08x" % (parcel.start))

                    # Convert the parcel to disassembly
                    # TODO: Fix sec name
                    if parcel.is_code:
                        self.disassembler.disassemble(chunk.name, parcel.start, parcel.end,
                                                      funcFmtLine=parseDisassemblyLine,
                                                      funcFmtLineArgs={
                                                          'self': self,
                                                          'superchunk': superchunk,
                                                          'chunk_name': chunk.name,
                                                      })
                    elif parcel.is_code == None:
                        # Defined Data
                        parseDataLine(chunk.name, parcel.start, parcel.end, self, superchunk, False)
                    elif parcel.is_code == False:
                        # Undefined
                        parseDataLine(chunk.name, parcel.start, parcel.end, self, superchunk, True)

        # Now we've got the superchunk fields populated

        # verify target address is at a valid instruction boundary (someday maybe we'll handle the odd case where it's not)
        for b in self.branches:
            b.isTargetAddrValid = False
            for superchunk in self.superchunks:
                if b.targetAddr in superchunk.instructions:
                    b.isTargetAddrValid = True
                    break

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
    def convertToHtmlLine(self):

        # weed out invalid branches
        blf = branch.BranchLineHtmlFormatter(self.branches)

        for superchunk in self.superchunks:
            superchunk.instUnits = []
            for key in sorted(superchunk.instructions.iterkeys()):
                inst = superchunk.instructions[key]

                # Fill the rawBytes structure
                byteStr = re.sub(r'\s', '',inst.rawBytes)

                if len(byteStr) > self.largestInstSize:
                    self.largestInstSize = len(byteStr)
                rawBytes = "%s" % (byteStr)

                if inst.isCode:
                    displayStr = self.makeInstr(inst)
                else:
                    displayStr = self.makeData(inst)

                # got to get the label first, because it is based on the previous offset
                branchLabel = blf.pushLabel()
                branchLines = blf.pushAddr(inst.offset)
                unit = DisplayUnit(inst.name[:8], inst.offset, rawBytes, displayStr, branchLines, branchLabel)

                if inst.offset in self.functions:
                    unit.make_label_target(self.functions[inst.offset].name)
                    unit.function = self.functions[inst.offset]
                    #chunk.lines += 2 + len(self.functions[inst.offset].xrefs)
                elif inst.offset in self.labels:
                    unit.make_label_target(self.mkLabelName(inst.offset,'loc'))
                    #chunk.lines += 1
                superchunk.instUnits.append(unit)

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
            instStr += rawInstrStr

        # Check for errors
        if inst.isError:
            instStr = "<disline addr=%x><dislineerr>     %s</dislineerr></disline>" % (inst.offset,instStr)
        else:
            instStr = " %s" % (instStr)

        return instStr

            
                
                
        