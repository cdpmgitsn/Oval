from django.contrib import admin
from modeltranslation.admin import TranslationAdmin
from .models import *


@admin.register(Country)
class CountryAdmin(TranslationAdmin):
    list_display = ('name', 'code')
    list_display_links = ('name',)
    search_fields = ('name',)


@admin.register(City)
class CityAdmin(TranslationAdmin):
    list_display = ('name', 'code', 'country', 'use_in_bot')
    list_display_links = ('name',)
    list_filter = ('country', 'use_in_bot')
    list_editable = ('use_in_bot',)
    search_fields = ('name',)
    autocomplete_fields = ('country',)
