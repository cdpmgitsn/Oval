from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from modeltranslation.admin import TranslationAdmin
from .models import *


@admin.register(About)
class AboutAdmin(admin.ModelAdmin):
    list_display = ('name', 'logo_url', 'profile_url', 'bot_url_')
    list_display_links = ('name',)
    search_fields = ('name',)

    def logo_url(self, obj: About):
        url = obj.logo.url
        return format_html("<a href=\"{}\">Логотип</a>", url)

    def profile_url(self, obj: About):
        url = obj.profile_icon.url
        return format_html("<a href=\"{}\">Иконка профиля</a>", url)

    def bot_url_(self, obj: About):
        url = obj.bot_url
        return format_html("<a href=\"{}\">Ссылка бота</a>", url)
    
    logo_url.short_description = "Логотип"
    profile_url.short_description = "Иконка профиля"
    bot_url_.short_description = "Ссылка бота"


@admin.register(Tex_work)
class Tex_workAdmin(TranslationAdmin):
    list_display = ('order', 'name', 'status')
    list_display_links = ('name',)
    list_editable = ('order', 'status')
    list_filter = ('status',)
    search_fields = ('name',)


@admin.register(Explanation)
class ExplanationAdmin(TranslationAdmin):
    list_display = ('explanation_type', 'status')
    list_display_links = ('explanation_type',)
    list_editable = ('status',)
    list_filter = ('explanation_type',)
    search_fields = ('description',)
