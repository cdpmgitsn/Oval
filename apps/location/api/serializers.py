from rest_framework import serializers
from apps.location.models import *


class CountrySerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Country
        fields = ['id', 'name_en', 'name_ru', 'name_uz', 'name_de', 'name_hi', 'code']


class CitySerializer(serializers.HyperlinkedModelSerializer):

    country = CountrySerializer(read_only=True, many=False)

    class Meta:
        model = City
        fields = ['id', 'country', 'name_en', 'name_ru', 'name_uz', 'name_de', 'name_hi', 'code']
