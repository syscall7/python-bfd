import bfd

from oda.libs.odb.bfd.analyzer import analyzer_factory
from oda.libs.odb.structures.parcel import Parcel, ParcelList
from oda.libs.odb.ops.split_parcel_operation import SplitParcelOperation
from oda.libs.odb.ops.active_scan_operation import ActiveScanOperation
from oda.libs.odb.ops.create_function_operation import CreateFunctionOperation, EditFunctionOperation, DeleteFunctionOperation
from ofd import UNKNOWN_ARCH

from oda.libs.odb.structures.comment import Comment
from oda.libs.odb.structures.data_string import DataString
from oda.libs.odb.structures.branch import Branch
from oda.libs.odb.structures.function import Function
from oda.libs.odb.structures.parcel import Parcel
from oda.libs.odb.structures.section import Section
from oda.libs.odb.structures.symbol import Symbol
from oda.libs.odb.structures.label import Label

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
    analyzer = analyzer_factory(platform, None)
    if analyzer == None:
        analyzer = analyzer_factory('defaultAnalyzer', None)

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

def get_platform_options2(platform):
    analyzer = analyzer_factory(platform, None)
    if analyzer == None:
        analyzer = analyzer_factory('defaultAnalyzer', None)

    return [{
        'name': x[0],
        'desc': x[1],
        'type': x[2],
        'values': x[3]
    } for x in analyzer.options]

class Disassembler(object):
    def __init__(self, odb_file):
        self.odb_file = odb_file
        architecture = self.odb_file.get_binary().options.architecture
        self.analyzer = analyzer_factory(architecture, odb_file)

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
        parcels = ParcelList(self.odb_file.get_structure_list(Parcel))
        p = parcels.find_parcel_by_vma(vma)
        if not p.is_code:
            raise Exception("Cannot make data on non-code parcel")
        self.odb_file.execute(SplitParcelOperation(vma))

    def make_code(self, vma):
        parcels = ParcelList(self.odb_file.get_structure_list(Parcel))
        p = parcels.find_parcel_by_vma(vma)
        if p.is_code:
            raise Exception("Cannot make code on a code parcel")
        self.odb_file.execute(ActiveScanOperation(vma))

    def make_function(self, vma, name, args, retval):
        self.odb_file.execute(CreateFunctionOperation(vma, name, args, retval))

    def edit_function(self, vma, name, args, retval):
        self.odb_file.execute(EditFunctionOperation(vma, name, args, retval))

    def delete_function(self, vma):
        self.odb_file.execute(DeleteFunctionOperation(vma))

    def analyze(self, start, lines, logical):

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
        dus = self.analyzer.analyze(parcels, start=start, maxUnits=lines)
        sorted_du = dus.values()
        sorted_du.sort(key=lambda x: x.offset, reverse=False)
        return sorted_du

    def unused_get_text_listing_via_dus(self):
        dus = self.analyze(0, self.total_lines(), True)
        functions = {f.offset: f for f in self.odb_file.get_structure_list(Function)}
        labels = {l.offset:l.label for l in self.odb_file.get_structure_list(Label)}
        listing = ''
        # calculate the maximum width needed to fit the longest raw bytes
        max_raw_width = reduce(lambda x, y: x if x > len(y.rawBytes) else len(y.rawBytes), dus, 0)
        max_sec_width = reduce(lambda x, y: x if x > len(y.section_name) else len(y.section_name), dus, 0)
        for du in dus:

            if du.offset in functions.keys():
                listing += '%s            %s ; ======================== FUNCTION =========================\n' % (' '*max_sec_width, ' '*max_raw_width)
                listing += '%s            %s %s\n' %  (' '*max_sec_width, ' '*max_raw_width, functions[du.offset].name)
            if du.offset in labels.keys():
                listing += '%s:0x%08x      %s:\n' % (du.section_name.rjust(max_sec_width, ' '),
                                                  du.offset,
                                                  labels[du.offset])
            target = ''
            if du.isTargetAddrValid:
                target = labels[du.targetAddr] if du.targetAddr in labels.keys() else '0x%08x' % du.targetAddr

            listing += '%s:0x%08x %s %s %s\n' % (du.section_name.rjust(max_sec_width, ' '),
                                              du.offset,
                                              du.rawBytes.ljust(max_raw_width, ' '),
                                              du.instStr,
                                              target)
        return listing

    def get_text_listing(self):
        parcels = ParcelList(self.odb_file.get_structure_list(Parcel))
        return self.analyzer.get_text_listing(parcels)


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
        return self.analyzer.find(pattern)

