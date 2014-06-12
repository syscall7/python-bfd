__author__ = 'davis'

class OdaObject(object):

    def __init__(self, object_id):
        self.object_id = object_id

    @property
    def item_type(self):
        return self.__class__.__name__

import pkgutil
modules = pkgutil.iter_modules(path=["odb.structures"])
for loader, mod_name, ispkg in modules:
    print mod_name