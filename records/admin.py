from django.contrib import admin

from .models import Record


@admin.register(Record)
class RecordAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "weather", "place_name", "created_at")
    list_filter = ("weather", "created_at")
    search_fields = ("user__username", "content", "place_name")
