from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from locations.models import Place
from locations.services import VERIFIED_LOCATION_SESSION_KEY


class HomeRecordEntryTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="home-user",
            password="test-password",
        )
        self.place = Place.objects.create(
            name="집 근처 공원",
            address="서울특별시 마포구 테스트로 1",
            district="마포구",
            latitude="37.5500000",
            longitude="126.9100000",
        )
        self.client.force_login(self.user)

    def test_unverified_user_is_linked_to_record_entry_check(self):
        response = self.client.get(reverse("common:home"))
        self.assertContains(response, f'href="{reverse("records:create")}"')
        self.assertNotContains(response, 'data-record-modal')

    def test_verified_user_can_open_record_modal_on_home(self):
        session = self.client.session
        session[VERIFIED_LOCATION_SESSION_KEY] = {
            "place_id": self.place.pk,
            "verified_on": timezone.localdate().isoformat(),
        }
        session.save()

        response = self.client.get(reverse("common:home"))
        self.assertContains(response, "data-open-record-modal")
        self.assertContains(response, "data-record-modal")
