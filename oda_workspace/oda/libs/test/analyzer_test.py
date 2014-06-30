import os
import unittest

from oda.libs.odb.odb_file import OdbFile
from oda.libs.odb.ops.load_operation import LoadOperation
from oda.libs.odb.ops.passive_scan_operation import PassiveScanOperation
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

    def test_analyzer_output(self):
        cwd = os.path.dirname(os.path.realpath(__file__))

        odb_file = OdbFile(BinaryFile(os.path.join(cwd, 'data/ls'), 'elf64-x86-64', 'i386:x86-64'))
        odb_file.execute(LoadOperation())
        odb_file.execute(PassiveScanOperation())

        dasm = Disassembler(odb_file)

        # Disassemble at a provided offset
        units = dasm.analyze(0x4095e0, 200, False)

        # The provided address should be the first instruction
        self.assertEquals(0x4095e0, units[0].offset)
        self.assertEquals("mov", units[0].opcode)

        # Another random instruction
        self.assertEquals("test", units[18].opcode)
        self.assertEquals("al,al", units[18].operands)

        # Disassemble at a provided negative offset
        units = dasm.analyze(0x4095e0, -10, False)

        # The provided address should be the last instruction
        self.assertEquals(0x4095e0, units[9].offset)
        self.assertEquals("mov", units[9].opcode)
        # IDA finds this one through a function pointer in data section
        # self.assertEquals(True, units[9].isFunction)

        # 9 instructions earlier
        self.assertEquals(0x4095BB, units[0].offset)
        self.assertEquals("call", units[0].opcode)

        # Disassemble a function
        units = dasm.analyze(0x40BEE0, 10, False)
        self.assertEquals(True, units[0].isFunction)

        # Cross Parcel Boundaries
        units = dasm.analyze(0x412BF4, -10, False)
        self.assertEquals(0x412BF4, units[9].offset)
        self.assertEquals("ret", units[9].opcode)
        self.assertEquals(".fini", units[9].section_name)
        self.assertEquals(0x412BE1, units[2].offset)
        self.assertEquals("jmp", units[2].opcode)
        self.assertEquals(".text", units[2].section_name)

        # Cross Code/Data Boundaries
        units = dasm.analyze(0x412BF4, 10, False)
        self.assertEquals(0x412BF4, units[0].offset)
        self.assertEquals(0x412C00, units[1].offset)
        self.assertEquals(1, units[1].dataSize)




