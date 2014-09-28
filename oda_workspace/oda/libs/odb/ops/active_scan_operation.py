import logging

from oda.libs.odb.bfd import ofd
from oda.libs.odb.bfd.analyzer import analyzer_factory
from oda.libs.odb.ops.operation import Operation
from oda.libs.odb.structures.parcel import Parcel, ParcelList
from oda.libs.odb.structures.symbol import Symbol
from oda.libs.odb.ops.scanners import FunctionScanner, BranchScanner, ParcelOffsetScanner, BadCodeScanner, HaltScanException
from oda.libs.odb.ops.split_parcel_operation import SplitParcelOperation

logger = logging.getLogger(__name__)

class ActiveScanOperation(Operation):

    def __init__(self, vma):
        super(ActiveScanOperation, self).__init__()
        self.object_id = -1
        self.vma = vma

    def _is_valid_instruction(self, the_ofd, analyzer, vma, end):
        """ Verify whether the given address points to a valid instruction or not """

        bad_code_scanner = BadCodeScanner(analyzer)
        section = the_ofd.get_section_from_addr(vma)

        the_ofd.disassemble(section.name, [], vma, end,
                            numLines=1,
                            funcFmtLine=bad_code_scanner.scan_line,
                            funcFmtLineArgs={'parcel': None})

        return bad_code_scanner.bad_addr is None

    def operate(self, odb_file):

        self.object_id = odb_file.get_object_id()

        parcels = ParcelList(odb_file.get_structure_list(Parcel))
        if len(parcels) == 0:
            raise Exception('Invalid operation: No parcels found')

        parcels_to_adjust = [p for p in parcels if p.vma_start > self.vma]

        analyzer = analyzer_factory(odb_file.get_arch())
        the_ofd = ofd.Ofd(odb_file.get_binary())
        p = parcels.find_parcel_by_vma(self.vma)

        if p is None:
            raise Exception('Invalid address: 0x%08x' % self.vma)

        # before doing anything, check if the given address starts with at least one valid instruction
        if not self._is_valid_instruction(the_ofd, analyzer, self.vma, p.vma_end):
            raise Exception("Failed to make code: invalid opcode")

        bad_code_scanner = BadCodeScanner(analyzer)
        function_scanner = FunctionScanner(analyzer, odb_file.get_structure_list(Symbol))
        branch_scanner = BranchScanner(analyzer)
        parcel_scanner = ParcelOffsetScanner()

        scanners = [
            # The parcel scanner must come first here, because we need it to 'push_vma' for the bad instruction, if
            # one is encountered
            parcel_scanner,
            bad_code_scanner,
            function_scanner,
            branch_scanner,
        ]

        # split the data parcel
        odb_file.execute(SplitParcelOperation(self.vma))

        parcels = ParcelList(odb_file.get_structure_list(Parcel))
        p = parcels.find_parcel_by_vma(self.vma)
        ldas_before_scan = p.size # one lda per byte

        def callback(addr, rawData, instr, abfd, self):
            for scanner in scanners:
                scanner.scan_line(addr, rawData, instr, abfd, p)

        section = the_ofd.get_section_from_addr(self.vma)
        the_ofd.disassemble(section.name, [], self.vma, p.vma_end,
                            funcFmtLine=callback,
                            funcFmtLineArgs={
                                'self': self,
                                })

        ldas_removed = ldas_before_scan - p.num_ldas
        for p in parcels_to_adjust:
            p.lda_start -= ldas_removed

        for scanner in scanners:
            scanner.commit(odb_file)

        bad_addr = bad_code_scanner.bad_addr
        if bad_addr is not None:
            p = parcels.find_parcel_by_vma(bad_addr)
            odb_file.execute(SplitParcelOperation(bad_addr))

        #
        # consolidate the code parcels
        #
        parcels = ParcelList(odb_file.get_structure_list(Parcel))
        transaction = parcels.consolidate()

        # remove dead parcels
        for p in transaction.to_remove:
            odb_file.remove_item(p)

