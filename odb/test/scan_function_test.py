import unittest
from odb.odb_file import OdbFile
from odb.ops.load_operation import LoadOperation
from odb.ops.scan_operation import ScanOperation
from odb.structures.function import Function

__author__ = 'davis'


class TestScanOperation(unittest.TestCase):

    def testBasicScan(self):
        load_operation = LoadOperation('test/data/ls')
        odb_file = OdbFile()
        load_operation.operate(odb_file)

        scan_operation = ScanOperation()
        scan_operation.operate(odb_file)

        self.assertEqual(2, len(odb_file.items[Function]))