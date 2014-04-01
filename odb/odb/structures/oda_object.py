__author__ = 'davis'


class OdaObject(object):
    def __init__(self, object_id):
        self.object_id = object_id

import pkgutil
modules = pkgutil.iter_modules(path=["odb.structures"])
for loader, mod_name, ispkg in modules:
    print mod_name