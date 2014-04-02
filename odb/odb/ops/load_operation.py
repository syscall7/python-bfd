from odb.bfd import ofd
import logging
from odb.structures.section import Section
from odb.structures.symbol import Symbol

logger = logging.getLogger(__name__)

class Options(object):
    def __init__(self):
        self.target = None
        self.architecture = None

class LoadOperation(object):
    def __init__(self, filename):
        self.filename = filename

    def operate(self, odb_file):
        logger.info("Loading %s".format(odb_file))
        filename = self.filename

        class Binary(object):

            def __init__(self):
                self.options = Options()

            @staticmethod
            def file_handle():
                return open(filename)


        o = ofd.Ofd(Binary())

        for section in o.sections:
            odb_file.items[Section].append(odb_file.create_item('Section', {
                'name': section.name
            }))

        for symbol in o.symbols():
            odb_file.items[Symbol].append(odb_file.create_item('Symbol', {
                'name': symbol.name
            }))



