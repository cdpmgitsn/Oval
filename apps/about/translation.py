from modeltranslation.translator import register, TranslationOptions
from .models import *


@register(Tex_work)
class Tex_workTranslationOptions(TranslationOptions):
    fields = ('name', 'description')


@register(Explanation)
class ExplanationTranslationOptions(TranslationOptions):
    fields = ('description',)
