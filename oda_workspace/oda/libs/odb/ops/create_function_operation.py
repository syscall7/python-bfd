import logging

from oda.libs.odb.ops.operation import Operation
from oda.libs.odb.structures.function import Function

logger = logging.getLogger(__name__)

class CreateFunctionOperation(Operation):

    def __init__(self, vma, name, args, retval):
        super(CreateFunctionOperation, self).__init__()
        self.object_id = -1

    def operate(self, odb_file):

        # TODO: Verify that the given address is already code
        # TODO: Verify that the given function name does not already exist

        func = self.odb_file.create_item(Function, {
            'name': self.name,
            'offset': self.vma,
            'sym_type': 't',
            'xrefs': [],
            'retval': self.retval,
            'args': self.args,
        })

        self.odb_file.insert_item(func)