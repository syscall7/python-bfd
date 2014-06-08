import logging
import re

from oda.libs.odb.bfd import ofd
from oda.libs.odb.bfd.analyzer import analyzer_factory
from oda.libs.odb.bfd.analyzers.instruction import DisplayUnit, InstructionType
from oda.libs.odb.ops.operation import Operation
from oda.libs.odb.structures.branch import Branch
from oda.libs.odb.structures.function import Function
from oda.libs.odb.structures.parcel import Parcel


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

class ParcelOffsetScanner(object):
    def __init__(self):
        self.inst_sample_interval = 50
        self.sample_offset_count = 0
        self.last_parcel = None

    def instruction(self, parcel, addr, rawData, instr, abfd):

        #we've advanced to the next parcel, reset the counter
        if parcel != self.last_parcel:
            self.sample_offset_count = 0
            self.last_parcel = parcel

        if self.sample_offset_count == self.inst_sample_interval:
            parcel.sample_offsets.append(addr)
            self.sample_offset_count = 0
        else:
            self.sample_offset_count += 1

        # associate this vma with the parcel
        parcel.push_vma(addr)

    def commit(self, odb_file):
        pass

class BranchScanner(object):
    def __init__(self, analyzer):
        self.analyzer = analyzer

        self.opcode_regex = re.compile(analyzer.opcodeRegExStr)
        self.branches = []
        self.labels = []

    def instruction(self, parcel, addr, rawData, instr, abfd):
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

    def commit(self, odb_file):
        for b in self.branches:
            branch = odb_file.create_item('Branch', b)
            odb_file.get_structure_list(Branch).append(branch)

class FunctionScanner(object):

    def __init__(self, analyzer):

        self.analyzer = analyzer
        self.error_instruction_regex = re.compile(analyzer.errorInstRegExStr)
        self.opcode_regex = re.compile(analyzer.opcodeRegExStr)

        self.functions = {}

    def instruction(self, parcel, addr, rawData, instr, abfd):
        ''' Disassembly line parser optimized for finding functions '''

        if self.error_instruction_regex.match(instr):
            return

        # Get the Opcode
        match_obj = self.opcode_regex.match(instr)
        if match_obj:
            du = create_display_unit(self.analyzer, match_obj, addr)

            # If we need to create a function
            if du.isTargetAddrValid and du.instType == InstructionType.call:

                # If this is a new Function
                if du.targetAddr not in self.functions:

                    self.functions[du.targetAddr] = {
                        'name': 'func_%0.8x' % du.targetAddr,
                        'offset': du.targetAddr,
                        'type': 't',
                        'xrefs':  set([du.offset])
                    }
                else:
                    # Else, update a pre-existing Function, add a new cross reference
                    self.functions[du.targetAddr]['xrefs'].update([du.offset])

                # If this is a new Function
                #if du.targetAddr not in self.functions:
                #    self.functions[du.targetAddr] = Function(du.targetAddr, 'func_%0.8x' % (du.targetAddr), 't',
                #                                             set([du.offset]))

                # Else, update a pre-existing Function
                #else:
                 #   # Add new cross reference to set
                  #  self.functions[du.targetAddr].xrefs.update([du.offset])

    def commit(self, odb_file):
        for addr, f in self.functions.iteritems():
            func = odb_file.create_item('Function', f)
            odb_file.get_structure_list(Function).append(func)


class ScanOperation(Operation):

    def __init__(self):
        super(ScanOperation, self).__init__()
        self.object_id = -1

    def operate(self, odb_file):
        assert (len(odb_file.get_structure_list(Parcel)) > 0)

        self.object_id = odb_file.get_object_id()

        function_scanner = FunctionScanner(analyzer_factory(odb_file.get_arch()))
        branch_scanner = BranchScanner(analyzer_factory(odb_file.get_arch()))
        parcel_scanner = ParcelOffsetScanner()

        scanners = [
            function_scanner,
            branch_scanner,
            parcel_scanner
        ]

        lda_offset = 0
        parcels = odb_file.get_structure_list(Parcel)
        parcels.sort(key=lambda p: p.start, reverse=False)

        for parcel in parcels:

            logger.debug("parcel start=0x%08x parcel.end=0x%08x" % (parcel.start, parcel.end))

            # initialize the logical display unit address

            the_ofd = ofd.Ofd(odb_file.get_binary())
            section = the_ofd.get_section_from_addr(parcel.start)

            parcel.lda_start = lda_offset
            if parcel.is_code:

                def callback(addr, rawData, instr, abfd, self):
                    for scanner in scanners:
                        scanner.instruction(parcel, addr, rawData, instr, abfd)


                the_ofd.disassemble(section.name, [], parcel.start, parcel.end,
                                    funcFmtLine=callback,
                                    funcFmtLineArgs={
                                        'self': self,
                                    })

            # account for the new display units
            lda_offset += parcel.num_ldas()

        for scanner in scanners:
            scanner.commit(odb_file)