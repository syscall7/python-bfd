from odb.structures.oda_object import OdaObject

__author__ = 'davis'

class Section(OdaObject):
    def __init__(self, object_id, **kwargs):
        super(Section, self).__init__(object_id)
        self.name = kwargs['name']