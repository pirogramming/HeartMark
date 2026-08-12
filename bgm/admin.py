from django.contrib import admin

from .models import BackgroundMusic, RecordBackgroundMusic


@admin.register(BackgroundMusic)
class BackgroundMusicAdmin(admin.ModelAdmin):
    # 음악 목록에서 확인할 항목 설정
    list_display = (
        "id",
        "title",
        "artist",
        "mood_group",
        "is_active",
        "attribution_required",
    )

    # 음악 분위기와 활성화 여부로 필터링
    list_filter = (
        "mood_group",
        "is_active",
        "attribution_required",
    )

    # 제목과 제작자로 검색 가능하게
    search_fields = (
        "title",
        "artist",
    )


@admin.register(RecordBackgroundMusic)
class RecordBackgroundMusicAdmin(admin.ModelAdmin):
    # 기록과 연결된 음악 확인
    list_display = (
        "id",
        "record",
        "music",
        "created_at",
    )