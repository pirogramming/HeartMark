from django.utils import timezone

from .models import Place


VERIFIED_LOCATION_SESSION_KEY = "verified_location"


def set_verified_place(request, place):
    """Store today's verified place in the current user's session."""
    request.session[VERIFIED_LOCATION_SESSION_KEY] = {
        "place_id": place.pk,
        "verified_on": timezone.localdate().isoformat(),
    }


def get_verified_place(request):
    """Return today's verified Place, removing stale session data."""
    verification = request.session.get(VERIFIED_LOCATION_SESSION_KEY) or {}
    if verification.get("verified_on") != timezone.localdate().isoformat():
        request.session.pop(VERIFIED_LOCATION_SESSION_KEY, None)
        return None

    place = Place.objects.filter(pk=verification.get("place_id")).first()
    if place is None:
        request.session.pop(VERIFIED_LOCATION_SESSION_KEY, None)
    return place


def clear_verified_place(request):
    """
    세션에 남아 있는 위치 인증을 지운다.

    기록이 실제로 저장된 직후에 호출한다. 인증 정보를 그대로 두면 날짜가 바뀌기 전까지
    같은 Place가 계속 유효한 상태로 남아, 다음 기록이 (사용자가 다시 고르지 않은)
    이전 장소로 저장될 여지가 생긴다.
    """
    request.session.pop(VERIFIED_LOCATION_SESSION_KEY, None)


def has_verified_location(request):
    return bool(request.user.is_authenticated and get_verified_place(request))
