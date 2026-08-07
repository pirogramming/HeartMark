from django.contrib.auth import get_user_model
from django.test import TestCase

from .models import Invitation
from .services import (
    FriendshipError,
    accept_invitation,
    are_friends,
    get_friends,
    send_friend_request,
)


class FriendshipServiceTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.yeonwoo = user_model.objects.create_user(username="yeonwoo", password="pass")
        self.friend = user_model.objects.create_user(username="friend", password="pass")

    def test_accept_invitation_creates_friendship(self):
        invitation = send_friend_request(self.yeonwoo, self.friend)

        accept_invitation(invitation, self.friend)

        self.assertTrue(are_friends(self.yeonwoo, self.friend))
        self.assertIn(self.friend, list(get_friends(self.yeonwoo)))

    def test_prevent_self_request(self):
        with self.assertRaises(FriendshipError):
            send_friend_request(self.yeonwoo, self.yeonwoo)

    def test_prevent_duplicate_pending_request(self):
        send_friend_request(self.yeonwoo, self.friend)

        with self.assertRaises(FriendshipError):
            send_friend_request(self.friend, self.yeonwoo)

    def test_link_invitation_can_be_accepted_by_first_user(self):
        invitation = Invitation.objects.create(inviter=self.yeonwoo)

        accept_invitation(invitation, self.friend)

        invitation.refresh_from_db()
        self.assertEqual(invitation.invitee, self.friend)
        self.assertEqual(invitation.status, Invitation.Status.ACCEPTED)
