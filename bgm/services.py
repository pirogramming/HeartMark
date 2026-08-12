from .models import BackgroundMusic


def get_available_music():
    """
    현재 사용할 수 있는 전체 BGM 목록 반환함.
    """

    # 활성화된 BGM만 조회함.
    return BackgroundMusic.objects.filter(
        is_active=True,
    ).order_by(
        "id",
    )