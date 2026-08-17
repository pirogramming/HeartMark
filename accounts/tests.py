from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import UserProfile


class LoginRedirectTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="login-user",
            password="test-password",
        )
        UserProfile.objects.create(
            user=self.user,
            display_name="login-user",
            character_id=1,
            onboarding_completed=True,
        )

    def test_login_returns_to_requested_record_entry(self):
        record_entry = reverse("records:create")
        response = self.client.post(
            f"{reverse('accounts:login')}?next={record_entry}",
            {
                "username": self.user.username,
                "password": "test-password",
                "next": record_entry,
            },
        )
        self.assertRedirects(
            response,
            reverse("accounts:post_login_redirect"),
            fetch_redirect_response=False,
        )

        response = self.client.get(reverse("accounts:post_login_redirect"))
        self.assertRedirects(response, record_entry, fetch_redirect_response=False)

    def test_character_can_be_changed_from_mypage(self):
        self.client.force_login(self.user)
        response = self.client.post(
            f"{reverse('accounts:character_select')}?edit=1",
            {
                "display_name": "새 이름",
                "character_id": "4",
            },
        )

        self.assertRedirects(response, reverse("mypage:home"))
        self.user.refresh_from_db()
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.character_id, 4)
        self.assertEqual(self.user.first_name, "새 이름")

        response = self.client.get(reverse("mypage:home"))
        self.assertEqual(
            response.context["character_url"],
            "/static/accounts/images/4.png",
        )


class SignupTests(TestCase):
    def test_duplicate_username_is_rejected(self):
        User = get_user_model()
        User.objects.create_user(username="duplicate-user", password="test-password")

        response = self.client.post(
            reverse("accounts:signup"),
            {
                "username": "duplicate-user",
                "password": "test-password",
                "password_confirm": "test-password",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.filter(username="duplicate-user").count(), 1)
        self.assertIn("username", response.context["errors"])

    def test_duplicate_username_with_different_case_is_rejected(self):
        User = get_user_model()
        User.objects.create_user(username="DuplicateUser", password="test-password")

        response = self.client.post(
            reverse("accounts:signup"),
            {
                "username": "duplicateuser",
                "password": "test-password",
                "password_confirm": "test-password",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.filter(username__iexact="duplicateuser").count(), 1)
        self.assertIn("username", response.context["errors"])
