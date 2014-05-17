import os
import unittest

from oda.libs.odb.odb_file import OdbFile
from oda.libs.odb.ops.load_operation import LoadOperation
from oda.libs.odb.ops.scan_operation import ScanOperation
from oda.libs.odb.structures.branch import Branch
from oda.libs.odb.structures.function import Function
from oda.libs.odb.odb_file import BinaryFile, BinaryString

__author__ = 'davis'


class TestScanOperation(unittest.TestCase):
    def test_basic_scan(self):
        cwd = os.path.dirname(os.path.realpath(__file__))

        odb_file = OdbFile(BinaryFile(os.path.join(cwd, 'data/ls'), 'elf64-x86-64', 'i386:x86-64'))
        odb_file.execute(LoadOperation())
        odb_file.execute(ScanOperation())

        self.assertEqual(215, len(odb_file.get_structure_list(Function)))

        for f in odb_file.get_structure_list(Function):
            print(f.name)

        self.assertEqual(2814, len(odb_file.get_structure_list(Branch)))