import unittest
from odb.odb_file import OdbFile
from odb.ops.add_function import AddFunction


class TestAddFunction(unittest.TestCase):
    def test_add(self):
        odb_file = OdbFile()
        add_func_operation = AddFunction(**{'name': 'blah'})
        add_func_operation.operate(odb_file)

        self.assertEquals(1, len(odb_file.functions))
        self.assertEquals('blah', odb_file.functions[0].name)

        add_func_operation.invert(odb_file)

        self.assertEquals(0, len(odb_file.functions))

    def test_multiple_add(self):
        odb_file = OdbFile()
        add_func_operation = AddFunction(**{'name': 'blah'})
        add_func_operation.operate(odb_file)

        add_func_operation2 = AddFunction(**{'name': 'blah2'})
        add_func_operation2.operate(odb_file)

        self.assertEqual(2, len(odb_file.functions))

        add_func_operation2.invert(odb_file)
        self.assertEqual(1, len(odb_file.functions))
        self.assertEqual('blah', odb_file.functions[0].name)

        add_func_operation.invert(odb_file)
        self.assertEqual(0, len(odb_file.functions))


if __name__ == "__main__":
    unittest.main()