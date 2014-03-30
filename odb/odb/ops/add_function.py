from odb.ops.operation import Operation
from odb.structures.function import Function

__author__ = 'davis'

class AddFunction(Operation):

    def __init__(self, **kwargs):
        self.name = kwargs['name']
        self.function_object_id = -1

    def operate(self, odbFile):
        func = Function(self.name)
        self.function_object_id = func.object_id
        odbFile.functions.append(func)

    def invert(self, odbFile):
        func = next(x for x in odbFile.functions if x.object_id == self.function_object_id)
        odbFile.functions.remove(func)






