from oda.libs.odb.structures.oda_object import OdaObject

__author__ = 'davis'

class Section(OdaObject):
    def __init__(self, object_id, name, size, vma, flags):
        super(Section, self).__init__(object_id)
        self.name = name
        self.size = size
        self.vma = vma
        self.flags = flags

    def is_loadable(self):
        names = [f.name for f in self.flags]
        return set(['SEC_LOAD']).issubset(names)