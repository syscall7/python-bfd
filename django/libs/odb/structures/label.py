from odb.odb.structures.oda_object import OdaObject

__author__ = 'davis'

class Label(OdaObject):
    def __init__(self, object_id, **kwargs):
        super(OdaObject, self).__init__(object_id)

        self.label = kwargs['label']
