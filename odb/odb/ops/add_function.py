from odb.ops.operation import Operation
from odb.structures.function import Function

__author__ = 'davis'

class AddFunction(Operation):

    def __init__(self, **kwargs):
        self.name = kwargs.name

    def operate(self, odbFile):
        func = Function(self.name)
        self.old_name = func.name
        odbFile.functions.push(func)

    def invert(self, odbFile):
        func = next(x for x in odbFile.functions if x.object_id == self.object_id)
        func.name = self.old_name






