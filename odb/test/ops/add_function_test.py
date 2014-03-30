import unittest
from odb.odb_file import OdbFile
from odb.ops.add_function import AddFunction


class TestAddFunction(unittest.TestCase):

    def testAdd(self):
        odbFile = OdbFile()
        addFuncOperation = AddFunction()
        addFuncOperation.operate(odbFile)

        self.assertEquals(1, len(odbFile.functions))


if __name__ == "__main__":

    unittest.main()