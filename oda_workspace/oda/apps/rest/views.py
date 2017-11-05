import logging
from django.core.urlresolvers import reverse
from django.http import HttpResponseNotAllowed

from rest_framework import viewsets, status
#from rest_framework.decorators import action, link, api_view
from rest_framework.decorators import api_view, detail_route
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from oda.apps.odaweb.models import OdaMaster, Share
from oda.apps.odaweb.utils import id_generator

from oda.apps.rest.serializers import OdaMasterSerializer, SectionSerializer, StringSerializer, DisplayUnitSerializer, \
    FindResultsSerializer, CommentSerializer, FunctionSerializer, DataStringSerializer, SymbolSerializer, \
    LabelSerializer, ParcelSerializer, CStructSerializer, CStructFieldSerializer
from oda.libs.cuckoo import cuckoo
from oda.libs.cuckoo.cuckoo import CuckooJob
from oda.libs.odb.bfd.disassembler import Disassembler, get_supported_archs, get_supported_endians, get_platform_options2
from oda.libs.odb.odb_file import OdbFile
from oda.libs.odb.binaries import BinaryString
from oda.libs.odb.ops.load_operation import LoadOperation
from oda.libs.odb.ops.add_struct_operation import AddStructOperation
from oda.libs.odb.ops.modify_settings import ModifySettingsFactory
from oda.libs.odb.ops.passive_scan_operation import PassiveScanOperation
from oda.libs.odb.structures.comment import Comment
from oda.libs.odb.structures.data_string import DataString
from oda.libs.odb.structures.function import Function
from oda.libs.odb.structures.label import Label
from oda.libs.odb.structures.section import Section
from oda.libs.odb.structures.symbol import Symbol
from oda.libs.odb.structures.parcel import Parcel, ParcelList
from oda.libs.odb.structures.types import BuiltInTypeFactory, BuiltInTypeNames, BuiltInTypes
from oda.libs.odb import structures
from oda.libs.odb.ops.add_operation import AddOperation
from oda.libs.odb.structures.c_struct import CStruct, BuiltinField, CStructField, CStructObject
from oda.libs.odb.bfd.analyzers.branch import BranchGraphView

logger = logging.getLogger(__name__)


class OdaMasterViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = OdaMaster.objects.all()
    serializer_class = OdaMasterSerializer
    paginate_by = 10


class OdaStructureViewSet(viewsets.GenericViewSet):
    def __init__(self, **kwargs):
        super(OdaStructureViewSet, self).__init__(**kwargs)
        self.odb_file = None

    def get_structure_list(self):
        return self.odb_file.get_structure_list(self.structure)

    def map_item(self, item):
        return item

    def list(self, request, format=None):
        short_name = request.query_params.get('short_name', None)
        revision = request.query_params.get('revision', None)

        oda = OdaMaster.objects.get(short_name=short_name, revision=revision)
        self.odb_file = oda.odb_file

        structure_list = self.get_structure_list()
        mapped_structure_list = [self.map_item(i) for i in structure_list]
        serializer = self.get_serializer(mapped_structure_list, many=True)
        return Response(serializer.data)


class CommentViewSet(OdaStructureViewSet):
    serializer_class = CommentSerializer
    structure = Comment

    def create(self, request):

        logger.info("Creating comment " + str(request))

        comment = request.data['comment']
        offset = request.data['offset']
        short_name = request.data['short_name']
        revision = request.data['revision']

        oda = OdaMaster.objects.get(short_name=short_name, revision=revision)
        odb_file = oda.odb_file
        item = odb_file.create_item(Comment, {
            'comment': comment,
            'offset': offset
        })

        odb_file.execute(structures.comment.generate_operation(AddOperation, item))

        oda.save()

        serializer = self.get_serializer(item, many=False)
        return Response(serializer.data)

    def destroy(self, request, pk=None):
        oda = OdaMaster.objects.get(short_name=request.data['short_name'], revision=request.data['revision'])
        odb_file = oda.odb_file
        if request.data.get('vma'):
            offset = request.data.get('vma')
            comments = {c.offset: c for c in odb_file.get_structure_list(Comment)}
            if offset in comments:
                odb_file.remove_item(comments[offset])
                oda.save()
                return Response({}, status=status.HTTP_200_OK)

        return Response({'error': ''}, status=status.HTTP_400_BAD_REQUEST)

