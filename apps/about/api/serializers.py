from rest_framework import serializers
from apps.about.models import *


class AboutSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = About
        fields = ['name', 'logo']


class Tex_workSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Tex_work
        fields = [
            'id',
            'order',
            'name_ru',
            'name_uz',
            'name_en',
            'name_de',
            'name_hi',
            'description_ru',
            'description_uz',
            'description_en',
            'description_de',
            'description_hi',
            'poster',
            'status'
        ]


class ExplanationSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Explanation
        fields = [
            'id',
            'explanation_type',
            'description_ru',
            'description_uz',
            'description_en',
            'description_de',
            'description_hi',
            'status'
        ]
