from oda.libs.odb.ops.add_operation import AddOperation
from oda.libs.odb.ops.operation import Validator, ValidationError
from oda.libs.odb.structures.oda_object import OdaObject

__author__ = 'davis'


class NameValidator(Validator):
    def validate(self, operation, odb_file):
        v = next((f for f in odb_file.get_structure_list(Function) if f.name == operation.item.name), None)
        if v is not None:
            raise ValidationError('Cannot Use Duplicate Function Name')


def generate_operation(op, *args):
    factory = {
        AddOperation: AddOperation(args[0], [NameValidator()])
    }
    if op in factory:
        return factory[op]

    return op(*args)


class Function(OdaObject):
    def __init__(self, object_id, name, offset, sym_type, xrefs=set([]), retval='unknown', args='unknown'):
        super(Function, self).__init__(object_id)
        self.name = name
        self.offset = offset
        self.xrefs = xrefs
        self.type = sym_type
        self.retval = retval
        self.args = args