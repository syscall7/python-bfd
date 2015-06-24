import os
from oda.libs.odb.binaries import BinaryFile

from oda.libs.odb.odb_file import OdbFile
from oda.libs.odb.ops.load_operation import LoadOperation
from oda.libs.odb.ops.active_scan_operation import ActiveScanOperation
from oda.libs.odb.ops.passive_scan_operation import PassiveScanOperation
from oda.libs.odb.structures.parcel import Parcel, ParcelList
from oda.test.oda_test_case import OdaLibTestCase
from oda.libs.odb.bfd.analyzers.branch import BranchGraphView, BranchGraphNode

class TestGraphNodes(OdaLibTestCase):

    # basic test to verify we generate the graph nodes correctly
    def test_basic_graph_nodes(self):

        # we load this ELF as a raw binary, because it has an invalid opcode fairly early on
        odb_file = OdbFile(BinaryFile(self.get_test_bin_path('mkdir'), 'elf64-x86-64', 'i386:x86-64'))
        odb_file.execute(LoadOperation())
        odb_file.execute(PassiveScanOperation())

        bgv = BranchGraphView(odb_file, 0x401980)

        expectedNodes = [
            BranchGraphNode(0x401980, 0x401990, 0x4019dd, 0x401992),
            BranchGraphNode(0x401992, 0x4019b0, 0x4019d6, 0x4019b2),
            BranchGraphNode(0x4019b2, 0x4019b2, 0x4019b8, None),
            BranchGraphNode(0x4019b8, 0x4019d4, 0x4019b8, 0x4019d6),
            BranchGraphNode(0x4019d6, 0x4019d6, 0x4019dd, None),
            BranchGraphNode(0x4019dd, 0x4019e4, None, None),
        ]

        self.assertItemsEqual(expectedNodes, bgv._nodes.values())

