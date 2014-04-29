from odb.structures.oda_object import OdaObject

__author__ = 'davis'


class DataString(OdaObject):
    def __init__(self, object_id, **kwargs):
        super(DataString, self).__init__(object_id)
        self.value = kwargs['value']
        self.addr = kwargs['addr']