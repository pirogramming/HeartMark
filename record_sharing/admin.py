from django.contrib import admin

from .models import RecordShare, RecordShareComment


@admin.register(RecordShare)
class RecordShareAdmin(admin.ModelAdmin):
    list_display = ("record", "sender", "receiver", "share_location", "created_at", "revoked_at")
    # 취소된 것만 보기 / 장소 공개된 것만 보기 같은 필터
    list_filter = ("share_location", "created_at", "revoked_at")
    search_fields = ("sender__username", "receiver__username")
    # 자동으로 채워지는 값이라 admin에서 손으로 못 고치게 잠근다.
    readonly_fields = ("created_at",)
    # FK 를 드롭다운 대신 검색창으로. 기록·사용자가 많아져도 admin 이 느려지지 않는다.
    raw_id_fields = ("record", "sender", "receiver")


@admin.register(RecordShareComment)
class RecordShareCommentAdmin(admin.ModelAdmin):
    list_display = ("share", "author", "content", "created_at")
    search_fields = ("author__username", "content")
    raw_id_fields = ("share", "author")
