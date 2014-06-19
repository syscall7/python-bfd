import logging

from oda.libs.odb.bfd import ofd
from oda.libs.odb.bfd.analyzer import analyzer_factory
from oda.libs.odb.ops.operation import Operation
from oda.libs.odb.structures.parcel import Parcel
from oda.libs.odb.ops.scanners import FunctionScanner, BranchScanner, ParcelOffsetScanner

logger = logging.getLogger(__name__)

class PassiveScanOperation(Operation):

    def __init__(self):
        super(PassiveScanOperation, self).__init__()
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
        parcels.sort(key=lambda p: p.vma_start, reverse=False)

        for parcel in parcels:

            logger.debug("parcel.vma_start=0x%08x parcel.vma_end=0x%08x" % (parcel.vma_start, parcel.vma_end))

            # initialize the logical display unit address

            the_ofd = ofd.Ofd(odb_file.get_binary())
            section = the_ofd.get_section_from_addr(parcel.vma_start)

            parcel.lda_start = lda_offset
            if parcel.is_code:

                def callback(addr, rawData, instr, abfd, self):
                    for scanner in scanners:
                        scanner.scan_line(parcel, addr, rawData, instr, abfd)


                the_ofd.disassemble(section.name, [], parcel.vma_start, parcel.vma_end,
                                    funcFmtLine=callback,
                                    funcFmtLineArgs={
                                        'self': self,
                                    })

            # account for the new display units
            lda_offset += parcel.num_ldas

        for scanner in scanners:
            scanner.commit(odb_file)