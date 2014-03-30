from odb.structures.oda_object import OdaObject

__author__ = 'davis'

class Function(OdaObject):
    def __init__(self, name):
        super(Function, self).__init__(1)
        self.name = name