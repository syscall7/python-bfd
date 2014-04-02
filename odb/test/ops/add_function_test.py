import unittest
from odb.odb_file import OdbFile
from odb.ops.add_operation import AddOperation
from odb.structures.function import Function


class TestAddFunction(unittest.TestCase):
    def test_add(self):
        odb_file = OdbFile()

        item = odb_file.create_item('Function', {
            'name': 'FUNCTION TEST NAME'
        })
        add_operation = AddOperation(item)

        add_operation.operate(odb_file)

        #add_func_operation = AddFunction(**{'name': 'blah'})
        #add_func_operation.operate(odb_file)

        self.assertEquals(1, len(odb_file.items[Function]))
        f = odb_file.items[Function][0]
        self.assertEquals('FUNCTION TEST NAME', odb_file.items[Function][0].name)

        add_operation.invert(odb_file)

        self.assertEquals(0, len(odb_file.items[Function]))

    def test_multiple_add(self):
        odb_file = OdbFile()
        item = odb_file.create_item('Function', {
            'name': 'FUNCTION TEST NAME1'
        })
        add_operation = AddOperation(item)
        add_operation.operate(odb_file)

        item2 = odb_file.create_item('Function', {
            'name': 'FUNCTION TEST NAME2'
        })
        add_operation2 = AddOperation(item2)
        add_operation2.operate(odb_file)

        self.assertEquals(2, len(odb_file.items[Function]))

        add_operation2.invert(odb_file)
        self.assertEquals(1, len(odb_file.items[Function]))
        self.assertEquals('FUNCTION TEST NAME1', odb_file.items[Function][0].name)

        add_operation.invert(odb_file)
        self.assertEquals(0, len(odb_file.items[Function]))

    def test_add_same_id_fails(self):
        pass

    def invert_not_last_fails(self):
        pass

if __name__ == "__main__":
    unittest.main()