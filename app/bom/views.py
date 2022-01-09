from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from bom.models import Assembly
from bom.serializers import FileUploadSerializer, AssemblySerializer
from bom.services import save_to_db, validate_file


class FileValidateAPIView(generics.GenericAPIView):
    serializer_class = FileUploadSerializer

    @extend_schema(
        request=FileUploadSerializer,
        responses={204: str},
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        file = serializer.validated_data['file']
        results = validate_file(file)
        if results:
            return Response(status=status.HTTP_400_BAD_REQUEST, data=results)
        return Response(status=status.HTTP_204_NO_CONTENT, data="Validation successful")


class FileUploadAPIView(generics.GenericAPIView):
    serializer_class = FileUploadSerializer
    @extend_schema(
        request=FileUploadSerializer,
        responses={204: str},
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        file = serializer.validated_data['file']
        save_to_db(file)
        return Response(status=status.HTTP_204_NO_CONTENT, data="Uploaded successfully")


class ItemDetailsAPIView(generics.RetrieveAPIView):
    def get_object(self):
        return get_object_or_404(Assembly, id=self.kwargs.get('id', None))

    def get(self, request, *args, **kwargs):
        tree = Assembly.dump_bulk(self.get_object(), keep_ids=False)
        return Response(tree)


class ItemListAPIView(generics.ListAPIView):
    serializer_class = AssemblySerializer
    queryset = Assembly.objects.select_related('component').filter(depth=1)
