__author__ = 'davis'


class OdbFile(object):
    def __init__(self):
        self.object_id = 0
        self.functions = []

    def get_object_id(self):
        self.object_id += 1
        return self.object_id