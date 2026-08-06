from django.contrib.auth import get_user_model
from django.apps import apps
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

    def test_display_name_is_synced_to_accounts_profile(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("mypage:home"),
            {"display_name": "updated-name"},
        )

        self.assertRedirects(response, reverse("mypage:home"))
        profile_model = apps.get_model("accounts", "UserProfile")
        profile = profile_model.objects.get(user=self.user)
        self.assertEqual(profile.display_name, "updated-name")

    def test_existing_display_name_is_repaired_when_mypage_opens(self):
        profile_model = apps.get_model("accounts", "UserProfile")
        profile_model.objects.create(
            user=self.user,
            display_name="old-name",
            character_id=1,
        )
        self.user.first_name = "latest-name"
        self.user.save(update_fields=["first_name"])
        self.client.force_login(self.user)

        response = self.client.get(reverse("mypage:home"))

        self.assertEqual(response.status_code, 200)
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.display_name, "latest-name")

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

    def test_attendance_year_selection_shows_the_whole_year(self):
        selected_year = timezone.localdate().year - 1
        self.user.date_joined = timezone.make_aware(
            timezone.datetime(selected_year - 1, 1, 1)
        )
        self.user.save(update_fields=["date_joined"])
        self.client.force_login(self.user)

        response = self.client.get(
            reverse("mypage:home"),
            {"attendance_year": selected_year},
        )

        days = [
            day
            for page in response.context["attendance_pages"]
            for day in page["days"]
        ]
        self.assertEqual(days[0]["date"], date(selected_year, 1, 1))
        self.assertEqual(days[-1]["date"], date(selected_year, 12, 31))
        self.assertEqual(response.context["attendance_period_label"], f"{selected_year}년 전체")

    def test_period_before_join_date_returns_no_attendance_days(self):
        self.user.date_joined = timezone.now().replace(month=7, day=31)
        self.user.save(update_fields=["date_joined"])
        self.client.force_login(self.user)

        response = self.client.get(
            reverse("mypage:home"),
            {
                "attendance_year": self.user.date_joined.year,
                "attendance_month": 1,
            },
        )

        self.assertEqual(response.context["attendance_pages"], [])
        self.assertFalse(response.context["attendance_has_days"])
        self.assertContains(response, "검색 기록이 없습니다.")

    def test_future_month_shows_empty_footprint_days(self):
        today = timezone.localdate()
        future_year = today.year + 1
        self.client.force_login(self.user)

        response = self.client.get(
            reverse("mypage:home"),
            {"attendance_year": future_year, "attendance_month": 1},
        )

        days = [
            day
            for page in response.context["attendance_pages"]
            for day in page["days"]
        ]
        self.assertEqual(len(days), 31)
        self.assertTrue(all(day["is_future"] for day in days))
        self.assertTrue(all(day["emotion_number"] is None for day in days))
