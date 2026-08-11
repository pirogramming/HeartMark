from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .views import HOME_PROMPTS
from locations.models import Place
from locations.services import VERIFIED_LOCATION_SESSION_KEY


class HomePromptTests(TestCase):
    def test_authenticated_home_contains_a_random_prompt(self):
        user = get_user_model().objects.create_user(username="prompt-user", password="test-pass")
        self.client.force_login(user)

        response = self.client.get(reverse("common:home"))

        self.assertEqual(response.status_code, 200)
        self.assertIn(response.context["home_prompt"], HOME_PROMPTS)
        self.assertContains(response, response.context["home_prompt"])

    def test_guest_home_does_not_receive_a_random_prompt(self):
        response = self.client.get(reverse("common:home"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["home_prompt"], "")


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

    def verify_location(self):
        session = self.client.session
        session[VERIFIED_LOCATION_SESSION_KEY] = {
            "place_id": self.place.pk,
            "verified_on": timezone.localdate().isoformat(),
        }
        session.save()

    def test_unverified_user_is_linked_to_place_select(self):
        response = self.client.get(reverse("common:home"))
        self.assertContains(response, f'href="{reverse("locations:place_select")}"')
        self.assertNotContains(response, "data-record-modal")

    def test_verified_user_is_still_linked_to_place_select(self):
        """오늘 이미 인증했더라도 홈의 기록 작성 링크는 위치 선택 화면으로 가야 한다."""
        self.verify_location()

        response = self.client.get(reverse("common:home"))
        self.assertContains(response, f'href="{reverse("locations:place_select")}"')
        # 홈에서 곧바로 모달을 여는 트리거는 없어야 한다.
        self.assertNotContains(response, "data-open-record-modal")
