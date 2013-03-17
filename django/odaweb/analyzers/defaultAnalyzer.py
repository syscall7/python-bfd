'''
Created on Jun 12, 2012

@author: Owner
'''

from instruction import *
import re
import branch

class InstUnit(object):
    def __init__(self, section_name, offset, rawBytes, instStr, branch, branch_label):
        self.section_name = section_name
        self.offset = offset
        self.rawBytes = rawBytes
        self.instStr = instStr
        self.branch = branch
        self.branch_label = branch_label

    def make_label_target(self, labelName):
        self.labelName = labelName

class Function(object):
    def __init__(self, offset, name, xrefs):
        self.offset = offset
        self.xrefs = xrefs
        self.name = name


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

    def analyze(self, bfd, chunks=None):
        
        self.bfd = bfd
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

        # Grab the symbols for convenience and performance reasons
        self.symbols = self.bfd.symbols() 
        
        # Add preidentified symbols to the labels and functions list
        for sym in self.symbols:
            if sym.type == 'T' or sym.type == 't':
                self.functions[sym.value] = Function(sym.value, sym.name, set())
                
        # Make a first pass at parsing for organizing the instructions
        self.chunks = chunks
        for chunk in self.chunks:
            
            # Convert the chunk to disassembly
            from cStringIO import StringIO
            file_str = StringIO()
            file_str.write( bfd.disassemble(chunk.sec_name, chunk.start, chunk.end)[0] )
            rawDisassembly = file_str.getvalue()
                
            # Parse each disassembly line in the chunk
            chunk.instructions = {}
            for line in rawDisassembly.split('\n'):
                inst = self.parseDisassemblyLine(line)
                if inst:
                    chunk.instructions[inst.offset] = inst
                        
        # set branches whose target addresses are not mapped to a valid range to invalid
        for b in self.branches:
            b.isTargetAddrValid = False
            for sec in self.bfd.sections:
                # Check if the branch falls within a valid section range
                if b.targetAddr > sec.vma and b.targetAddr < (sec.vma + sec.size):
                    b.isTargetAddrValid = True
                                    
        # Make a second pass through the instructions to create the html
        self.convertToHtmlLine()

    
    def parseDisassemblyLine(self,listing):
        
        # Perform the match
        matchObj = self.instParserRegEx.match(listing)
        
        if matchObj:
            
            inst = instruction()
             
            # Separate out the address 
            inst.offset = int(matchObj.group(1),16)
        
            # Separate out the raw bytes
            inst.rawBytes = matchObj.group(2)
            
            # Separate out the instruction and check for errors
            inst.listing = matchObj.group(3)
            matchObj = self.errorInstRegEx.match(inst.listing)
            if matchObj:
                inst.isError = True 

            # Get the Opcode
            if not inst.isError:
                matchObj = self.opcodeRegEx.match(inst.listing)
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
                                self.functions[inst.targetAddr] = Function(inst.targetAddr, 'func_%0.8x' % (inst.targetAddr), set([inst.offset]))
                            else:
                                # Add new cross reference to set
                                self.functions[inst.targetAddr].xrefs.update([inst.offset])
                                   

            return inst 
        return None        
                                
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

    def convertToHtmlLine(self):

        # weed out invalid branches
        blf = branch.BranchLineHtmlFormatter(self.branches)

        for chunk in self.chunks:
            chunk.instUnits = []
            for key in sorted(chunk.instructions.iterkeys()):
                inst = chunk.instructions[key]
    
                # Fill the rawBytes structure
                byteStr = re.sub(r'\s', '',inst.rawBytes)
    
                if len(byteStr) > self.largestInstSize:
                    self.largestInstSize = len(byteStr)
                rawBytes = "%s" % (byteStr)
    
                instStr = self.makeInstr(inst)
    
                # got to get the label first, because it is based on the previous offset
                branchLabel = blf.pushLabel()
                branchLines = blf.pushAddr(inst.offset)
                unit = InstUnit(chunk.sec_name[:8], inst.offset, rawBytes, instStr, branchLines, branchLabel)
    
                if inst.offset in self.functions:
                    unit.make_label_target(self.functions[inst.offset].name)
                    unit.function = self.functions[inst.offset]
                    chunk.lines += 2 + len(self.functions[inst.offset].xrefs)
                elif inst.offset in self.labels:
                    unit.make_label_target(self.mkLabelName(inst.offset,'loc'))
                    chunk.lines += 1
                chunk.instUnits.append(unit)


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
                    instStr += "%-7s<a href=\"#view/tab-assembly/offset/%08x\">%s</a>" % (inst.opcode, inst.targetAddr, labelName)
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

            
                
                
        