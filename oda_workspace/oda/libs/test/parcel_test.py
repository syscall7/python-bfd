import os
import unittest

from oda.libs.odb.odb_file import OdbFile
from oda.libs.odb.ops.load_operation import LoadOperation
from oda.libs.odb.ops.split_parcel_operation import SplitParcelOperation
from oda.libs.odb.ops.scan_operation import ScanOperation
from oda.libs.odb.structures.branch import Branch
from oda.libs.odb.structures.data_string import DataString
from oda.libs.odb.structures.function import Function
from oda.libs.odb.structures.parcel import Parcel
from oda.libs.odb.structures import parcel
from oda.libs.odb.structures.section import Section
from oda.libs.odb.structures.symbol import Symbol
from oda.libs.odb.odb_file import BinaryFile, BinaryString

class TestParcels(unittest.TestCase):

    def test_basic_split(self):
        cwd = os.path.dirname(os.path.realpath(__file__))

        odb_file = OdbFile(BinaryFile(os.path.join(cwd, 'data/ls'), 'elf64-x86-64', 'i386:x86-64'))
        odb_file.execute(LoadOperation())
        odb_file.execute(ScanOperation())

        parcels = odb_file.get_structure_list(Parcel)
        p = parcel.find_parcel_by_vma(0x4029c0, parcels)

        # number of parcels before the split
        self.assertEquals(25, len(parcels))

        odb_file.execute(SplitParcelOperation(0x4029d5, False))

        # number of parcels after the split
        parcels = odb_file.get_structure_list(Parcel)
        self.assertEquals(27, len(parcels))


