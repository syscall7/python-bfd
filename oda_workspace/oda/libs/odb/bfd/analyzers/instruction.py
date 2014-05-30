'''
Created on Jul 7, 2012

@author: Owner
'''

class InstructionType:
    normal = 0
    branch = 1
    call = 2
    undefined = 3
    data = 4

class callType:
    direct = 0
    indirect = 1    

class RefUnit(object):
    def __init__(self, offset):
        self.offset = offset


class DisplayUnit(object):
    '''
    classdocs
    '''

    def __init__(self):
        self.section_name = ""
        self.offset = 0
        self.rawBytes = ""
        self.instStr = ""
        self.branch = ""
        self.branch_label = ""
        self.isFunction= False
        self.isBranch= False
        self.branchRef = None
        self.stringRef = None
        self.targetRef = None
        self.crossRef = []
        self.opcode = ''
        self.operands = ''
        self.isError = False
        self.isTargetAddrValid = False
        self.instType = InstructionType.undefined
        self.callType = None
        self.targetAddr = 0
        self.labelName = 'abc'
