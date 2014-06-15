from oda.libs.odb.structures.oda_object import OdaObject

__author__ = 'davis'


class DataString(OdaObject):
    def __init__(self, object_id, value, addr):
        super(DataString, self).__init__(object_id)
        self.value = value
        self.addr = addr