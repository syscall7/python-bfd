from odb.structures.oda_object import OdaObject

__author__ = 'davis'

class Symbol(OdaObject):
    def __init__(self, object_id, **kwargs):
        super(Symbol, self).__init__(object_id)
        self.name = kwargs['name']