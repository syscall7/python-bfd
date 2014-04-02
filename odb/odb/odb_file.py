from odb.structures.function import Function

__author__ = 'davis'


class OdaObjectFactory(object):
    def __init__(self, oda_file):
        self.oda_file = oda_file

    def create(self, type_name, parameters):
        if type_name == 'Function':
            return Function(self.oda_file.get_object_id(), **parameters)
        raise Exception(object + ' Not Found')


class OdbFile(object):
    def __init__(self):

        self.object_id = 0
        self.factory = OdaObjectFactory(self)

        self.items = {
            Function: []
        }

    def create_item(self, type_name, parameters):
        return self.factory.create(type_name, parameters)

    def insert_item(self, item):
        self.items[item.__class__].append(item)

    def remove_item(self, item):
        self.items[item.__class__].remove(item)

    def modify_item(self, item):
        for n, i in enumerate(self.items[item.__class__]):
            if n == item:
                self.items[item.__class__][i] = item
                break

    def get_object_id(self):
        self.object_id += 1
        return self.object_id


def scan():
    import pkgutil
    import sys

    modules = pkgutil.iter_modules(path=["odb/structures"])
    for loader, mod_name, ispkg in modules:
        loader.find_module(mod_name).load_module(mod_name)

    [x for x in sys.modules.iterkeys() if x.startswith('odb')]