class FunctionViewSet(OdaStructureViewSet):
    serializer_class = FunctionSerializer
    structure = Function

    def partial_update(self,request,pk):
        oda = OdaMaster.objects.get(short_name=request.data['short_name'], revision=request.data['revision'])

        error = None
        offset = None
        if request.data.get('offset'):
            offset = int(request.data.get('offset'), 0)

        name = None
        if request.data.get('name'):
            name = request.data.get('name')

        args = None
        if request.data.get('args'):
            args = request.data.get('args')

        retval = None
        if request.data.get('retval'):
            retval = request.data.get('retval')

        dasm = Disassembler(oda.odb_file)
        try:
            dasm.edit_function(offset, name, args, retval)
            oda.save()
        except Exception as e:
            error = e.message
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        return Response({
                    'function': name,
                    'error': error
        })

class SectionsViewSet(OdaStructureViewSet):
    serializer_class = SectionSerializer
    structure = Section

    def get_structure_list(self):
        sections = self.odb_file.get_structure_list(Section)
        return filter(lambda s: s.is_loadable(), sections)


class StringsViewSet(OdaStructureViewSet):
    serializer_class = DataStringSerializer
    structure = DataString

    def map_item(self, item):
        return {
            'string': item.value,
            'addr': item.addr
        }


class LabelsViewSet(OdaStructureViewSet):
    serializer_class = LabelSerializer
    structure = Label

class SymbolsViewSet(OdaStructureViewSet):
    serializer_class = SymbolSerializer
    structure = Symbol

    def get_structure_list(self):

        # NOTE: If there are multiple symbols for the same address, we will ignore all but one of them here when
        #       creating this dictionary.
        sym_dict = {
            sym.offset: sym
                for sym in self.odb_file.get_structure_list(Symbol)
                    if (sym.type == 't' or sym.type=='T')
        }

        return sym_dict.values()

class ParcelsViewSet(OdaStructureViewSet):
    serializer_class = ParcelSerializer
    structure = Parcel

    def get_structure_list(self):
        parcels = self.odb_file.get_structure_list(Parcel)
        return sorted(parcels, key=lambda p: p.vma_start)

class BinaryStringViewSet(viewsets.GenericViewSet):
    def partial_update(self, request, pk):
        oda_master = OdaMaster.objects.get(short_name=request.data['short_name'], revision=request.data['revision'])

        previous_odb = oda_master.odb_file

        try:
            odb_file = OdbFile(BinaryString(request.data['binary_string'], previous_odb.get_binary().options.architecture))
            odb_file.execute(LoadOperation())
            odb_file.execute(PassiveScanOperation())
        except (TypeError, UnicodeDecodeError, UnicodeEncodeError):
            return HttpResponseNotAllowed('Invalid hex digits')

        oda_master.odb_file = odb_file
        oda_master.save()

        logger.info("updating...")

        return Response({'binary_string': request.data['binary_string']})


class OptionsViewSet(viewsets.GenericViewSet):
    def partial_update(self,request,pk):
        oda_master = OdaMaster.objects.get(short_name=request.data['short_name'], revision=request.data['revision'])

        arch = request.data.get('options[architecture]')
        base_address = request.data.get('options[base_address]')
        endian = request.data.get('options[endian][name]')
        selected_opts = request.data.getlist('options[selected_opts][]', [])

        logger.info("updating...")

        odb_file = oda_master.odb_file
        odb_file.execute(ModifySettingsFactory.set_values({
            'architecture': arch,
            'base_address': base_address,
            'endian': endian,
            'selected_opts': selected_opts
        }))

        odb_file = OdbFile(odb_file.binary)

        # do not treat all sections as code for raw binary uploads, instead let user interactively disassemble
        odb_file.execute(LoadOperation())
        odb_file.execute(PassiveScanOperation())
        oda_master.odb_file = odb_file
        oda_master.save()

        return Response({'status': 'ok'})




