from oda.libs.odb.ops.add_operation import AddOperation
from oda.libs.odb.structures.comment import OffsetValidator
from oda.libs.odb.structures.oda_object import OdaObject

__author__ = 'davis'


def generate_operation(op, *args):
    factory = {
        AddOperation: AddOperation(args[0], [OffsetValidator()])
    }
    if op in factory:
        return factory[op]

    return op(*args)

class Label(OdaObject):
    def __init__(self, object_id, **kwargs):
        super(Label, self).__init__(object_id)
        self.offset = kwargs['offset']
        self.name = kwargs['name']