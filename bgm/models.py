from django.db import models

from records.models import Record


class BackgroundMusic(models.Model):
    # 음악 분위기 그룹 저장함.
    mood_group = models.CharField(
        max_length=30,
    )

    # 음악 제목 저장함.
    title = models.CharField(
        max_length=100,
    )

    # 음악 제작자 정보 저장함.
    artist = models.CharField(
        max_length=100,
        blank=True,
    )

    # bgm/static/bgm/audio/ 내부의 음원 파일명 저장함.
    file_name = models.CharField(
        max_length=255,
    )

    # 원본 음원 출처 URL 저장함.
    source_url = models.URLField(
        blank=True,
    )

    # 음원 라이선스 이름 저장함.
    license_name = models.CharField(
        max_length=100,
        blank=True,
    )

    # 음원 라이선스 관련 URL 저장함.
    license_url = models.URLField(
        blank=True,
    )

    # 출처 표시가 필요한 음원인지 구분함.
    attribution_required = models.BooleanField(
        default=False,
    )

    # 현재 서비스에서 사용할 수 있는 음원인지 구분함.
    is_active = models.BooleanField(
        default=True,
    )

    def __str__(self):
        return f"{self.title} - {self.artist}"


class RecordBackgroundMusic(models.Model):
    # 하나의 기록에는 하나의 BGM만 연결함.
    record = models.OneToOneField(
        Record,
        on_delete=models.CASCADE,
        related_name="background_music",
    )

    # 하나의 음악을 여러 기록에서 사용할 수 있음.
    music = models.ForeignKey(
        BackgroundMusic,
        on_delete=models.PROTECT,
        related_name="records",
    )

    # 기록과 음악이 처음 연결된 시각 저장함.
    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        return f"{self.record_id} - {self.music.title}"