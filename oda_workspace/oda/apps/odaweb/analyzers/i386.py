'''
Created on Jun 12, 2012

@author: Owner
'''
import re

from oda.apps.odaweb.analyzers.defaultAnalyzer import defaultAnalyzer
from oda.apps.odaweb.analyzers.instruction import instructionType, callType


class i386(defaultAnalyzer):
    '''
    classdocs
    '''

    def __init__(self):
        defaultAnalyzer.__init__(self)
        
        self.errorInstRegExStr = "\(bad\)"
        self.branchTargetRegEx = re.compile("\w+\s+(0x[0-9a-f]+)")
        self.opcodeTypes = { "jne" : instructionType.branch, 
                             "jo" : instructionType.branch, 
                             "js" : instructionType.branch,
                               "jns" : instructionType.branch,
                               "je" : instructionType.branch,
                               "jz" : instructionType.branch,
                               "jnz": instructionType.branch,
                               "jb": instructionType.branch,
                               "jnae": instructionType.branch,
                               "jc": instructionType.branch,
                               "jnb": instructionType.branch,
                               "jae": instructionType.branch,
                               "jnc": instructionType.branch,
                               "jbe": instructionType.branch,
                               "jna": instructionType.branch,
                               "ja": instructionType.branch,
                               "jnbe": instructionType.branch,
                               "jl": instructionType.branch,
                               "jnge": instructionType.branch,
                               "jge": instructionType.branch,
                               "jnl": instructionType.branch,
                               "jle": instructionType.branch,
                               "jng": instructionType.branch,
                               "jg": instructionType.branch,
                               "jnle": instructionType.branch,
                               "jp": instructionType.branch,
                               "jpe": instructionType.branch,
                               "jnp": instructionType.branch,
                               "jpo": instructionType.branch,
                               "jcxz": instructionType.branch,
                               "jecxz": instructionType.branch,
                               "jmp": instructionType.branch,
                               "jmpq": instructionType.branch,
                               "call" : instructionType.call,
                               "callq" : instructionType.call
                              }
        self.options = [
            ('Syntax Style', 'Switch between AT&T and Intel syntax', 'CHOICE', ('DEFAULT', 'intel-mnemonic', 'att-mnemonic')),
            ('Suffix', 'Always display instruction suffix in AT&T syntax', 'BOOL', ('DEFAULT','suffix', '')),
            ('Mode', 'Disassemble in 16bit mode, 32bit mode, or 64bit mode', 'CHOICE', ('DEFAULT','i8086', 'i386', 'x86-64')),
            ('Address Size', 'Assume 16bit, 32bit, or 64bit address size', 'CHOICE', ('DEFAULT','addr16', 'addr32', 'addr64')),
            ('Data Size', 'Assume 16bit or 32bit data size', 'CHOICE', ('DEFAULT','data16', 'data32')),
        ]
        
    def computeTargetAddr(self,inst):       
        #print repr( inst.opcode + " " + str(inst.instType) + " " + inst.operands)
        # Simple targets
        if (( inst.instType == instructionType.call or \
              inst.instType == instructionType.branch) and \
              len(inst.operands)>0 ):
            inst.isTargetAddrValid = False
            try: 
                # Watch out for pure address operands prefixed by '*'
                if inst.operands[0] == '*': 
                    inst.targetAddr = int(inst.operands[1:],16)
                else:
                    inst.targetAddr = int(inst.operands,16)
                inst.callType = callType.direct
                inst.isTargetAddrValid = True
            except: 
                inst.callType = callType.indirect

          