class DisplayUnitsViewSet(viewsets.GenericViewSet):
    serializer_class = DisplayUnitSerializer

    def get_queryset(self):
        pass

    def list(self, request):

        start = 0
        units = 100
        logical = False

        if request.query_params.get('addr'):
            start = int(request.query_params.get('addr'), 0)
        if request.query_params.get('units'):
            units = int(request.query_params.get('units'), 0)
        if request.query_params.get('logical'):
            logical = True # TODO: Check this value for realz

        oda = OdaMaster.objects.get(short_name=request.query_params.get('short_name'),
                                    revision=request.query_params.get('revision'))

        dasm = Disassembler(oda.odb_file)
        dunits = dasm.analyze(start, units, logical)


        logger.debug("DisplayUnitsViewSet: Generate serialized data")
        serializer = self.get_serializer(dunits, many=True)
        serialData = Response(serializer.data)
        logger.debug("DisplayUnitsViewSet: Serial data complete")
        return serialData

    @detail_route()
    def size(self, request, pk):
        oda = OdaMaster.objects.get(short_name=request.query_params.get('short_name'),
                                    revision=request.query_params.get('revision'))

        dasm = Disassembler(oda.odb_file)
        return Response(dasm.total_lines())

    @detail_route()
    def vmaToLda(self, request, pk):
        oda = OdaMaster.objects.get(short_name=request.query_params.get('short_name'),
                                    revision=request.query_params.get('revision'))

        vma = 0
        if request.query_params.get('vma'):
            vma = int(request.query_params.get('vma'), 0)

        dasm = Disassembler(oda.odb_file)
        return Response(dasm.vma_to_lda(vma))

    @detail_route()
    def ldaToVma(self, request, pk):
        oda = OdaMaster.objects.get(short_name=request.query_params.get('short_name'),
                                    revision=request.query_params.get('revision'))

        lda = 0
        if request.query_params.get('lda'):
            lda = int(request.query_params.get('lda'), 0)

        dasm = Disassembler(oda.odb_file)
        return Response(dasm.lda_to_vma(lda))

    @detail_route()
    def makeData(self, request, pk):
        oda = OdaMaster.objects.get(short_name=request.query_params.get('short_name'),
                                    revision=request.query_params.get('revision'))

        error = None
        vma = 0
        if request.query_params.get('vma'):
            vma = int(request.query_params.get('vma'), 0)

        dasm = Disassembler(oda.odb_file)
        try:
            dasm.make_data(vma)
        except Exception as e:
            error = e.message
        oda.save()

        return Response({'error': error})

    @detail_route()
    def makeStruct(self, request, pk):
        oda = OdaMaster.objects.get(short_name=request.query_params.get('short_name'),
                                    revision=request.query_params.get('revision')
                                    )

        error = None
        vma = 0
        if request.query_params.get('vma'):
            vma = int(request.query_params.get('vma'), 0)

        struct_type = str(request.query_params.get('struct_type'))
        variable_name = str(request.query_params.get('variable_name'))

        oda.odb_file.execute(AddStructOperation(vma,struct_type,variable_name))

        oda.save()

        return Response({'error': error})

    @detail_route()
    def makeCode(self, request, pk):
        oda = OdaMaster.objects.get(short_name=request.query_params.get('short_name'),
                                    revision=request.query_params.get('revision'))

        error = None
        vma = 0
        if request.query_params.get('vma'):
            vma = int(request.query_params.get('vma'), 0)

        dasm = Disassembler(oda.odb_file)
        try:
            dasm.make_code(vma)
        except Exception as e:
            error = e.message
        oda.save()

        return Response({'error': error})

    #@action()
    def makeFunction(self, request, pk):
        oda = OdaMaster.objects.get(short_name=request.data.get('short_name'),
                                    revision=request.data.get('revision'))

        error = None
        offset = 0
        if request.data.get('offset'):
            offset = int(request.data.get('offset'), 0)

        name = 'func_%x' % offset
        if request.data.get('name'):
            name = request.data.get('name')

        args = 'unknown'
        if request.data.get('args'):
            args = request.data.get('args')

        retval = 'unknown'
        if request.data.get('retval'):
            retval = request.data.get('retval')

        dasm = Disassembler(oda.odb_file)
        try:
            dasm.make_function(offset, name, args, retval)
            oda.save()
        except Exception as e:
            error = e.message
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        return Response({
                    'function': name,
                    'error': error
        })



class FindViewSet(viewsets.GenericViewSet):
    serializer_class = FindResultsSerializer

    def list(self, request):
        bytes = self.request.query_params.get('bytes', None)
        oda = OdaMaster.objects.get(short_name=request.query_params.get('short_name'),
                                    revision=request.query_params.get('revision'))

        dasm = Disassembler(oda.odb_file)
        results = [{'addr': key, 'section': value} for key, value in
                   sorted(dasm.find(bytes).items(), key=lambda s: s[0])]
        serializer = self.get_serializer(results, many=True)
        return Response(serializer.data)

