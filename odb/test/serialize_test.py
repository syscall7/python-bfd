import unittest
from odb.odb_file import OdbFile, DefaultOdbSerializer
from odb.ops.load_operation import LoadOperation
from odb.structures.function import Function

__author__ = 'davis'


class TestSerialize(unittest.TestCase):

    def test_serialize(self):
        load_operation = LoadOperation('test/data/ls')
        odb_file = OdbFile()
        load_operation.operate(odb_file)

        serialized = DefaultOdbSerializer().dumps(odb_file)

        loaded_odb_file = DefaultOdbSerializer().load(serialized)

        self.assertEqual(len(odb_file.items[Function]), len(loaded_odb_file.items[Function]))



