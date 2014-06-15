from oda.libs.odb.ops.add_operation import AddOperation
from oda.libs.odb.ops.operation import ValidationError
from oda.libs.odb.structures.oda_object import OdaObject

__author__ = 'davis'


class OffsetValidator(object):
    def validate(self, operation, odb_file):
        offset = operation.item.offset
        if offset < 0 or offset > 1024:
            raise ValidationError("Offset not valid on item")

def generate_operation(op, *args):
    factory = {
        AddOperation: AddOperation(args[0], [OffsetValidator()])
    }
    if op in factory:
        return factory[op]

    return op(*args)

class Comment(OdaObject):
    def __init__(self, object_id, offset, comment):
        super(Comment, self).__init__(object_id)
        self.offset = offset
        self.comment = comment

