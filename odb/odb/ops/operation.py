__author__ = 'davis'


class Validator(object):
    def validate(self, odb_file):
        return True


class Operation(object):
    def __init__(self, validators=[]):
        self.validators = validators

    def validate(self, odb_file):
        for validator in self.validators:
            validator.validate(self, odb_file)

    def operate(self, odb_file):
        pass