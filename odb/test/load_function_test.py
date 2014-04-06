import unittest
from odb.odb_file import OdbFile
from odb.ops.load_operation import LoadOperation
from odb.structures.function import Function
from odb.structures.section import Section
from odb.structures.symbol import Symbol


class TestLoadOperation(unittest.TestCase):

    def test_basic_loader(self):
        load_operation = LoadOperation('test/data/ls')
        odb_file = OdbFile()
        load_operation.operate(odb_file)

        self.assertEquals(26, len(odb_file.items[Section]))

        self.assertEquals(120, len(odb_file.items[Symbol]))

        self.assertEquals(2, len(odb_file.items[Function]))

        self.assertEquals(1, len([x for x in odb_file.items[Function] if x.name == '_init']))
        self.assertEquals(1, len([x for x in odb_file.items[Function] if x.name == '_fini']))