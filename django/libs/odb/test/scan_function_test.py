import unittest
from odb.odb_file import OdbFile
from odb.ops.load_operation import LoadOperationFactory
from odb.ops.scan_operation import ScanOperation
from odb.structures.branch import Branch
from odb.structures.function import Function


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