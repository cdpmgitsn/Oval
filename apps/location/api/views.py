from django.shortcuts import render
from rest_framework import viewsets
from django.db.models import Q
from .serializers import *
from .pagination import *


class CountryViewSet(viewsets.ModelViewSet):

    serializer_class = CountrySerializer
    pagination_class = CountryPagination

    def get_queryset(self):

        objs = Country.objects.all()

        url_data = self.request.GET

        if url_data:
            if 'type' in url_data and url_data['type']:
                if url_data['type'] == 'get_by_id':
                    item_id = url_data['id']
                    objs = objs.filter(id=int(item_id))

        return objs


class CityViewSet(viewsets.ModelViewSet):

    serializer_class = CitySerializer
    pagination_class = CityPagination

    def get_queryset(self):

        objs = City.objects.all()

        url_data = self.request.GET

        if url_data:
            if 'type' in url_data and url_data['type']:
                if url_data['type'] == 'get_by_id':
                    item_id = url_data['id']
                    objs = objs.filter(id=int(item_id))
                
                elif url_data['type'] == 'get_by_country':
                    country_id = url_data['country_id']
                    objs = objs.filter(country_id=country_id)
                
                elif url_data['type'] == 'get_by_name':
                    name = url_data['name']
                    objs = objs.filter(
                        Q(name_en=name)
                        |
                        Q(name_ru=name)
                        |
                        Q(name_uz=name)
                        |
                        Q(name_de=name)
                        |
                        Q(name_hi=name)
                    )
                
                elif url_data['type'] == 'get_for_bot':
                    objs = objs.filter(use_in_bot=True)

        return objs
