from django.contrib.contenttypes.models import ContentType
from rest_framework import viewsets
from rest_framework.response import Response
from odaweb.disassembler import Disassembler, analyzerFactory
from odaweb.models import OdaMaster, Comment, BinaryDisassemblySuperChunk
from rest.serializers import OdaMasterSerializer, CommentSerializer, SectionSerializer, StringSerializer, SymbolSerializer


class OdaMasterViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = OdaMaster.objects.all()
    serializer_class = OdaMasterSerializer

class CommentViewSet(viewsets.ModelViewSet):
    #queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    model = Comment

    def get_queryset(self):
        oda = OdaMaster.objects.get(short_name=self.request.QUERY_PARAMS.get('short_name'),
                                  revision=self.request.QUERY_PARAMS.get('revision'))

        return Comment.get_for_binary(oda.binary)


class SectionsViewSet(viewsets.GenericViewSet):
    serializer_class = SectionSerializer

    def list(self, request):
        oda = OdaMaster.objects.get(short_name=request.QUERY_PARAMS.get('short_name'),
                                  revision=request.QUERY_PARAMS.get('revision'))
        d = Disassembler(oda.binary)
        section_info = d.get_loadable_sections()
        serializer = self.get_serializer(section_info.code_sections, many=True)
        return Response(serializer.data)

class StringsViewSet(viewsets.GenericViewSet):
    serializer_class = StringSerializer

    def list(self, request):
        oda = OdaMaster.objects.get(short_name=request.QUERY_PARAMS.get('short_name'),
                                    revision=request.QUERY_PARAMS.get('revision'))

        binary = oda.binary
        dasm = Disassembler(binary)
        strings = [{'addr': key, 'string': value} for key, value in dasm.strings().items()]
        serializer = self.get_serializer(strings, many=True)
        return Response(serializer.data)

class SymbolsViewSet(viewsets.GenericViewSet):
    serializer_class = SymbolSerializer

    def list(self, request):
        oda = OdaMaster.objects.get(short_name=request.QUERY_PARAMS.get('short_name'),
                                    revision=request.QUERY_PARAMS.get('revision'))

        binary = oda.binary
        dasm = Disassembler(binary)

        ctype = ContentType.objects.get_for_model(binary)

        superchunks = BinaryDisassemblySuperChunk.objects.filter(content_type=ctype.id, object_id= binary.id)[:]

        architecture = binary.options.architecture
        analyzer = analyzerFactory(architecture)
        analyzer.analyze(dasm, superchunks)

        #syms = render_to_string('symbols.djhtml', {
        #    'symbols' : sorted(analyzer.functions.values(), key=lambda t: t.offset)
        #})

        serializer = self.get_serializer(analyzer.functions.values(), many=True)
        return Response(serializer.data)



