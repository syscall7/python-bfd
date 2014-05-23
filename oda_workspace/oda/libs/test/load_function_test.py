import os
import unittest

from oda.libs.odb.odb_file import OdbFile
from oda.libs.odb.ops.load_operation import LoadOperation
from oda.libs.odb.ops.scan_operation import ScanOperation
from oda.libs.odb.structures.branch import Branch
from oda.libs.odb.structures.data_string import DataString
from oda.libs.odb.structures.function import Function
from oda.libs.odb.structures.parcel import Parcel
from oda.libs.odb.structures.section import Section
from oda.libs.odb.structures.symbol import Symbol
from oda.libs.odb.odb_file import BinaryFile, BinaryString

class TestLoadOperation(unittest.TestCase):

    def test_basic_loader(self):
        cwd = os.path.dirname(os.path.realpath(__file__))

        odb_file = OdbFile(BinaryFile(os.path.join(cwd, 'data/ls'), 'elf64-x86-64', 'i386:x86-64'))
        odb_file.execute(LoadOperation())

        self.assertEquals(26, len(odb_file.get_structure_list(Section)))

        self.assertEquals(120, len(odb_file.get_structure_list(Symbol)))

        self.assertEquals(2, len(odb_file.get_structure_list(Function)))

        self.assertEquals(1, len([x for x in odb_file.get_structure_list(Function) if x.name == '_init']))
        self.assertEquals(1, len([x for x in odb_file.get_structure_list(Function) if x.name == '_fini']))

        self.assertEquals(1304, len(odb_file.get_structure_list(DataString)))

        self.assertEquals(1, len([s for s in odb_file.get_structure_list(DataString) if s.value == 'hide-control-chars']))
        self.assertEquals(1, len([s for s in odb_file.get_structure_list(DataString) if s.value == 'error initializing month strings']))

    def test_basic_binary_loader(self):
        cwd = os.path.dirname(os.path.realpath(__file__))

        odb_file = OdbFile(BinaryFile(os.path.join(cwd, 'data/ls.bin.x86-64'), 'binary', 'i386:x86-64'))
        odb_file.execute(LoadOperation())

        self.assertEquals(1, len(odb_file.get_structure_list(Section)))

        self.assertEquals(0, len(odb_file.get_structure_list(Symbol)))

        self.assertEquals(0, len(odb_file.get_structure_list(Function)))

        self.assertEquals(857, len(odb_file.get_structure_list(DataString)))

    def test_load_string(self):

        s = '55 31 D2 89 E5 8B 45 08 56 8B 75 0C 53 8D 58 FF 0F B6 0C 16 88 4C 13 01 83 C2 01 84 C9 75 F1 5B 5E 5D C3'

        odb_file = OdbFile(BinaryString(s, 'i386'))
        odb_file.execute(LoadOperation())

        scan_operation = ScanOperation()
        odb_file.execute(scan_operation)

        self.assertEqual(1, len(odb_file.get_structure_list(Branch)))
        self.assertEqual(1, len(odb_file.get_structure_list(Parcel)))
        self.assertEqual(0, odb_file.get_structure_list(Parcel)[0].start)
        self.assertEqual(35, odb_file.get_structure_list(Parcel)[0].end)

    def test_hash(self):
        s = '55 31 D2 89 E5 8B 45 08 56 8B 75 0C 53 8D 58 FF 0F B6 0C 16 88 4C 13 01 83 C2 01 84 C9 75 F1 5B 5E 5D C3'

        odb_file = OdbFile(BinaryString(s, 'i386'))
        self.assertEqual('d41d8cd98f00b204e9800998ecf8427e', odb_file.get_binary().md5())
        self.assertEqual('da39a3ee5e6b4b0d3255bfef95601890afd80709', odb_file.get_binary().sha1())




    def test_load_string_arm(self):

        s = '01 20 40 E2 02 20 61 E0 01 30 D1 E4 00 00 53 E3 02 30 C1 E7 FB FF FF 1A 1E FF 2F E1'

        odb_file = OdbFile(BinaryString(s, 'arm'))
        odb_file.execute(LoadOperation())

        scan_operation = ScanOperation()
        odb_file.execute(scan_operation)

        self.assertEqual(0, len(odb_file.get_structure_list(Branch)))


