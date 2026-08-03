from django.urls import reverse

from .services import get_verified_place


def location_verification(request):
    verified_place = get_verified_place(request) if request.user.is_authenticated else None
    can_create_record = verified_place is not None
    return {
        "can_create_record": can_create_record,
        "verified_place": verified_place,
        "record_entry_url": (
            f"{reverse('common:home')}?open_record=1"
            if can_create_record
            else reverse("records:create")
        ),
    }