class CStructFieldsViewSet(OdaStructureViewSet):
    serializer_class = CStructFieldSerializer
    structure = CStructField

    def get_structure_list(self):
        #fields = self.odb_file.get_structure_list(CStructField)

        fields = BuiltInTypes()

        # Include the built in types
        instances = [field() for field in fields]

        # Include c_structs too
        cstructs = self.odb_file.get_structure_list(CStruct)

        return sorted(instances + cstructs, key=lambda s: type(s).__name__)

class CStructsViewSet(OdaStructureViewSet):
    serializer_class = CStructSerializer
    structure = CStruct

    def get_structure_list(self):
        cstructs = self.odb_file.get_structure_list(CStruct)
        return sorted(cstructs, key=lambda s: s.name)

    def create(self, request):

        logger.info("Creating cstruct " + str(request))

        name = request.data['name']
        is_packed = request.data['is_packed']
        short_name = request.data['short_name']
        revision = request.data['revision']

        oda = OdaMaster.objects.get(short_name=short_name, revision=revision)
        odb_file = oda.odb_file
        item = odb_file.create_item(CStruct, {
            'name': name,
            'is_packed': is_packed
        })

        odb_file.execute(structures.c_struct.generate_operation(AddOperation, item))

        oda.save()

        serializer = self.get_serializer(item, many=False)
        return Response(serializer.data)

    @detail_route()
    def modify(self, request, pk):

        logger.info("Modify cstruct " + str(request))

        short_name = request.query_params.get('short_name')
        revision = request.query_params.get('revision')
        field_names = request.query_params.getlist('field_names[]')
        field_types = request.query_params.getlist('field_types[]')


        oda = OdaMaster.objects.get(short_name=short_name, revision=revision)
        struct_list = oda.odb_file.get_structure_list(CStruct)
        item = struct_list[int(pk)]

        # Delete existing fields
        for oldfield in item.fields[:]:
            item.delete_field(oldfield.name)

        # Add new ones
        for i in range(len(field_names)):

            # Check if the field is a built-in type
            builtin = BuiltInTypeFactory(str(field_types[i]))
            if ( builtin != None ):
                item.append_field( BuiltinField(name=str(field_names[i]),type=builtin) )
            else:
                # Check if the field is an existing c_struct
                for struct in struct_list:
                    if struct.name == field_types[i]:
                       item.append_field( CStructField(name=str(field_names[i]),c_struct_obj=struct) )

        oda.save()

        serializer = self.get_serializer(item, many=False)
        return Response(serializer.data)

    def destroy(self, request, pk=None):
        oda = OdaMaster.objects.get(short_name=request.data['short_name'], revision=request.data['revision'])


        struct_list = oda.odb_file.get_structure_list(CStruct)

        if pk:
            item = struct_list[int(pk)]

            # Remove references to the struct in other structs
            for struct in struct_list:
                for field in struct.fields[:]:
                    if field.type == item.name:
                        item.delete_field(field.name)

            # Remove associated struct variables from parcels
            parcels = ParcelList(oda.odb_file.get_structure_list(Parcel))
            dataparcels = [p for p in parcels if not p.is_code]
            for dp in dataparcels:
                for struct in dp.structs:
                    if struct.struct_type == item.name:
                        dp.delete_struct_variable(struct.addr)

            # Delete the struct type
            oda.odb_file.remove_item(item)
            oda.save()

            return Response({}, status=status.HTTP_200_OK)

        return Response({'error': ''}, status=status.HTTP_400_BAD_REQUEST)

    @detail_route()
    def append_field(self, request, pk):

        logger.info("Adding field to cstruct " + str(request))

        short_name = request.query_params.get('short_name')
        revision = request.query_params.get('revision')
        field_name = request.query_params.get('field_name')
        field_type = request.query_params.get('field_type')

        oda = OdaMaster.objects.get(short_name=short_name, revision=revision)
        struct_list = oda.odb_file.get_structure_list(CStruct)
        item = struct_list[int(pk)]

        # Check if the field is a built-in type
        builtin = BuiltInTypeFactory(field_type)
        if ( builtin != None ):
            item.append_field( BuiltinField(name=field_name,type=builtin) )
        else:
            # Check if the field is an existing c_struct
            for struct in struct_list:
                if struct.name == field_type:
                   item.append_field( CStructField(name=field_name,c_struct_obj=struct) )

        oda.save()

        serializer = self.get_serializer(item, many=False)
        return Response(serializer.data)

