from django.db import migrations


# ============================================================
# 기본 BGM 데이터 생성
# ============================================================

def create_background_music(apps, schema_editor):
    # migration 시점의 BackgroundMusic 모델 가져옴.
    BackgroundMusic = apps.get_model(
        "bgm",
        "BackgroundMusic",
    )

    # 서비스에서 사용할 기본 BGM 5곡.
    music_data = [
        {
            "mood_group": "general",
            "title": "Down Town",
            "artist": "Retro BGM Chan",
            "file_name": (
                "retro-bgm-chan-down-town-523653.mp3"
            ),
            "source_url": "",
            "license_name": "",
            "license_url": "",
            "attribution_required": False,
            "is_active": True,
        },
        {
            "mood_group": "general",
            "title": "Good Morning",
            "artist": "Retro BGM Chan",
            "file_name": (
                "retro-bgm-chan-good-morning-516296.mp3"
            ),
            "source_url": "",
            "license_name": "",
            "license_url": "",
            "attribution_required": False,
            "is_active": True,
        },
        {
            "mood_group": "general",
            "title": "Home at Night",
            "artist": "Retro BGM Chan",
            "file_name": (
                "retro-bgm-chan-home-at-night-516298.mp3"
            ),
            "source_url": "",
            "license_name": "",
            "license_url": "",
            "attribution_required": False,
            "is_active": True,
        },
        {
            "mood_group": "general",
            "title": "Home Town",
            "artist": "Retro BGM Chan",
            "file_name": (
                "retro-bgm-chan-home-town-516297.mp3"
            ),
            "source_url": "",
            "license_name": "",
            "license_url": "",
            "attribution_required": False,
            "is_active": True,
        },
        {
            "mood_group": "general",
            "title": "Shop",
            "artist": "Retro BGM Chan",
            "file_name": (
                "retro-bgm-chan-shop-516323.mp3"
            ),
            "source_url": "",
            "license_name": "",
            "license_url": "",
            "attribution_required": False,
            "is_active": True,
        },
    ]

    # 같은 파일명이 이미 있다면 중복 생성하지 않음.
    for music in music_data:
        BackgroundMusic.objects.get_or_create(
            file_name=music["file_name"],
            defaults=music,
        )


# ============================================================
# migration 되돌릴 때 기본 BGM 삭제
# ============================================================

def delete_background_music(apps, schema_editor):
    BackgroundMusic = apps.get_model(
        "bgm",
        "BackgroundMusic",
    )

    file_names = [
        "retro-bgm-chan-down-town-523653.mp3",
        "retro-bgm-chan-good-morning-516296.mp3",
        "retro-bgm-chan-home-at-night-516298.mp3",
        "retro-bgm-chan-home-town-516297.mp3",
        "retro-bgm-chan-shop-516323.mp3",
    ]

    BackgroundMusic.objects.filter(
        file_name__in=file_names,
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        (
            "bgm",
            "0002_recordbackgroundmusic",
        ),
    ]

    operations = [
        migrations.RunPython(
            create_background_music,
            delete_background_music,
        ),
    ]