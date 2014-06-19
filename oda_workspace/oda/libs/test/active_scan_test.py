import os
import unittest

from oda.libs.odb.odb_file import OdbFile
from oda.libs.odb.ops.load_operation import LoadOperation
from oda.libs.odb.ops.active_scan_operation import ActiveScanOperation
from oda.libs.odb.structures.branch import Branch
from oda.libs.odb.structures.function import Function
from oda.libs.odb.odb_file import BinaryFile, BinaryString

__author__ = 'davis'


class TestActiveScanOperation(unittest.TestCase):

    def test_basic_active_scan(self):
        cwd = os.path.dirname(os.path.realpath(__file__))

        # we load this ELF as a raw binary, because it has an invalid opcode fairly early on
        odb_file = OdbFile(BinaryFile(os.path.join(cwd, 'data/ls'), 'binary', 'i386:x86-64'))
        odb_file.execute(LoadOperation())

        # scan starting at address 0
        odb_file.execute(ActiveScanOperation(0))

