import bfd

from oda.libs.odb.bfd.analyzer import analyzer_factory
from oda.libs.odb.structures.parcel import Parcel

__author__ = 'davis'


def get_supported_archs():
    '''Return a list of all architectures supported
    '''
    supportedArchs = bfd.list_architectures()

    # Remove Problem archs
    problemArchs = ['MicroBlaze',
                    'i960:ka_sa',
                    'i960:kb_sb',
                    'r800',
                    'moxie',
    ]

    for arch in problemArchs:
        supportedArchs.remove(arch)

    return supportedArchs


def get_supported_endians():
    endians = {
        'DEFAULT': bfd.ENDIAN_DEFAULT,
        'LITTLE': bfd.ENDIAN_LITTLE,
        'BIG': bfd.ENDIAN_BIG
    }

    return endians

def get_platform_options(platform):
    djhtmlOpts = []
    analyzer = analyzer_factory(platform)
    if analyzer == None:
        analyzer = analyzer_factory('defaultAnalyzer')

    #print "Checking if"
    if analyzer.options:
        #print "ANalyzer",analyzer.options
        for opt in analyzer.options:
        # Form the name of the widget by stripping out options
            widgetName = opt[0].replace(' ', '')
            widgetType = ''
            if opt[2] == 'CHOICE' or opt[2] == 'BOOL':
                widgetType = 'select'
                widgetName += widgetType

            # Build the Modal
            djhtmlOpts.append((widgetName,widgetType) + opt)
            #print 'DHTML',djhtmlOpts
    return djhtmlOpts

class Disassembler(object):
    def __init__(self, odb_file):
        self.odb_file = odb_file

    def analyze(self, start, lines):

        architecture = self.odb_file.get_binary().options.architecture
        analyzer = analyzer_factory(architecture)

        parcels = self.odb_file.get_structure_list(Parcel)

        if lines >= 0:
            parcels = [p for p in parcels if p.end > start] #BinaryParcel.objects.filter(content_type=ctype.id, object_id= self.binary.id, end__gte = start)[:]
        else:
            parcels = [p for p in parcels if p.start < start]

        analyzer.analyze(self.odb_file, parcels, start=start, maxUnits=lines)
        sorted_du = analyzer.displayUnits.values()
        sorted_du.sort(key=lambda x: x.offset, reverse=False)
        return sorted_du
