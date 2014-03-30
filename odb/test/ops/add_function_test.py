import unittest
from odb.odb_file import OdbFile
from odb.ops.add_function import AddFunction


class TestAddFunction(unittest.TestCase):

    def testAdd(self):
        odb_file = OdbFile()
        add_func_operation = AddFunction(**{'name': 'blah'})
        add_func_operation.operate(odb_file)

        self.assertEquals(1, len(odb_file.functions))

        add_func_operation.invert(odb_file)

        self.assertEquals(0, len(odb_file.functions))




if __name__ == "__main__":

    unittest.main()