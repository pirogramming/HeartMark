import random

from .emotion_mapping import EMOTION_MUSIC_GROUP
from .models import BackgroundMusic, RecordBackgroundMusic


def get_music_for_record(record):
    """
    기록의 대표 감정에 맞는 BGM을 조회함.

    이미 음악이 연결된 기록이라면 기존 음악을 반환함.
    처음 조회하는 기록이라면 감정 그룹에 맞는 음악을 선택하고 저장함.
    """

    # 해당 기록에 이미 연결된 음악이 있는지 확인함.
    existing_music = (
        RecordBackgroundMusic.objects
        .filter(record=record)
        .select_related("music")
        .first()
    )

    # 이미 음악이 연결되어 있다면 기존 음악 반환함.
    if existing_music:
        return existing_music.music

    # 기록의 대표 감정 ID 가져옴.
    emotion_id = record.main_emotion

    # 대표 감정에 해당하는 음악 분위기 그룹 조회함.
    mood_group = EMOTION_MUSIC_GROUP.get(emotion_id)

    # 매핑되지 않은 감정이라면 음악 없음으로 처리함.
    if mood_group is None:
        return None

    # 해당 분위기 그룹에서 현재 사용 가능한 음악 조회함.
    available_musics = list(
        BackgroundMusic.objects.filter(
            mood_group=mood_group,
            is_active=True,
        )
    )

    # 사용할 수 있는 음악이 하나도 없다면 음악 없음으로 처리함.
    if not available_musics:
        return None

    # 사용 가능한 음악 중 하나 선택함.
    selected_music = random.choice(available_musics)

    # 선택된 음악을 해당 기록에 저장함.
    # 이후 같은 기록을 열면 같은 음악을 사용하게 됨.
    RecordBackgroundMusic.objects.create(
        record=record,
        music=selected_music,
    )

    return selected_music