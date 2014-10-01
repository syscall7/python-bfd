import bfd

from oda.libs.odb.bfd.analyzer import analyzer_factory
from oda.libs.odb.structures.parcel import Parcel, ParcelList
from oda.libs.odb.ops.split_parcel_operation import SplitParcelOperation
from oda.libs.odb.ops.active_scan_operation import ActiveScanOperation
from ofd import UNKNOWN_ARCH

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

    def total_lines(self):
        parcels = ParcelList(self.odb_file.get_structure_list(Parcel))
        return parcels.sum_ldas()

    def vma_to_lda(self, vma):
        parcels = ParcelList(self.odb_file.get_structure_list(Parcel))
        return parcels.vma_to_lda(vma)

    def lda_to_vma(self, lda):
        parcels = ParcelList(self.odb_file.get_structure_list(Parcel))
        return parcels.lda_to_vma(lda)

    def make_data(self, vma):
        self.odb_file.execute(SplitParcelOperation(vma))

    def make_code(self, vma):
        self.odb_file.execute(ActiveScanOperation(vma))

    def analyze(self, start, lines, logical):

        architecture = self.odb_file.get_binary().options.architecture
        analyzer = analyzer_factory(architecture)

        parcels = ParcelList(self.odb_file.get_structure_list(Parcel))

        # if we are analyzing based on lda, first convert to vma
        if logical:
            start = parcels.lda_to_vma(start)
            if start is None:
                # TODO: Throw exception here?
                return []

        # if we are going backwards
        if lines < 0:
            # Note: Use start+1 to include start in the returned disassembly
            lda_end = parcels.vma_to_lda(start) + 1
            lda_start = lda_end + lines if lda_end > lines else 0
            start = parcels.lda_to_vma(lda_start)
            lines = abs(lines)

        parcels = [p for p in parcels if p.vma_end > start]
        analyzer.analyze(self.odb_file, parcels, start=start, maxUnits=lines)
        sorted_du = analyzer.displayUnits.values()
        sorted_du.sort(key=lambda x: x.offset, reverse=False)
        return sorted_du

    @staticmethod
    def guess_bfd_arch(filename):
        ''' Returns our best guess at target (file format) and architecture '''

        # use defaults these default when we can't detect the arch/target
        arch = UNKNOWN_ARCH
        target = 'binary'
        try:
            target_archs = bfd.guess_target_arch(filename)

            # TODO: Present these options to the user and let them pick from all matching target/archs

            # for each detected target/arch
            for (t, a) in target_archs:

                # we'll set the target here even in cases where we cannot detect arch (i.e., ihex, srec)
                target = t
                if a != "UNKNOWN!":
                    arch = a
                    break

        except bfd.BfdFileFormatException, e:
            pass
        except Exception, e:
            pass

        return arch, target

    def find(self, pattern):
        architecture = self.odb_file.get_binary().options.architecture
        analyzer = analyzer_factory(architecture)
        return analyzer.find(self.odb_file, pattern)

