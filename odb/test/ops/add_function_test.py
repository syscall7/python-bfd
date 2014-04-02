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

    # def test_multiple_add(self):
    #     odb_file = OdbFile()
    #     add_func_operation = AddFunction(**{'name': 'blah'})
    #     add_func_operation.operate(odb_file)
    #
    #     add_func_operation2 = AddFunction(**{'name': 'blah2'})
    #     add_func_operation2.operate(odb_file)
    #
    #     self.assertEqual(2, len(odb_file.functions))
    #
    #     add_func_operation2.invert(odb_file)
    #     self.assertEqual(1, len(odb_file.functions))
    #     self.assertEqual('blah', odb_file.functions[0].name)
    #
    #     add_func_operation.invert(odb_file)
    #     self.assertEqual(0, len(odb_file.functions))


if __name__ == "__main__":
    unittest.main()