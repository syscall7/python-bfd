from rest_framework import viewsets
from rest_framework.response import Response
from odaweb.disassembler import Disassembler
from odaweb.models import OdaMaster, Comment
from rest.serializers import OdaMasterSerializer, CommentSerializer, SectionSerializer, BinarySuperChunkSerializer


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

class SuperChunksViewSet(viewsets.GenericViewSet):
    serializer_class = BinarySuperChunkSerializer

    def list(self, request):
        oda = OdaMaster.objects.get(short_name=request.QUERY_PARAMS.get('short_name'),
                                  revision=request.QUERY_PARAMS.get('revision'))
        d = Disassembler(oda.binary)
        superchunks = d.get_all_superchunks()
        serializer = self.get_serializer(superchunks, many=True)
        return Response(serializer.data)

