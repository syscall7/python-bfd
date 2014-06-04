import os
import unittest

from oda.libs.odb.odb_file import OdbFile
from oda.libs.odb.ops.load_operation import LoadOperation
from oda.libs.odb.odb_file import BinaryFile
from oda.libs.odb.bfd.disassembler import Disassembler


class TestAnalyzer(unittest.TestCase):

    def test_total_lines(self):
        cwd = os.path.dirname(os.path.realpath(__file__))

        odb_file = OdbFile(BinaryFile(os.path.join(cwd, 'data/ls'), 'elf64-x86-64', 'i386:x86-64'))
        odb_file.execute(LoadOperation())

        dasm = Disassembler(odb_file)
        total_lines = dasm.total_lines()

        self.assertEquals(41614, total_lines)


