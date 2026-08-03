from django.contrib import admin

from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "display_name", "character_id", "onboarding_completed", "updated_at")
    search_fields = ("user__username", "display_name")
    list_filter = ("onboarding_completed", "character_id")
