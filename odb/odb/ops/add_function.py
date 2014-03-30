from odb.ops.operation import Operation
from odb.structures.function import Function

__author__ = 'davis'


class AddFunction(Operation):
    def __init__(self, **kwargs):
        self.name = kwargs['name']
        self.function_object_id = -1

    def operate(self, odb_file):
        func = Function(self.name, odb_file.get_object_id())
        self.function_object_id = func.object_id
        odb_file.functions.append(func)

    def invert(self, odb_file):
        func = next(x for x in odb_file.functions if x.object_id == self.function_object_id)
        odb_file.functions.remove(func)






