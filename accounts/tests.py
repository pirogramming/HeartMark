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
