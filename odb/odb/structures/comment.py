from odb.structures.oda_object import OdaObject

__author__ = 'davis'

class Comment(OdaObject):
    def __init__(self, **kwargs):
        self.offset = kwargs['offset']
        self.comment = kwargs['comment']

