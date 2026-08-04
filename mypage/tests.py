from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from calendar import monthrange
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

    def test_attendance_can_be_filtered_by_period(self):
        self.user.date_joined = timezone.now() - timedelta(days=20)
        self.user.save(update_fields=["date_joined"])
        self.client.force_login(self.user)
        today = timezone.localdate()
        selected_date = today - timedelta(days=5)

        response = self.client.get(
            reverse("mypage:home"),
            {
                "attendance_year": selected_date.year,
                "attendance_month": selected_date.month,
                "attendance_day": selected_date.day,
            },
        )

        self.assertEqual(response.status_code, 200)
        pages = response.context["attendance_pages"]
        self.assertEqual(len(pages), 1)
        self.assertEqual(len(pages[0]["days"]), 1)
        self.assertEqual(pages[0]["days"][0]["date"], selected_date)

    def test_attendance_month_selection_shows_the_whole_month(self):
        self.user.date_joined = timezone.now() - timedelta(days=400)
        self.user.save(update_fields=["date_joined"])
        self.client.force_login(self.user)
        selected_date = timezone.localdate().replace(day=1)

        response = self.client.get(
            reverse("mypage:home"),
            {
                "attendance_year": selected_date.year,
                "attendance_month": selected_date.month,
            },
        )

        pages = response.context["attendance_pages"]
        days = [day for page in pages for day in page["days"]]
        self.assertEqual(days[0]["date"], selected_date)
        self.assertEqual(days[-1]["date"].month, selected_date.month)
        self.assertEqual(days[-1]["date"].day, monthrange(selected_date.year, selected_date.month)[1])
