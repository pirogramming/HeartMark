import json

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Place
from .services import VERIFIED_LOCATION_SESSION_KEY


class ConfirmPlaceTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="location-user",
            password="test-password",
        )

    def test_login_is_required(self):
        response = self.client.post(
            reverse("locations:confirm_place"),
            data=json.dumps({}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("accounts:login"), response.url)

    def test_confirmed_place_is_stored_as_today_verification(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("locations:confirm_place"),
            data=json.dumps({
                "latitude": "37.5665000",
                "longitude": "126.9780000",
                "address": "서울특별시 종로구 테스트로 1",
                "district": "종로구",
                "name": "테스트 장소",
                "kakao_place_id": "kakao-test-id",
            }),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        place = Place.objects.get()
        verification = self.client.session[VERIFIED_LOCATION_SESSION_KEY]
        self.assertEqual(verification["place_id"], place.pk)
        self.assertEqual(verification["verified_on"], timezone.localdate().isoformat())
        self.assertEqual(
            response.json()["redirect_url"],
            f"{reverse('locations:map')}?place={place.pk}",
        )
