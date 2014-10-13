import logging

from oda.libs.odb.ops.operation import Operation
from oda.libs.odb.structures.function import Function

logger = logging.getLogger(__name__)

class CreateFunctionOperation(Operation):

    def __init__(self, vma, name, args, retval):
        super(CreateFunctionOperation, self).__init__()
        self.object_id = -1
        self.name = name
        self.vma = vma
        self.args = args
        self.retval = retval

    def operate(self, odb_file):

        # TODO: Verify that the given address is already code
        # TODO: Verify that the given function name does not already exist

        self.object_id = odb_file.get_object_id()

        func = odb_file.create_item(Function, {
            'name': self.name,
            'offset': self.vma,
            'sym_type': 't',
            'xrefs': [],
            'retval': self.retval,
            'args': self.args,
        })

        odb_file.insert_item(func)

class EditFunctionOperation(Operation):

    def __init__(self, vma, name, args, retval):
        super(EditFunctionOperation, self).__init__()
        self.object_id = -1
        self.name = name
        self.vma = vma
        self.args = args
        self.retval = retval

    def operate(self, odb_file):
        self.object_id = odb_file.get_object_id()

        functions = {f.offset: f for f in odb_file.get_structure_list(Function)}

        if (self.vma in functions.keys()):
            f = functions[self.vma]

            if self.name != None:
                f.name = self.name

            if self.args != None:
                f.args = self.args

            if self.retval != None:
                f.retval = self.retval
        else:
            raise Exception("Cannot edit a function that does not already exist!")
