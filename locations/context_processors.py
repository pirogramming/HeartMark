from django.urls import reverse

from .services import has_verified_location


def location_verification(request):
    can_create_record = has_verified_location(request)
    return {
        "can_create_record": can_create_record,
        "record_entry_url": (
            f"{reverse('common:home')}?open_record=1"
            if can_create_record
            else reverse("records:create")
        ),
    }
