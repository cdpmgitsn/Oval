from modeltranslation.translator import register, TranslationOptions
from .models import *


@register(Subscription_type)
class Subscription_typeTranslationOptions(TranslationOptions):
    fields = ('description',)


@register(Subscription_feature)
class Subscription_featureTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(Subscription_period)
class Subscription_periodTranslationOptions(TranslationOptions):
    fields = ('name',)
