import unittest

from oda.libs.odb.odb_file import OdbFile
from oda.libs.odb.ops.load_operation import LoadOperationFactory
from oda.libs.odb.ops.scan_operation import ScanOperation
from oda.libs.odb.structures.branch import Branch
from oda.libs.odb.structures.function import Function


__author__ = 'davis'


class TestScanOperation(unittest.TestCase):
    def test_basic_scan(self):
        load_operation = LoadOperationFactory.load_from_file('test/data/ls')
        odb_file = OdbFile()
        load_operation.operate(odb_file)

        scan_operation = ScanOperation()
        scan_operation.operate(odb_file)

        self.assertEqual(215, len(odb_file.get_structure_list(Function)))

        for f in odb_file.get_structure_list(Function):
            print(f.name)

        self.assertEqual(2814, len(odb_file.get_structure_list(Branch)))