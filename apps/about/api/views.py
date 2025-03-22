from django.shortcuts import render
from rest_framework import viewsets
from django.db.models import Q
from .serializers import *


class AboutViewSet(viewsets.ModelViewSet):

    serializer_class = AboutSerializer

    def get_queryset(self):

        objs = About.objects.all()

        url_data = self.request.GET

        if url_data:
            if 'type' in url_data and url_data['type']:
                if url_data['type'] == 'get_by_id':
                    item_id = url_data['id']
                    objs = objs.filter(id=int(item_id))

        return objs


class Tex_workViewSet(viewsets.ModelViewSet):

    serializer_class = Tex_workSerializer

    def get_queryset(self):

        objs = Tex_work.objects.all()

        url_data = self.request.GET

        if url_data:
            if 'type' in url_data and url_data['type']:
                if url_data['type'] == 'get_by_id':
                    item_id = url_data['id']
                    objs = objs.filter(id=int(item_id))
                
                elif url_data['type'] == 'get_by_name':
                    name = url_data['name']
                    objs = objs.filter(
                        Q(name_ru=name)
                        |
                        Q(name_uz=name)
                        |
                        Q(name_en=name)
                        |
                        Q(name_de=name)
                        |
                        Q(name_hi=name)
                    )

        return objs


class ExplanationViewSet(viewsets.ModelViewSet):

    serializer_class = ExplanationSerializer

    def get_queryset(self):

        objs = Explanation.objects.all()

        url_data = self.request.GET

        if url_data:
            if 'type' in url_data and url_data['type']:
                if url_data['type'] == 'get_by_id':
                    item_id = url_data['id']
                    objs = objs.filter(id=int(item_id))
                
                elif url_data['type'] == 'get_by_name':
                    name = url_data['name']
                    objs = objs.filter(explanation_type=name)

        return objs
