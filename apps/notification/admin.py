from django.contrib import admin
from .models import *


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('trader', '_type', 'status', 'date')
    list_display_links = ('trader',)
    list_filter = ('_type', 'status')
    search_fields = ('trader__username',)
    autocomplete_fields = ('trader',)
    date_hierarchy = "date"
