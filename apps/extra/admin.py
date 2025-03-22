from django.contrib import admin
from .models import *


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('document_type',)
    list_display_links = ('document_type',)
    list_filter = ('document_type',)
