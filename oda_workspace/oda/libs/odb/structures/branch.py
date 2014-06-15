from oda.libs.odb.structures.oda_object import OdaObject

__author__ = 'davis'

class Branch(OdaObject):

    def __init__(self, object_id, srcAddr, targetAddr, instr):
        super(Branch, self).__init__(object_id)
        self.srcAddr = srcAddr
        self.targetAddr = targetAddr
        self.branchDown = self.srcAddr <= self.targetAddr
        self.startAddr = self.srcAddr if self.branchDown else self.targetAddr
        self.stopAddr = self.targetAddr if self.branchDown else self.srcAddr
        self.span = self.stopAddr - self.startAddr
        self.tag = None
        self.instr = instr

    def getTargetAddrValid(self):
        return self.instr.isTargetAddrValid

    def setTargetAddrValid(self, value):
        self.instr.isTargetAddrValid = value

    isTargetAddrValid = property(getTargetAddrValid, setTargetAddrValid)

    def overlaps(self, b):
        ret = False

        if (self.stopAddr > b.startAddr) and (self.startAddr < b.stopAddr):
            ret = True

        return ret

    def isSibling(self, b):
        return self.targetAddr == b.targetAddr

    def spans(self, addr):
        return (addr >= self.startAddr) and (addr <= self.stopAddr)

    def isSource(self, addr):
        return (addr == self.srcAddr)

    def isTarget(self, addr):
        return (addr == self.targetAddr)

    def setTag(self, o):
        self.tag = o

    def getTag(self):
        return self.tag
