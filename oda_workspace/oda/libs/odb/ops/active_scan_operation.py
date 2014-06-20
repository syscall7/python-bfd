import logging

from oda.libs.odb.bfd import ofd
from oda.libs.odb.bfd.analyzer import analyzer_factory
from oda.libs.odb.ops.operation import Operation
from oda.libs.odb.structures.parcel import Parcel, ParcelList
from oda.libs.odb.ops.scanners import FunctionScanner, BranchScanner, ParcelOffsetScanner, BadCodeScanner, HaltScanException
from oda.libs.odb.ops.split_parcel_operation import SplitParcelOperation

logger = logging.getLogger(__name__)

class ActiveScanOperation(Operation):

    def __init__(self, vma):
        super(ActiveScanOperation, self).__init__()
        self.object_id = -1
        self.vma = vma

    def operate(self, odb_file):
        assert (len(odb_file.get_structure_list(Parcel)) > 0)

        self.object_id = odb_file.get_object_id()
        analyzer = analyzer_factory(odb_file.get_arch())

        bad_code_scanner = BadCodeScanner(analyzer)
        function_scanner = FunctionScanner(analyzer)
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

        parcels = ParcelList(odb_file.get_structure_list(Parcel))
        parcels_to_adjust = [p for p in parcels if p.vma_start > self.vma]

        # split the data parcel
        odb_file.execute(SplitParcelOperation(self.vma))

        parcels = ParcelList(odb_file.get_structure_list(Parcel))
        p = parcels.find_parcel_by_vma(self.vma)
        ldas_before_scan = p.size # one lda per byte

        def callback(addr, rawData, instr, abfd, self, code_ldas):
            code_ldas += 1
            for scanner in scanners:
                scanner.scan_line(p, addr, rawData, instr, abfd)

        the_ofd = ofd.Ofd(odb_file.get_binary())
        section = the_ofd.get_section_from_addr(p.vma_start)

        code_ldas = 0
        the_ofd.disassemble(section.name, [], self.vma, p.vma_end,
                            funcFmtLine=callback,
                            funcFmtLineArgs={
                                'self': self,
                                'code_ldas': code_ldas,
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

