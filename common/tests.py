
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .views import HOME_PROMPTS


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
