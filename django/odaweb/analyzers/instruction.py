'''
Created on Jul 7, 2012

@author: Owner
'''

class instructionType:
    normal = 0
    branch = 1
    call = 2
    undefined = 3
    
class callType:
    direct = 0
    indirect = 1    

class instruction(object):
    '''
    classdocs
    '''

    def __init__(self):
        self.offset = 0
        self.listing = ""
        self.rawBytes = ""
        self.isError = False
        self.isTargetAddrValid = False
        self.targetAddr = 0
        self.opcode = ""
        self.operands = ""
        self.instType = instructionType.undefined
        self.callType = None
