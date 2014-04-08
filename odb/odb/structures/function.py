from odb.ops.add_operation import AddOperation
from odb.ops.load_operation import LoadOperation
from odb.ops.operation import Validator
from odb.structures.oda_object import OdaObject

__author__ = 'davis'


class NameValidator(Validator):
    def validate(self, operation, odb_file):
        next((f for f in odb_file.get_structure_list(Function) if f.name == operation.item.name), None) is None


def generate_operation(op, *args):
    factory = {
        AddOperation: AddOperation(args[0], [NameValidator()])
    }
    if op in factory:
        return factory[op]

    return op(*args)


class Function(OdaObject):
    def __init__(self, object_id, **kwargs):
        super(Function, self).__init__(object_id)
        self.name = kwargs['name']
        self.offset = kwargs['offset']
        self.xrefs = kwargs.get('xrefs', [])
        self.type = kwargs['type']