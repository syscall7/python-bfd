import unittest

from oda.libs.odb.odb_file import OdbFile
from oda.libs.odb.ops.add_operation import AddOperation
from oda.libs.odb.structures import c_struct
from oda.libs.odb.structures.c_struct import CStruct, BuiltinField, CStructField
from oda.libs.odb.structures.types import BuiltInTypeFactory

__author__ = 'davis'

class TestAddCStruct(unittest.TestCase):
    def test_add(self):

        odb_file = OdbFile()

        item = odb_file.create_item(CStruct, {
            'name' : 'simpleStruct'
        })

        builtin = BuiltInTypeFactory('Uint8')
        item.append_field( BuiltinField(name='Field1',type=builtin) )
        item.append_field( BuiltinField(name='Field2',type=builtin) )
        item.append_field( BuiltinField(name='Field3',type=builtin) )

        self.assertEquals(3, item.size)

        odb_file.execute(c_struct.generate_operation(AddOperation, item))

        self.assertEquals(1, len(odb_file.get_structure_list(CStruct)))

    def test_compound_add(self):

        odb_file = OdbFile()

        item = odb_file.create_item(CStruct, {
            'name' : 'simpleStruct'
        })

        builtin = BuiltInTypeFactory('Uint8')
        item.append_field( BuiltinField(name='Field1',type=builtin) )
        item.append_field( BuiltinField(name='Field2',type=builtin) )
        item.append_field( BuiltinField(name='Field3',type=builtin) )

        odb_file.execute(c_struct.generate_operation(AddOperation, item))

        item2 = odb_file.create_item(CStruct, {
            'name' : 'complexStruct'
        })

        item2.append_field( BuiltinField(name='Field1',type=builtin) )
        item2.append_field( CStructField(name='Field3',c_struct_obj=item) )

        odb_file.execute(c_struct.generate_operation(AddOperation, item2))


        struct_list = odb_file.get_structure_list(CStruct)
        self.assertEquals(2, len(struct_list))
        self.assertEquals(4, struct_list[1].size)

        item.delete_field( name='Field2')

        struct_list = odb_file.get_structure_list(CStruct)
        sizeLen = struct_list[1].size
        self.assertEquals(3, sizeLen )

