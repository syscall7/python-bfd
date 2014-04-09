import unittest

from odb.odb_file import OdbFile
from odb.ops.load_operation import LoadOperationFactory
from odb.structures.data_string import DataString
from odb.structures.function import Function
from odb.structures.section import Section
from odb.structures.symbol import Symbol


class TestLoadOperation(unittest.TestCase):

    def test_basic_loader(self):
        load_operation = LoadOperationFactory.load_from_file('test/data/ls')
        odb_file = OdbFile()

        odb_file.execute(load_operation)

        self.assertEquals(26, len(odb_file.get_structure_list(Section)))

        self.assertEquals(120, len(odb_file.get_structure_list(Symbol)))

        self.assertEquals(2, len(odb_file.get_structure_list(Function)))

        self.assertEquals(1, len([x for x in odb_file.get_structure_list(Function) if x.name == '_init']))
        self.assertEquals(1, len([x for x in odb_file.get_structure_list(Function) if x.name == '_fini']))

        self.assertEquals(1304, len(odb_file.get_structure_list(DataString)))

        self.assertEquals(1, len([s for s in odb_file.get_structure_list(DataString) if s.value == 'hide-control-chars']))
        self.assertEquals(1, len([s for s in odb_file.get_structure_list(DataString) if s.value == 'error initializing month strings']))

    def test_load_string(self):
        odb_file = OdbFile()

        load_operation = LoadOperationFactory.load_from_string('55 31 D2 89 E5 8B 45 08 56 8B 75 0C 53 8D 58 FF 0F B6 0C 16 88 4C 13 01 83 C2 01 84 C9 75 F1 5B 5E 5D C3')

        odb_file.execute(load_operation)

