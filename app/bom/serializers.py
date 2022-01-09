from rest_framework import serializers

from bom.models import Assembly, Component


class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()

    class Meta:
        fields = ('file',)


class ComponentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Component
        exclude = ('id',)


class AssemblySerializer(serializers.ModelSerializer):
    component = ComponentSerializer()

    class Meta:
        model = Assembly
        exclude = ('numchild', 'path',)
