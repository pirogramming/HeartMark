from django.contrib import admin

from .models import Friendship, Invitation


@admin.register(Friendship)
class FriendshipAdmin(admin.ModelAdmin):
    list_display = ("user1", "user2", "created_at")
    search_fields = ("user1__username", "user2__username")
    date_hierarchy = "created_at"


@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    list_display = ("inviter", "invitee", "status", "code", "created_at", "responded_at")
    list_filter = ("status", "created_at")
    search_fields = ("inviter__username", "invitee__username", "code")
    readonly_fields = ("code", "created_at", "updated_at", "responded_at")
