'''
Created on November 7, 2012

@author: Owner
'''
import re

from odaweb.analyzers.defaultAnalyzer import defaultAnalyzer
from odaweb.analyzers.instruction import instructionType, callType


class mips(defaultAnalyzer):
    '''
    classdocs
    '''

    def __init__(self):
        defaultAnalyzer.__init__(self)

        self.options = [
            ('ABI', 'Naming style used for gpr and fpr registers', 'CHOICE', ('DEFAULT', 'numeric', '32', 'n32', '64humb'), ''),
            ('ARCH', 'Naming style used for cp0 and hwr registers', 'CHOICE',
                ('DEFAULT', 'numeric', 'r3000', 'r3900', 'r4000', 'r4010', 'vr4100', 
                 'vr4111', 'vr4120', 'r4300', 'r4400', 'r4600', 'r4650', 
                 'r5000', 'vr5400', 'vr5500', 'r6000', 'rm7000', 'rm9000', 
                 'r8000', 'r10000', 'r12000', 'r14000', 'r16000', 'mips5', 
                 'mips32', 'mips32r2', 'mips64', 'mips64r2', 'sb1', 
                 'loongson2e', 'loongson2f', 'loongson3a', 'octeon', 
                 'octeon+', 'octeon2', 'xlr', 'xlp'), ''),
        ]
        
        self.opcodeTypes = {   
                               "b" : instructionType.branch,
                               "bal" : instructionType.branch,                                
                               "beq" : instructionType.branch,
                               "beqz" : instructionType.branch,
                               "bgez" : instructionType.branch,
                               "bgezal" : instructionType.branch,
                               "bgtz" : instructionType.branch,
                               "blez" : instructionType.branch,
                               "bltz" : instructionType.branch,
                               "bltzal" : instructionType.branch,
                               "bne" : instructionType.branch,
                               "bnez" : instructionType.branch,
                               "j" : instructionType.branch,
                               "jal" : instructionType.call,
                               "jalr" : instructionType.call,
                               "jr" : instructionType.call,                     
                              }
        
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

          