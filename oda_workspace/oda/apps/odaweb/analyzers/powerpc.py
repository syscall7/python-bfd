'''
Created on November 7, 2012

@author: Owner
'''
import re

from oda.apps.odaweb.analyzers.defaultAnalyzer import defaultAnalyzer
from oda.apps.odaweb.analyzers.instruction import instructionType, callType


class powerpc(defaultAnalyzer):
    '''
    classdocs
    '''

    def __init__(self):
        defaultAnalyzer.__init__(self)

        self.options = [
            ('Mode', 'Processor mode', 'CHOICE', ('DEFAULT', '32', '64'), ''),
            ('CPU', 'CPU variant', 'CHOICE',
                ('DEFAULT', '403', '405', '440', '464', '476', '601', '603', '604',
                 '620', '7400', '7410', '7450', '7455', '750cl', 'a2', 
                 'altivec', 'any', 'booke', 'booke32', 'cell', 'com', 'e300',
                 'e500','e500mc','e500mc64', 'e5500', 'e6500', 'e500x2', 
                 'efs', 'power4', 'power5', 'power6', 'power7', 'ppc', 'ppc32', 
                 'ppc64', 'ppc64bridge', 'ppcps', 'pwr', 'pwr2', 'pwr4', 
                 'pwr5', 'pwr5x', 'pwr6', 'pwr7', 'pwrx', 'spe', 'titan', 
                 'vle', 'vsx'), ''),
        ]

        self.opcodeTypes = {   
                               "b" : instructionType.branch,
                               "ba" : instructionType.branch,                                
                               "bc" : instructionType.branch,
                               "bca" : instructionType.branch,
                               "bcl" : instructionType.call,
                               "bcla" : instructionType.call,
                               "bclr" : instructionType.call,
                               "bclrl" : instructionType.call,
                               "bcctr" : instructionType.branch,
                               "bcctrl" : instructionType.call,
                               "bl" : instructionType.call,
                               "bla" : instructionType.call,
                               
                               "blt" : instructionType.branch,
                               "ble" : instructionType.branch,
                               "beq" : instructionType.branch,
                               "bge" : instructionType.branch,
                               "bgt" : instructionType.branch,
                               "bnl" : instructionType.branch,
                               "bne" : instructionType.branch,
                               "bng" : instructionType.branch,
                               "bso" : instructionType.branch,
                               "bns" : instructionType.branch,
                               "bun" : instructionType.branch,
                               "bnu" : instructionType.branch,
                               
                               "bltlr" : instructionType.branch,
                               "blelr" : instructionType.branch,
                               "beqlr" : instructionType.branch,
                               "bgelr" : instructionType.branch,
                               "bgtlr" : instructionType.branch,
                               "bnllr" : instructionType.branch,
                               "bnelr" : instructionType.branch,
                               "bnglr" : instructionType.branch,
                               "bsolr" : instructionType.branch,
                               "bnslr" : instructionType.branch,
                               "bunlr" : instructionType.branch,
                               "bnulr" : instructionType.branch,
                               
                               "bltctr" : instructionType.branch,
                               "blectr" : instructionType.branch,
                               "beqctr" : instructionType.branch,
                               "bgectr" : instructionType.branch,
                               "bgtctr" : instructionType.branch,
                               "bnlctr" : instructionType.branch,
                               "bnectr" : instructionType.branch,
                               "bngctr" : instructionType.branch,
                               "bsoctr" : instructionType.branch,
                               "bnsctr" : instructionType.branch,
                               "bunctr" : instructionType.branch,
                               "bnuctr" : instructionType.branch,

                               "bltl" : instructionType.call,
                               "blel" : instructionType.call,
                               "beql" : instructionType.call,
                               "bgel" : instructionType.call,
                               "bgtl" : instructionType.call,
                               "bnll" : instructionType.call,
                               "bnel" : instructionType.call,
                               "bngl" : instructionType.call,
                               "bsol" : instructionType.call,
                               "bnsl" : instructionType.call,
                               "bunl" : instructionType.call,
                               "bnul" : instructionType.call,

                               "bltla" : instructionType.call,
                               "blela" : instructionType.call,
                               "beqla" : instructionType.call,
                               "bgela" : instructionType.call,
                               "bgtla" : instructionType.call,
                               "bnlla" : instructionType.call,
                               "bnela" : instructionType.call,
                               "bngla" : instructionType.call,
                               "bsola" : instructionType.call,
                               "bnsla" : instructionType.call,
                               "bunla" : instructionType.call,
                               "bnula" : instructionType.call,

                               "bltlrl" : instructionType.call,
                               "blelrl" : instructionType.call,
                               "beqlrl" : instructionType.call,
                               "bgelrl" : instructionType.call,
                               "bgtlrl" : instructionType.call,
                               "bnllrl" : instructionType.call,
                               "bnelrl" : instructionType.call,
                               "bnglrl" : instructionType.call,
                               "bsolrl" : instructionType.call,
                               "bnslrl" : instructionType.call,
                               "bunlrl" : instructionType.call,
                               "bnulrl" : instructionType.call,

                               "bltctrl" : instructionType.call,
                               "blectrl" : instructionType.call,
                               "beqctrl" : instructionType.call,
                               "bgectrl" : instructionType.call,
                               "bgtctrl" : instructionType.call,
                               "bnlctrl" : instructionType.call,
                               "bnectrl" : instructionType.call,
                               "bngctrl" : instructionType.call,
                               "bsoctrl" : instructionType.call,
                               "bnsctrl" : instructionType.call,
                               "bunctrl" : instructionType.call,
                               "bnuctrl" : instructionType.call,
                               
                              }
        self.opcodeRegExStr = "^([-\w\+]+)\s+([^<]+)"

    def getInstructionType(self,opcode):
        if opcode[-1] == '-' or opcode[-1] == '+':
            opcode = opcode[:-1]
        if opcode in self.opcodeTypes:
            return self.opcodeTypes[opcode]
        return instructionType.normal

    def makeInstrBranch(self, inst, labelName):
        operands = inst.operands.split(',')
        operands[-1] = "<a href=\"#view/tab-assembly/offset/%08x\">%s</a>" % (inst.targetAddr,labelName)
        operands_str = ",".join(operands)
        return "%-8s%s" % (inst.opcode, operands_str)

    def computeTargetAddr(self,inst):       
        
        # Simple targets
        if (( inst.instType == instructionType.call or \
              inst.instType == instructionType.branch) and \
              len(inst.operands)>0 ):
            inst.isTargetAddrValid = False
            operands = inst.operands.split(',')
            try: 
                # The last operand is the immediate
                inst.targetAddr = int(operands[-1],16)
                inst.callType = callType.direct
                inst.isTargetAddrValid = True
            except: 
                inst.callType = callType.indirect

          