class SandboxViewSet(viewsets.GenericViewSet):

    #@action()
    def submit(self, request, pk):
        # disable for now
        return Response(status=status.HTTP_404_NOT_FOUND)

        short_name = request.data.get('short_name')
        revision = request.data.get('revision')
        oda = OdaMaster.objects.get(short_name= short_name, revision = revision)
        job = cuckoo.submit_job(oda)
        return Response({
            "status": job.status()
        })

    @detail_route()
    def status(self,request, pk):
        # disable for now
        return Response(status=status.HTTP_404_NOT_FOUND)

        short_name = request.query_params.get('short_name')
        revision = request.query_params.get('revision')
        oda = OdaMaster.objects.get(short_name= short_name, revision = revision)
        job = cuckoo.CuckooJob(oda)
        return Response({
            "status": job.status(),
        })

    @detail_route()
    def report(self,request, pk):
        # disable for now
        return Response(None)

        short_name = request.query_params.get('short_name')
        revision = request.query_params.get('revision')
        oda = OdaMaster.objects.get(short_name= short_name, revision = revision)
        try:
            job = cuckoo.CuckooJob(oda)
            response = Response(job.report())
        except:
            response = Response(None)

        return response

@api_view(['GET'])
def load_odb(request):
    short_name = request.query_params.get('short_name')
    revision = request.query_params.get('revision', 0)
    oda = OdaMaster.objects.get(short_name= short_name, revision = revision)
    odb_file = oda.odb_file

    sym_dict = {
        sym.offset: sym
            for sym in odb_file.get_structure_list(Symbol)
                if (sym.type == 't' or sym.type=='T')
    }

    symbols = sym_dict.values()

    parcels = sorted(odb_file.get_structure_list(Parcel), key=lambda p: p.vma_start)

    sections = filter(lambda s: s.is_loadable(), odb_file.get_structure_list(Section))

    dasm = Disassembler(odb_file)
    size = dasm.total_lines()

    fields = BuiltInTypes()

    # Include the built in types
    instances = [field() for field in fields]

    # Include c_structs too
    cstructs = odb_file.get_structure_list(CStruct)
    c_structs = sorted(instances + cstructs, key=lambda s: type(s).__name__)

    return Response({
        'functions': [FunctionSerializer(x).data for x in odb_file.get_structure_list(Function)],
        'labels': [LabelSerializer(x).data for x in odb_file.get_structure_list(Label)],
        'sections': SectionSerializer(sections, many=True).data,
        'parcels': [ParcelSerializer(x).data for x in parcels],
        'comments': [CommentSerializer(x).data for x in odb_file.get_structure_list(Comment)],
        'symbols': [SymbolSerializer(x).data for x in symbols],
        'strings': [DataStringSerializer({
            'string': x.value,
            'addr': x.addr
        }).data for x in odb_file.get_structure_list(DataString)],
        "structTypes": [CStructSerializer(x).data for x in odb_file.get_structure_list(CStruct)],
        "structFields": [CStructFieldSerializer(x).data for x in c_structs],
        "displayUnits": {
            "size": size
        }
    })

@api_view(['GET'])
def graph(request):
    short_name = request.query_params.get('short_name')
    revision = request.query_params.get('revision', 0)
    oda = OdaMaster.objects.get(short_name= short_name, revision = revision)
    odb_file = oda.odb_file
    vma = int(request.query_params.get('addr'))
    try:
        bgv = BranchGraphView(odb_file, vma)

        serialized_nodes = []
        for n in bgv.nodes:
            sn = n
            sn['instructions'] = DisplayUnitSerializer(n['instructions'], many=True).data
            serialized_nodes.append(sn)
        return Response({
            'nodes': serialized_nodes,
            'links': bgv.links,
        })
    except Exception, e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ShareView(APIView):
    def post(self, request):
        short_name = request.data.get('short_name')
        revision = request.data.get('revision')
        oda = OdaMaster.objects.get(short_name= short_name, revision = revision)
        share = Share(odaMaster = oda, name = id_generator(16))
        share.save()
        return Response({
            'shareName': share.name,
            'shareUrl': reverse('connect', args=(share.name,))
        })


class DisassemblerViewSet(viewsets.GenericViewSet):
    @detail_route()
    def architectures(self, request, pk):
        return Response({
            'architectures': get_supported_archs(),
            'endians': [{
                'name': x,
                'intValue': y
            } for x,y in get_supported_endians().items()]
        })


    @detail_route()
    def options(self, request, pk):
        arch = request.query_params.get('arch', 'i386:x86-64')
        return Response({
            'arch': arch,
            'options': get_platform_options2(arch)
        })
