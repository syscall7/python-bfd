import logging
from odb.bfd import ofd
from odb.bfd.analyzers.instruction import DisplayUnit, InstructionType
from odb.ops.operation import Operation
from odb.structures.function import Function
from odb.structures.parcel import Parcel

__author__ = 'davis'

logger = logging.getLogger(__name__)


class FunctionScanner(object):
    def instruction(self, addr, rawData, instr, abfd):
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
            if du.isTargetAddrValid and du.instType == InstructionType.call:

                # If this is a new Function
                if du.targetAddr not in self.functions:
                    self.functions[du.targetAddr] = Function(du.targetAddr, 'func_%0.8x' % (du.targetAddr), 't',
                                                             set([du.offset]))

                # Else, update a pre-existing Function
                else:
                    # Add new cross reference to set
                    self.functions[du.targetAddr].xrefs.update([du.offset])


class ScanOperation(Operation):
    def operate(self, odb_file):
        assert (len(odb_file.items[Parcel]) > 0)

        for parcel in [p for p in odb_file.items[Parcel] if p.is_code]:
            logger.debug("parcel start=0x%08x parcel.end=0x%08x" % (parcel.start, parcel.end))

            the_ofd = ofd.Ofd(odb_file.get_binary())
            section = the_ofd.get_section_from_addr(parcel.start)

            scanners = [FunctionScanner()]

            def callback(addr, rawData, instr, abfd, self):
                for scanner in scanners:
                    scanner.instruction(addr, rawData, instr, abfd)


            the_ofd.disassemble(section.name, [], parcel.start, parcel.end,
                                funcFmtLine=callback,
                                funcFmtLineArgs={
                                    'self': self,
                                })