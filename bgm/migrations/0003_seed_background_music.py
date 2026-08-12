from django.db import migrations

# bgm/static/bgm/audio/ 에 들어 있는 음원 파일과 짝이 되는 DB 레코드.
# 이 행이 없으면 파일이 있어도 BGM이 재생되지 않으므로(services.get_music_for_record가
# mood_group으로 조회한다) 새 DB에 배포할 때마다 자동으로 생성되도록 마이그레이션으로 넣는다.
#
# 주의: mood_group 배정과 artist/라이선스 정보는 파일명에서 추정한 값이다.
# 실제 출처(Pixabay 등)를 확인해서 source_url / license_name / license_url /
# attribution_required 를 채워 넣을 것.
SEED_MUSIC = [
    {
        "file_name": "alex-morgan-sad-piano-emotional-rain-story-575883.mp3",
        "mood_group": "grief",
        "title": "Sad Piano Emotional Rain Story",
        "artist": "Alex Morgan",
    },
    {
        "file_name": "nastelbom-love-466198.mp3",
        "mood_group": "love",
        "title": "Love",
        "artist": "Nastelbom",
    },
    {
        "file_name": "the_mountain-love-481753.mp3",
        "mood_group": "love",
        "title": "Love",
        "artist": "The Mountain",
    },
    {
        "file_name": "viacheslavstarostin-cute-pets-animals-music-382060.mp3",
        "mood_group": "joy",
        "title": "Cute Pets Animals Music",
        "artist": "Viacheslav Starostin",
    },
    {
        "file_name": "andriig-warm-warm-acoustic-music-573245.mp3",
        "mood_group": "moody",
        "title": "Warm Warm Acoustic Music",
        "artist": "AndriiG",
    },
]


def seed_background_music(apps, schema_editor):
    BackgroundMusic = apps.get_model("bgm", "BackgroundMusic")

    for entry in SEED_MUSIC:
        # file_name을 기준으로 삼아 이미 넣어둔 음원은 건드리지 않는다.
        BackgroundMusic.objects.update_or_create(
            file_name=entry["file_name"],
            defaults={
                "mood_group": entry["mood_group"],
                "title": entry["title"],
                "artist": entry["artist"],
                "is_active": True,
            },
        )


def unseed_background_music(apps, schema_editor):
    BackgroundMusic = apps.get_model("bgm", "BackgroundMusic")

    # 기록에 연결된 음원은 RecordBackgroundMusic이 PROTECT로 잡고 있어 삭제되지 않는다.
    # 되돌리기는 아직 아무 기록도 붙지 않은 경우에만 깔끔하게 동작한다.
    BackgroundMusic.objects.filter(
        file_name__in=[entry["file_name"] for entry in SEED_MUSIC]
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("bgm", "0002_recordbackgroundmusic"),
    ]

    operations = [
        migrations.RunPython(seed_background_music, unseed_background_music),
    ]
