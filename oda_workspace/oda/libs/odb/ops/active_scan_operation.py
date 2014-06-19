import logging

from oda.libs.odb.bfd import ofd
from oda.libs.odb.bfd.analyzer import analyzer_factory
from oda.libs.odb.ops.operation import Operation
from oda.libs.odb.structures.parcel import Parcel, ParcelList
from oda.libs.odb.ops.scanners import FunctionScanner, BranchScanner, ParcelOffsetScanner, BadCodeScanner, HaltScanException

logger = logging.getLogger(__name__)

class ActiveScanOperation(Operation):

    def __init__(self, vma):
        super(ActiveScanOperation, self).__init__()
        self.object_id = -1
        self.vma = vma

    def operate(self, odb_file):
        assert (len(odb_file.get_structure_list(Parcel)) > 0)

        self.object_id = odb_file.get_object_id()

        bad_code_scanner = BadCodeScanner(analyzer_factory(odb_file.get_arch()))
        function_scanner = FunctionScanner(analyzer_factory(odb_file.get_arch()))
        branch_scanner = BranchScanner(analyzer_factory(odb_file.get_arch()))
        parcel_scanner = ParcelOffsetScanner()

        scanners = [
            bad_code_scanner,
            function_scanner,
            branch_scanner,
            parcel_scanner
        ]

        parcels = ParcelList(odb_file.get_structure_list(Parcel))
        p = parcels.find_parcel_by_vma(self.vma)

        def callback(addr, rawData, instr, abfd, self):
            for scanner in scanners:
                scanner.scan_line(p, addr, rawData, instr, abfd)

        the_ofd = ofd.Ofd(odb_file.get_binary())
        section = the_ofd.get_section_from_addr(p.vma_start)

        the_ofd.disassemble(section.name, [], self.vma, p.vma_end,
                            funcFmtLine=callback,
                            funcFmtLineArgs={
                                'self': self,
                                })

        for scanner in scanners:
            scanner.commit(odb_file)