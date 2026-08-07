from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from accounts.models import UserProfile
from friendships.models import Friendship, Invitation


class FriendManagementViewTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(username="owner", password="password")
        self.friend = user_model.objects.create_user(username="friend", password="password")
        self.sender = user_model.objects.create_user(username="sender", password="password")
        UserProfile.objects.create(user=self.user, display_name="나", character_id=1)
        UserProfile.objects.create(user=self.friend, display_name="친구", character_id=3)
        UserProfile.objects.create(user=self.sender, display_name="보낸 사람", character_id=4)

    def test_anonymous_user_is_redirected_to_login(self):
        response = self.client.get(reverse("social_hub:friend_management"))

        self.assertRedirects(
            response,
            f"{reverse('accounts:login')}?next={reverse('social_hub:friend_management')}",
            fetch_redirect_response=False,
        )

    def test_real_friend_and_request_data_are_rendered(self):
        first, second = sorted((self.user, self.friend), key=lambda user: user.pk)
        Friendship.objects.create(user1=first, user2=second)
        Invitation.objects.create(inviter=self.sender, invitee=self.user)
        self.client.force_login(self.user)

        response = self.client.get(reverse("social_hub:friend_management"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "친구")
        self.assertContains(response, "보낸 사람")
        self.assertContains(response, "/friendships/invite/")
        self.assertContains(response, reverse("friendships:friend_delete", args=[self.friend.pk]))
