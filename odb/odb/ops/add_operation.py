from odb.ops.operation import Operation
from odb.structures.function import Function

__author__ = 'davis'


class AddOperation(Operation):
    def __init__(self, item):
        self.item = item

    def operate(self, odb_file):
        odb_file.insert_item(self.item)

    def invert(self, odb_file):
        #func = next(x for x in odb_file.functions if x.object_id == self.function_object_id)
        odb_file.remove_item(self.item)






