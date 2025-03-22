from modeltranslation.translator import register, TranslationOptions
from .models import *


@register(Country)
class CountryTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(City)
class CityTranslationOptions(TranslationOptions):
    fields = ('name',)
