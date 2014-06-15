from oda.libs.odb.structures.oda_object import OdaObject

__author__ = 'davis'

class Symbol(OdaObject):
    def __init__(self, object_id, name, sym_type, offset, xrefs, base, value):
        super(Symbol, self).__init__(object_id)
        self.name = name
        self.type = sym_type
        self.offset = offset
        self.xrefs = set(xrefs)
        self.base = base
        self.value = value
