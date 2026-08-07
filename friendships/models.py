import secrets

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils import timezone


def make_invitation_code():
    return secrets.token_urlsafe(8)


class Friendship(models.Model):
    user1 = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="friendships_as_user1",
    )
    user2 = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="friendships_as_user2",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=~Q(user1=models.F("user2")),
                name="friendship_prevent_self_relation",
            ),
            models.UniqueConstraint(
                fields=["user1", "user2"],
                name="friendship_unique_user_pair",
            ),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user1} - {self.user2}"

    def clean(self):
        super().clean()
        if self.user1_id and self.user2_id and self.user1_id == self.user2_id:
            raise ValidationError("자기 자신과는 친구 관계를 만들 수 없습니다.")

    def save(self, *args, **kwargs):
        if self.user1_id and self.user2_id and self.user1_id > self.user2_id:
            self.user1_id, self.user2_id = self.user2_id, self.user1_id
        self.full_clean()
        return super().save(*args, **kwargs)


class Invitation(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "대기"
        ACCEPTED = "accepted", "수락"
        REJECTED = "rejected", "거절"
        CANCELLED = "cancelled", "취소"

    inviter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_friend_invitations",
    )
    invitee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="received_friend_invitations",
    )
    code = models.CharField(max_length=32, unique=True, default=make_invitation_code)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.PENDING)
    message = models.CharField(max_length=120, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    responded_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=Q(invitee__isnull=True) | ~Q(inviter=models.F("invitee")),
                name="invitation_prevent_self_request",
            ),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        target = self.invitee or "link"
        return f"{self.inviter} -> {target} ({self.status})"

    @property
    def is_pending(self):
        return self.status == self.Status.PENDING

    @property
    def is_expired(self):
        return self.expires_at is not None and self.expires_at <= timezone.now()

    def clean(self):
        super().clean()
        if self.invitee_id and self.inviter_id == self.invitee_id:
            raise ValidationError("자기 자신에게 친구 요청을 보낼 수 없습니다.")
