from oda.libs.odb.structures.oda_object import OdaObject

__author__ = 'davis'

class Parcel(OdaObject):
    def __init__(self, object_id, **kwargs):
        super(Parcel, self).__init__(object_id)
        self.is_code = kwargs['is_code']
        self.start = kwargs['start']
        self.end = kwargs['end']
        self.sample_offsets = []

    def __repr__(self):
        return "Parcel {is_code=%s, start=%s, end=%s>" % (self.is_code, self.start, self.end)
