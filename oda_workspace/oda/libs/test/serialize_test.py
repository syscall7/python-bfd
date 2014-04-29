import unittest

from odb.odb_file import OdbFile, DefaultOdbSerializer
from odb.ops.load_operation import LoadOperationFactory
from odb.structures.function import Function


__author__ = 'davis'


class TestSerialize(unittest.TestCase):

    def test_serialize(self):
        load_operation = LoadOperationFactory.load_from_file('test/data/ls')
        odb_file = OdbFile()
        load_operation.operate(odb_file)

        serialized = DefaultOdbSerializer().dumps(odb_file)

        loaded_odb_file = DefaultOdbSerializer().load(serialized)

        self.assertEqual(len(odb_file.get_structure_list(Function)), len(loaded_odb_file.get_structure_list(Function)))



