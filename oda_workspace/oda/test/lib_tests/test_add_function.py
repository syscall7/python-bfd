from oda.libs.odb.odb_file import OdbFile
from oda.libs.odb.ops.add_operation import AddOperation
from oda.libs.odb.ops.operation import ValidationError
from oda.libs.odb.structures import function
from oda.libs.odb.structures.function import Function
from oda.test.oda_test_case import OdaLibTestCase

class TestAddFunction(OdaLibTestCase):
    def test_add(self):
        odb_file = OdbFile()

        item = odb_file.create_item(Function, {
            'name': 'FUNCTION TEST NAME',
            'offset': 0,
            'sym_type': 'U'

        })
        add_operation = function.generate_operation(AddOperation, item)

        odb_file.execute(add_operation)

        #add_func_operation = AddFunction(**{'name': 'blah'})
        #add_func_operation.operate(odb_file)

        self.assertEquals(1, len(odb_file.get_structure_list(Function)))
        f = odb_file.get_structure_list(Function)[0]
        self.assertEquals('FUNCTION TEST NAME', odb_file.get_structure_list(Function)[0].name)

        add_operation.invert(odb_file)

        self.assertEquals(0, len(odb_file.get_structure_list(Function)))

    def test_multiple_add(self):
        odb_file = OdbFile()
        item = odb_file.create_item(Function, {
            'name': 'FUNCTION TEST NAME1',
            'offset': 0,
            'sym_type': 'U'
        })
        add_operation = function.generate_operation(AddOperation, item)
        odb_file.execute(add_operation)

        item2 = odb_file.create_item(Function, {
            'name': 'FUNCTION TEST NAME2',
            'offset': 0,
            'sym_type': 'U'
        })
        add_operation2 = function.generate_operation(AddOperation, item2)
        odb_file.execute(add_operation2)

        self.assertEquals(2, len(odb_file.get_structure_list(Function)))

        add_operation2.invert(odb_file)
        self.assertEquals(1, len(odb_file.get_structure_list(Function)))
        self.assertEquals('FUNCTION TEST NAME1', odb_file.get_structure_list(Function)[0].name)

        add_operation.invert(odb_file)
        self.assertEquals(0, len(odb_file.get_structure_list(Function)))

    def test_add_same_func_name_fails(self):
        odb_file = OdbFile()
        item = odb_file.create_item(Function, {
            'name': 'FUNCTION TEST NAME1',
            'offset': 0,
            'sym_type': 'U'
        })
        add_operation = function.generate_operation(AddOperation, item)
        odb_file.execute(add_operation)

        item = odb_file.create_item(Function, {
            'name': 'FUNCTION TEST NAME1',
            'offset': 0,
            'sym_type': 'U'
        })
        add_operation = function.generate_operation(AddOperation, item)
        self.assertRaises(ValidationError, odb_file.execute, add_operation)




    def test_add_same_id_fails(self):
        odb_file = OdbFile()
        item = odb_file.create_item(Function, {
            'name': 'FUNCTION TEST NAME1',
            'offset': 0,
            'sym_type': 'U'
        })
        add_operation = function.generate_operation(AddOperation, item)
        odb_file.execute(add_operation)

        #This is a little forced, since the add_operation.item should really be immutable
        add_operation.item = odb_file.create_item(Function, {
            'name': 'FUNCTION TEST NAME2',
            'offset': 0,
            'sym_type': 'U'
        })
        self.assertRaises(ValidationError, odb_file.execute, add_operation)

    def invert_not_last_fails(self):
        pass
