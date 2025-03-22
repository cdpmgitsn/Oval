from django.contrib import admin
from modeltranslation.admin import TranslationAdmin
from .models import *


@admin.register(Subscription_type)
class Subscription_typeAdmin(TranslationAdmin):
    list_display = ('order', 'name', 'is_popular', 'status')
    list_display_links = ('name',)
    list_editable = ('order', 'is_popular', 'status')
    list_filter = ('status',)
    search_fields = ('name',)


@admin.register(Subscription_feature)
class Subscription_featureAdmin(TranslationAdmin):
    list_display = ('order', 'name', 'subscription_type', 'status')
    list_display_links = ('name',)
    list_editable = ('order', 'status')
    list_filter = ('subscription_type', 'status')
    search_fields = ('name',)
    autocomplete_fields = ('subscription_type',)


@admin.register(Subscription_period)
class Subscription_periodAdmin(TranslationAdmin):
    list_display = ('order', 'name', 'discount', 'status')
    list_display_links = ('name',)
    list_editable = ('order', 'status')
    list_filter = ('status',)
    search_fields = ('name',)


@admin.register(Subscription_price)
class Subscription_priceAdmin(admin.ModelAdmin):
    list_display = ('subscription_type', 'subscription_period', 'currency', 'initial_price', 'price')
    list_display_links = ('subscription_type',)
    list_editable = ('price',)
    list_filter = ('subscription_type', 'subscription_period', 'currency')
    search_fields = ('subscription_type__name',)
    autocomplete_fields = ('subscription_type', 'subscription_period', 'currency')


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('trader', 'subscription_type', 'subscription_period', 'currency', 'price', 'payment_type', 'payed', 'date')
    list_display_links = ('trader',)
    list_editable = ('payed',)
    list_filter = ('subscription_type', 'subscription_period', 'currency', 'payed')
    search_fields = ('subscription_type__name',)
    autocomplete_fields = ('trader', 'subscription_type', 'subscription_period', 'currency')
    date_hierarchy = "date"


@admin.register(Subscription_update)
class Subscription_updateAdmin(admin.ModelAdmin):
    list_display = ('trader', 'subscription_type', 'update_type', 'days', 'date')
    list_display_links = ('trader',)
    list_filter = ('subscription_type', 'update_type')
    search_fields = ('update_type',)
    autocomplete_fields = ('trader', 'subscription_type')
    date_hierarchy = "date"
