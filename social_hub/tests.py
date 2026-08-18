from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from accounts.models import UserProfile
from friendships.models import Friendship, Invitation
from record_sharing.models import RecordShare, RecordShareComment
from records.models import Record


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

    def test_member_can_be_searched_by_username_and_display_name(self):
        self.client.force_login(self.user)

        username_response = self.client.get(
            reverse("social_hub:friend_management"),
            {"q": "friend"},
        )
        display_name_response = self.client.get(
            reverse("social_hub:friend_management"),
            {"q": "보낸"},
        )

        self.assertContains(username_response, "@friend")
        self.assertContains(username_response, "친구 요청")
        self.assertContains(display_name_response, "@sender")

    def test_friend_request_updates_sent_and_received_tabs(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("friendships:send_request", args=[self.friend.pk]),
            {"next": reverse("social_hub:friend_management")},
        )

        self.assertRedirects(response, reverse("social_hub:friend_management"))
        self.assertTrue(
            Invitation.objects.filter(
                inviter=self.user,
                invitee=self.friend,
                status=Invitation.Status.PENDING,
            ).exists()
        )

        sent_page = self.client.get(reverse("social_hub:friend_management"))
        self.assertContains(sent_page, "답장 기다리는 중")

        self.client.force_login(self.friend)
        received_page = self.client.get(reverse("social_hub:friend_management"))
        self.assertContains(received_page, "친구 수락")


class SentRecordsViewTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.sender = user_model.objects.create_user(
            username="sender",
            password="password",
        )
        self.receiver = user_model.objects.create_user(
            username="receiver",
            password="password",
        )
        UserProfile.objects.create(
            user=self.sender,
            display_name="보내는 사람",
            character_id=1,
        )
        UserProfile.objects.create(
            user=self.receiver,
            display_name="받는 친구",
            character_id=2,
        )
        first, second = sorted((self.sender, self.receiver), key=lambda user: user.pk)
        Friendship.objects.create(user1=first, user2=second)
        self.record = Record.objects.create(
            user=self.sender,
            weather=Record.Weather.SUNNY,
            title="친구에게 보낼 기록",
            content="오늘 남긴 마음자국이에요.",
            image="records/test.png",
            emotions=[2],
            main_emotion=2,
        )

    def test_anonymous_user_is_redirected_to_login(self):
        response = self.client.get(reverse("social_hub:sent_records"))

        self.assertRedirects(
            response,
            f"{reverse('accounts:login')}?next={reverse('social_hub:sent_records')}",
            fetch_redirect_response=False,
        )

    def test_active_sent_share_is_rendered_with_receiver_and_record(self):
        RecordShare.objects.create(
            record=self.record,
            sender=self.sender,
            receiver=self.receiver,
            share_location=True,
        )
        self.client.force_login(self.sender)

        response = self.client.get(reverse("social_hub:sent_records"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "받는 친구님에게 보낸 마음 편지")
        self.assertContains(response, "친구에게 보낼 기록")
        self.assertContains(response, "장소 공개")
        self.assertContains(
            response,
            reverse("record_sharing:revoke", args=[self.record.pk]),
        )

    def test_revoked_share_is_not_rendered(self):
        share = RecordShare.objects.create(
            record=self.record,
            sender=self.sender,
            receiver=self.receiver,
        )
        share.revoke()
        self.client.force_login(self.sender)

        response = self.client.get(reverse("social_hub:sent_records"))

        self.assertNotContains(response, "친구에게 보낼 기록")
        self.assertContains(response, "아직 보낸 마음 편지가 없어요.")

    def test_both_participants_see_all_comments_in_their_mailboxes(self):
        share = RecordShare.objects.create(
            record=self.record,
            sender=self.sender,
            receiver=self.receiver,
        )
        RecordShareComment.objects.create(
            share=share,
            author=self.sender,
            content="보낸 사람이 남긴 댓글",
        )
        RecordShareComment.objects.create(
            share=share,
            author=self.receiver,
            content="받은 사람이 남긴 댓글",
        )

        self.client.force_login(self.sender)
        sent_response = self.client.get(reverse("social_hub:sent_records"))
        self.assertContains(sent_response, "보낸 사람이 남긴 댓글")
        self.assertContains(sent_response, "받은 사람이 남긴 댓글")

        self.client.force_login(self.receiver)
        received_response = self.client.get(reverse("social_hub:shared_records"))
        self.assertContains(received_response, "보낸 사람이 남긴 댓글")
        self.assertContains(received_response, "받은 사람이 남긴 댓글")

    def test_comment_creation_returns_each_participant_to_their_mailbox(self):
        share = RecordShare.objects.create(
            record=self.record,
            sender=self.sender,
            receiver=self.receiver,
        )
        comment_url = reverse("record_sharing:comment_create", args=[share.pk])

        self.client.force_login(self.sender)
        sender_response = self.client.post(comment_url, {"content": "발신자 댓글"})
        self.assertRedirects(
            sender_response,
            f"{reverse('social_hub:sent_records')}?comments={share.pk}#shared-record-{share.pk}",
            fetch_redirect_response=False,
        )

        self.client.force_login(self.receiver)
        receiver_response = self.client.post(comment_url, {"content": "수신자 댓글"})
        self.assertRedirects(
            receiver_response,
            f"{reverse('social_hub:shared_records')}?comments={share.pk}#shared-record-{share.pk}",
            fetch_redirect_response=False,
        )
