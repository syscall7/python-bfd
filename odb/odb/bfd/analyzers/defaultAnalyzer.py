'''
Created on Jun 12, 2012

@author: Owner
'''

from instruction import *
import re
import branch
import bfd
import logging
import odaweb.models
import string

logger = logging.getLogger(__name__)

class Function(object):
    def __init__(self, offset, name, type, xrefs):
        self.offset = offset
        self.xrefs = xrefs
        self.name = name
        self.type = type

def parseDataLine(section_name, start_addr, end_addr, self, displayUnits, is_data, maxLines):

    dataLen = end_addr - start_addr
    numLines = 0

    # Get the raw data from the file
    rawData = self.disassembler.ofd.bfd.raw_data(self.disassembler.ofd.bfd.sections[section_name], start_addr, dataLen)

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

            # TODO: Don't specify the css class here - it's not very classy, ha, ha
            du.instStr = "<span class='string'>%s</span>" % chr(c) if chr(c) in string.printable else ' '

            displayUnits[du.offset] = du

            addr += 1
            numLines += 1
            if (numLines == maxLines):
                break

    return numLines

def parseEverything(addr, rawData, instr, abfd, self, displayUnits, section_name):

    du = DisplayUnit()

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

            if du.instType == instructionType.call or du.instType == instructionType.branch:

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

def parseFunctionsOnly(addr, rawData, instr, abfd, self):
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

        self.computeTargetAddr(du)

        # If we need to create a function
        if du.isTargetAddrValid and du.instType == instructionType.call:

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

    def analyze_first_time(self, disassembler, parcels):
        ''' Here we do the minimum initial analysis for a brand new file, and nothing more '''

        self.errorInstRegEx = re.compile( self.errorInstRegExStr )
        self.opcodeRegEx = re.compile( self.opcodeRegExStr )

        # create Functions for symbols of type 't' and 'T'
        self.functions = {}
        for sym in disassembler.ofd.symbols():
            if sym.type == 'T' or sym.type == 't':
                self.functions[sym.value] = Function(sym.value, sym.name, sym.type, set())

        # create Functions for new functions we identify
        start = 0
        for parcel in parcels:
            logger.debug("PARCEL START: 0x%08x RQ START: 0x%08x" % (parcel.start,start))

            if parcel.end >= start:

                if start < parcel.end and start >= parcel.start:
                    dis_start = start
                else:
                    dis_start = parcel.start

                dis_end = parcel.end

                # Convert the parcel to disassembly
                if parcel.is_code:
                    s = disassembler.ofd.get_section_from_addr(dis_start)

                    logger.debug("Requesting disassembly from BFD...")
                    disassembler.ofd.disassemble(s.name, [], dis_start, dis_end,
                                                  funcFmtLine=parseFunctionsOnly,
                                                  funcFmtLineArgs={
                                                      'self': self,
                                                      })


    def analyze(self, disassembler, parcels=None, start=0, maxLines=None):

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

        # Add symbols from the database to the functions list
        for sym in self.symbols:
            if sym.type == 'T' or sym.type == 't':
                self.functions[sym.offset] = Function(sym.offset, sym.name, sym.type, sym.xrefs)

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
                s = self.disassembler.ofd.get_section_from_addr(parcel.start)
                if parcel.is_code:
                    logger.debug("Requesting disassembly from BFD...")
                    options = self.processOptions(self.disassembler.binary.options.get_extra_options())
                    (_, _, lines) = self.disassembler.ofd.disassemble(s.name, options, dis_start, dis_end,
                                                  numLines = maxLines,
                                                  funcFmtLine=parseEverything,
                                                  funcFmtLineArgs={
                                                      'self': self,
                                                      'displayUnits': self.displayUnits,
                                                      'section_name': s.name,
                                                  })

                # data section
                else:
                    lines = parseDataLine(s.name, dis_start, dis_end, self, self.displayUnits, False, maxLines)

                    #elif parcel.is_code == None:
                    #    # Defined Data
                    #    parseDataLine(s.name, parcel.start, parcel.end, self, self.displayUnits, False)
                    #elif parcel.is_code == False:
                    #    # Undefined
                    #    parseDataLine(s.name, parcel.start, parcel.end, self, self.displayUnits, True)

                if maxLines is not None:
                    maxLines -= lines
                    if maxLines <= 0:
                        break;

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
        prevFuncAddr = -1

        # sort displayUnits
        dunits = sorted(self.displayUnits.values(), key=lambda du: du.offset)

        if len(self.functions) > 0:
            for function in sorted(self.functions.values(), key=lambda f: f.offset):

                # get all the branches between prev func and this func
                branches = [b for b in self.branches if b.targetAddr > prevFuncAddr and b.targetAddr < function.offset]

                dus = [du for du in dunits if du.offset >= prevFuncAddr and du.offset < function.offset]

                self.addBranchLinesAndLabels(dus, branches)
                prevFuncAddr = function.offset

            # now process betwen the last func and the end
            branches = [b for b in self.branches if b.targetAddr >= prevFuncAddr]
            dus = [du for du in dunits if du.offset >= prevFuncAddr]
            self.addBranchLinesAndLabels(dus, branches)

        else:
            self.addBranchLinesAndLabels(dunits, self.branches)

        logger.debug("Analyze: SECOND PASS COMPLETE")

        logger.debug("Analyze: THIRD PASS FOR DATA")

        # TODO: Add data display back in, but make it respect maxLines
        for parcel in []: #parcels:
            logger.debug("PARCEL START: 0x%08x" % (parcel.start))
            s = self.disassembler.ofd.get_section_from_addr(parcel.start)
            if start < parcel.end and start > parcel.start:
                dis_start = start
            else:
                dis_start = parcel.start

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
                offset = du.targetAddr
                if du.targetAddr in self.functions:
                    du.targetRef = RefUnit(offset)
                elif du.targetAddr in self.labels:
                    du.targetRef = RefUnit(offset)

            if du.offset in self.functions:
                #unit.function = self.functions[inst.offset]
                du.isFunction = True
                du.branchRef = RefUnit(du.offset)
                for xref in self.functions[du.offset].xrefs:
                    du.crossRef.append(RefUnit( xref))

            elif du.offset in self.labels:
                du.branchRef = RefUnit(du.offset)
                du.isBranch = True

    def getInstructionType(self,opcode):
        if opcode in self.opcodeTypes:
            return self.opcodeTypes[opcode]
        return instructionType.normal

    def computeTargetAddr(self,inst):
        pass

    def makeData(self, inst):
        dataStr = ""

        # TODO: Account for endian

        if inst.dataSize == 1:
            dataStr = "0x"+inst.rawBytes
        else:
            dataStr = ""

        return dataStr

