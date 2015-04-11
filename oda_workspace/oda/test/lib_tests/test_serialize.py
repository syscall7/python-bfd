import os
import unittest
from oda.libs.odb.binaries import BinaryFile

from oda.libs.odb.odb_file import OdbFile, DefaultOdbSerializer
from oda.libs.odb.ops.load_operation import LoadOperation
from oda.libs.odb.structures.function import Function

__author__ = 'davis'


class TestSerialize(unittest.TestCase):

    def test_serialize(self):
        cwd = os.path.dirname(os.path.realpath(__file__))

        odb_file = OdbFile(BinaryFile(os.path.join(cwd, 'data/ls'), 'elf64-x86-64', 'i386:x86-64'))
        odb_file.execute(LoadOperation())

        serialized = DefaultOdbSerializer().dumps(odb_file)

        loaded_odb_file = DefaultOdbSerializer().load(serialized)

        self.assertEqual(len(odb_file.get_structure_list(Function)), len(loaded_odb_file.get_structure_list(Function)))



