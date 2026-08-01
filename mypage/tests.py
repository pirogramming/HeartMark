from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta


class MypageViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="mypage-user",
            password="test-password",
        )

    def test_login_is_required(self):
        response = self.client.get(reverse("mypage:home"))
        self.assertEqual(response.status_code, 302)

    def test_attendance_pages_begin_on_join_date(self):
        self.user.date_joined = timezone.now() - timedelta(days=20)
        self.user.save(update_fields=["date_joined"])
        self.client.force_login(self.user)
        response = self.client.get(reverse("mypage:home"))
        self.assertEqual(response.status_code, 200)
        pages = response.context["attendance_pages"]
        self.assertEqual(len(pages), 2)
        self.assertEqual(len(pages[0]["days"]), 14)
        self.assertEqual(len(pages[1]["days"]), 14)
        self.assertEqual(
            pages[0]["days"][0]["date"],
            timezone.localdate() - timedelta(days=20),
        )
        self.assertEqual(
            pages[-1]["days"][-1]["date"],
            timezone.localdate() + timedelta(days=7),
        )
        self.assertTrue(pages[-1]["days"][-1]["is_future"])

    def test_user_can_change_display_name(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("mypage:home"),
            {"display_name": "마음이"},
        )
        self.assertRedirects(response, reverse("mypage:home"))
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "마음이")
