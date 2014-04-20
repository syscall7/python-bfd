'''
Created on November 7, 2012

@author: Owner
'''
import re

from oda.apps.odaweb.analyzers.defaultAnalyzer import defaultAnalyzer
from oda.apps.odaweb.analyzers.instruction import instructionType, callType


class arm(defaultAnalyzer):
    '''
    classdocs
    '''

    def __init__(self):
        defaultAnalyzer.__init__(self)

        self.options = [
            ('Force Thumb Mode', 'Assume all insns are Thumb insns', 'CHOICE', ('DEFAULT','force-thumb', 'no-force-thumb'), False),
            ('Register Names', 'Select register names specified by ATPCS, APCS, ARM ISA, gcc, or raw', 'CHOICE', 
                ('DEFAULT','reg-names-special-atpcs', 'reg-names-atpcs', 'reg-names-apcs', 'reg-names-std', 'reg-names-gcc', 'reg-names-raw'), 'reg-names-gcc'),
        ]

        self.opcodeRegExStr = "^([\w\.]+)\s+([^<]+)"

        self.opcodeTypes = {   
                               "b" : instructionType.branch, 
                               "beq" : instructionType.branch,
                               "bne" : instructionType.branch,
                               "bcs" : instructionType.branch,
                               "bcc" : instructionType.branch,
                               "bmi" : instructionType.branch,
                               "bpl" : instructionType.branch,
                               "bvs" : instructionType.branch,
                               "bvc" : instructionType.branch,
                               "bhi" : instructionType.branch,
                               "bls" : instructionType.branch,
                               "bge" : instructionType.branch,
                               "blt" : instructionType.branch,
                               "bgt" : instructionType.branch,
                               "ble" : instructionType.branch,
                               "bal" : instructionType.branch,

                               "bl" : instructionType.call,
                               "bleq" : instructionType.call,
                               "blne" : instructionType.call,
                               "blcs" : instructionType.call,
                               "blcc" : instructionType.call,
                               "blmi" : instructionType.call,
                               "blpl" : instructionType.call,
                               "blvs" : instructionType.call,
                               "blvc" : instructionType.call,
                               "blhi" : instructionType.call,
                               "blls" : instructionType.call,
                               "blge" : instructionType.call,
                               "bllt" : instructionType.call,
                               "blgt" : instructionType.call,
                               "blle" : instructionType.call,
                               "blal" : instructionType.call,
                               
                               "bx" : instructionType.call,
                               "bxeq" : instructionType.call,
                               "bxne" : instructionType.call,
                               "bxcs" : instructionType.call,
                               "bxcc" : instructionType.call,
                               "bxmi" : instructionType.call,
                               "bxpl" : instructionType.call,
                               "bxvs" : instructionType.call,
                               "bxvc" : instructionType.call,
                               "bxhi" : instructionType.call,
                               "bxls" : instructionType.call,
                               "bxge" : instructionType.call,
                               "bxlt" : instructionType.call,
                               "bxgt" : instructionType.call,
                               "bxle" : instructionType.call,
                               "bxal" : instructionType.call,

                               "b.n" : instructionType.branch, 
                               "beq.n" : instructionType.branch,
                               "bne.n" : instructionType.branch,
                               "bcs.n" : instructionType.branch,
                               "bcc.n" : instructionType.branch,
                               "bmi.n" : instructionType.branch,
                               "bpl.n" : instructionType.branch,
                               "bvs.n" : instructionType.branch,
                               "bvc.n" : instructionType.branch,
                               "bhi.n" : instructionType.branch,
                               "bls.n" : instructionType.branch,
                               "bge.n" : instructionType.branch,
                               "blt.n" : instructionType.branch,
                               "bgt.n" : instructionType.branch,
                               "ble.n" : instructionType.branch,
                               "bal.n" : instructionType.branch,

                               "bl.n" : instructionType.call,
                               "bleq.n" : instructionType.call,
                               "blne.n" : instructionType.call,
                               "blcs.n" : instructionType.call,
                               "blcc.n" : instructionType.call,
                               "blmi.n" : instructionType.call,
                               "blpl.n" : instructionType.call,
                               "blvs.n" : instructionType.call,
                               "blvc.n" : instructionType.call,
                               "blhi.n" : instructionType.call,
                               "blls.n" : instructionType.call,
                               "blge.n" : instructionType.call,
                               "bllt.n" : instructionType.call,
                               "blgt.n" : instructionType.call,
                               "blle.n" : instructionType.call,
                               "blal.n" : instructionType.call,
                               
                               "bx.n" : instructionType.call,
                               "bxeq.n" : instructionType.call,
                               "bxne.n" : instructionType.call,
                               "bxcs.n" : instructionType.call,
                               "bxcc.n" : instructionType.call,
                               "bxmi.n" : instructionType.call,
                               "bxpl.n" : instructionType.call,
                               "bxvs.n" : instructionType.call,
                               "bxvc.n" : instructionType.call,
                               "bxhi.n" : instructionType.call,
                               "bxls.n" : instructionType.call,
                               "bxge.n" : instructionType.call,
                               "bxlt.n" : instructionType.call,
                               "bxgt.n" : instructionType.call,
                               "bxle.n" : instructionType.call,
                               "bxal.n" : instructionType.call,


                               "b.w" : instructionType.branch, 
                               "beq.w" : instructionType.branch,
                               "bne.w" : instructionType.branch,
                               "bcs.w" : instructionType.branch,
                               "bcc.w" : instructionType.branch,
                               "bmi.w" : instructionType.branch,
                               "bpl.w" : instructionType.branch,
                               "bvs.w" : instructionType.branch,
                               "bvc.w" : instructionType.branch,
                               "bhi.w" : instructionType.branch,
                               "bls.w" : instructionType.branch,
                               "bge.w" : instructionType.branch,
                               "blt.w" : instructionType.branch,
                               "bgt.w" : instructionType.branch,
                               "ble.w" : instructionType.branch,
                               "bal.w" : instructionType.branch,

                               "bl.w" : instructionType.call,
                               "bleq.w" : instructionType.call,
                               "blne.w" : instructionType.call,
                               "blcs.w" : instructionType.call,
                               "blcc.w" : instructionType.call,
                               "blmi.w" : instructionType.call,
                               "blpl.w" : instructionType.call,
                               "blvs.w" : instructionType.call,
                               "blvc.w" : instructionType.call,
                               "blhi.w" : instructionType.call,
                               "blls.w" : instructionType.call,
                               "blge.w" : instructionType.call,
                               "bllt.w" : instructionType.call,
                               "blgt.w" : instructionType.call,
                               "blle.w" : instructionType.call,
                               "blal.w" : instructionType.call,
                               
                               "bx.w" : instructionType.call,
                               "bxeq.w" : instructionType.call,
                               "bxne.w" : instructionType.call,
                               "bxcs.w" : instructionType.call,
                               "bxcc.w" : instructionType.call,
                               "bxmi.w" : instructionType.call,
                               "bxpl.w" : instructionType.call,
                               "bxvs.w" : instructionType.call,
                               "bxvc.w" : instructionType.call,
                               "bxhi.w" : instructionType.call,
                               "bxls.w" : instructionType.call,
                               "bxge.w" : instructionType.call,
                               "bxlt.w" : instructionType.call,
                               "bxgt.w" : instructionType.call,
                               "bxle.w" : instructionType.call,
                               "bxal.w" : instructionType.call,
                                                           
                              }

    def computeTargetAddr(self,inst):       
        
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
