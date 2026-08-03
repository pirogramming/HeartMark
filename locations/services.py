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


def has_verified_location(request):
    return bool(request.user.is_authenticated and get_verified_place(request))
