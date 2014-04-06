import logging
import re

from odb.bfd import ofd
from odb.bfd.analyzer import analyzer_factory
from odb.bfd.analyzers import branch
from odb.bfd.analyzers.instruction import DisplayUnit, InstructionType
from odb.ops.operation import Operation
from odb.structures.branch import Branch
from odb.structures.function import Function
from odb.structures.parcel import Parcel


__author__ = 'davis'

logger = logging.getLogger(__name__)



def create_display_unit(analyzer, match_obj,addr):
    du = DisplayUnit()
    du.offset = addr
    du.opcode = match_obj.group(1)
    du.instType = analyzer.getInstructionType(du.opcode)
    du.operands = match_obj.group(2)

    analyzer.computeTargetAddr(du)

    return du


class BranchScanner(object):
    def __init__(self, analyzer):
        self.analyzer = analyzer

        self.opcode_regex = re.compile(analyzer.opcodeRegExStr)
        self.branches = []
        self.labels = []

    def instruction(self, addr, rawData, instr, abfd):
        match_obj = self.opcode_regex.match(instr)
        if match_obj:

            du = create_display_unit(self.analyzer, match_obj, addr)
            if du.instType == InstructionType.branch:
                    self.branches.append({
                        'instr': du
                    })
                # Check if we need to create a label or function

            if du.isTargetAddrValid:

                # Create a new label for branch instructions
                if du.targetAddr not in self.labels and du.instType == InstructionType.branch:
                    self.labels.append(du.targetAddr)

class FunctionScanner(object):

    def __init__(self, analyzer):

        self.analyzer = analyzer
        self.error_instruction_regex = re.compile(analyzer.errorInstRegExStr)
        self.opcode_regex = re.compile(analyzer.opcodeRegExStr)

        self.functions = []

    def instruction(self, addr, rawData, instr, abfd):
        ''' Disassembly line parser optimized for finding functions '''

        if self.error_instruction_regex.match(instr):
            return

        # Get the Opcode
        match_obj = self.opcode_regex.match(instr)
        if match_obj:
            du = create_display_unit(self.analyzer, match_obj, addr)

            # If we need to create a function
            if du.isTargetAddrValid and du.instType == InstructionType.call:

                self.functions.append({
                    'name': 'func_%0.8x' % du.targetAddr,
                    'offset': du.targetAddr,
                    'type': 't',
                    'xrefs':  set([du.offset])
                })

                # If this is a new Function
                #if du.targetAddr not in self.functions:
                #    self.functions[du.targetAddr] = Function(du.targetAddr, 'func_%0.8x' % (du.targetAddr), 't',
                #                                             set([du.offset]))

                # Else, update a pre-existing Function
                #else:
                 #   # Add new cross reference to set
                  #  self.functions[du.targetAddr].xrefs.update([du.offset])


class ScanOperation(Operation):

    def operate(self, odb_file):
        assert (len(odb_file.items[Parcel]) > 0)

        function_scanner = FunctionScanner(analyzer_factory('i386'))
        branch_scanner = BranchScanner(analyzer_factory('i386'))

        scanners = [
            function_scanner,
            branch_scanner
        ]

        for parcel in [p for p in odb_file.items[Parcel] if p.is_code]:
            logger.debug("parcel start=0x%08x parcel.end=0x%08x" % (parcel.start, parcel.end))

            the_ofd = ofd.Ofd(odb_file.get_binary())
            section = the_ofd.get_section_from_addr(parcel.start)

            def callback(addr, rawData, instr, abfd, self):
                for scanner in scanners:
                    scanner.instruction(addr, rawData, instr, abfd)


            the_ofd.disassemble(section.name, [], parcel.start, parcel.end,
                                funcFmtLine=callback,
                                funcFmtLineArgs={
                                    'self': self,
                                })

        for f in function_scanner.functions:
            func = odb_file.create_item('Function', f)
            odb_file.items[Function].append(func)

        for b in branch_scanner.branches:
            branch = odb_file.create_item('Branch', b)
            odb_file.items[Branch].append(branch)