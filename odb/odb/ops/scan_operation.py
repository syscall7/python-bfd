import logging
from odb.bfd import ofd
from odb.bfd.analyzers.instruction import DisplayUnit
from odb.ops.operation import Operation
from odb.structures.function import Function
from odb.structures.parcel import Parcel

__author__ = 'davis'

logger = logging.getLogger(__name__)



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

class ScanOperation(Operation):
    def operate(self, odb_file):
        assert (len(odb_file.items[Parcel]) > 0)

        for parcel in [p for p in odb_file.items[Parcel] if p.is_code]:
            logger.debug("parcel start=0x%08x parcel.end=0x%08x" % (parcel.start, parcel.end))

            ofd.Ofd(odb_file.get_binary()).disassemble(parcel.name, [], parcel.start, parcel.end,
                              funcFmtLine=parseFunctionsOnly,
                              funcFmtLineArgs={
                                  'self': self,
                                  })