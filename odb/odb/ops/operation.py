__author__ = 'davis'



class Validator(object):
    def validate(self):
        return True

class Operation(object):
    def __init__(self, validators=[]):
        self.validators = validators

    def validate(self, odb_file):
        self.validate(odb_file)