from odb.structures.oda_object import OdaObject

__author__ = 'davis'


class Function(OdaObject):
    def __init__(self, object_id, **kwargs):
        super(Function, self).__init__(object_id)
        self.name = kwargs['name']
        self.offset = kwargs['offset']
        self.xrefs = kwargs.get('xrefs', [])
        self.type = kwargs['type']