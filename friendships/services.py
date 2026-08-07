from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from .models import Friendship, Invitation


class FriendshipError(ValueError):
    pass


def _ordered_users(user1, user2):
    if user1.pk == user2.pk:
        raise FriendshipError("자기 자신과는 친구가 될 수 없습니다.")
    return (user1, user2) if user1.pk < user2.pk else (user2, user1)


def are_friends(user1, user2):
    if not user1 or not user2 or user1.pk == user2.pk:
        return False
    first, second = _ordered_users(user1, user2)
    return Friendship.objects.filter(user1=first, user2=second).exists()


def get_friends(user):
    friendships = Friendship.objects.filter(Q(user1=user) | Q(user2=user)).select_related("user1", "user2")
    friend_ids = [
        friendship.user2_id if friendship.user1_id == user.pk else friendship.user1_id
        for friendship in friendships
    ]
    return get_user_model().objects.filter(pk__in=friend_ids).order_by("username")


def get_received_requests(user):
    return Invitation.objects.filter(
        invitee=user,
        status=Invitation.Status.PENDING,
    ).select_related("inviter", "invitee")


def get_sent_requests(user):
    return Invitation.objects.filter(
        inviter=user,
        status=Invitation.Status.PENDING,
    ).select_related("inviter", "invitee")


def get_or_create_invite_link(user):
    invitation = Invitation.objects.filter(
        inviter=user,
        invitee__isnull=True,
        status=Invitation.Status.PENDING,
    ).order_by("-created_at").first()
    if invitation and not invitation.is_expired:
        return invitation, False
    return Invitation.objects.create(inviter=user), True


def send_friend_request(inviter, invitee, message=""):
    if inviter.pk == invitee.pk:
        raise FriendshipError("자기 자신에게 친구 요청을 보낼 수 없습니다.")
    if are_friends(inviter, invitee):
        raise FriendshipError("이미 친구인 사용자입니다.")
    if Invitation.objects.filter(
        status=Invitation.Status.PENDING,
    ).filter(
        Q(inviter=inviter, invitee=invitee) | Q(inviter=invitee, invitee=inviter)
    ).exists():
        raise FriendshipError("이미 대기 중인 친구 요청이 있습니다.")
    return Invitation.objects.create(inviter=inviter, invitee=invitee, message=message[:120])


@transaction.atomic
def accept_invitation(invitation, user):
    invitation = Invitation.objects.select_for_update().get(pk=invitation.pk)
    if not invitation.is_pending:
        raise FriendshipError("이미 처리된 친구 요청입니다.")
    if invitation.is_expired:
        raise FriendshipError("만료된 친구 요청입니다.")
    if invitation.inviter_id == user.pk:
        raise FriendshipError("자기 자신의 초대는 수락할 수 없습니다.")
    if invitation.invitee_id and invitation.invitee_id != user.pk:
        raise FriendshipError("이 친구 요청을 처리할 권한이 없습니다.")
    if are_friends(invitation.inviter, user):
        invitation.status = Invitation.Status.ACCEPTED
        invitation.invitee = user
        invitation.responded_at = timezone.now()
        invitation.save(update_fields=["invitee", "status", "responded_at", "updated_at"])
        raise FriendshipError("이미 친구인 사용자입니다.")

    first, second = _ordered_users(invitation.inviter, user)
    friendship, _ = Friendship.objects.get_or_create(user1=first, user2=second)
    invitation.invitee = user
    invitation.status = Invitation.Status.ACCEPTED
    invitation.responded_at = timezone.now()
    invitation.save(update_fields=["invitee", "status", "responded_at", "updated_at"])
    Invitation.objects.filter(
        status=Invitation.Status.PENDING,
    ).filter(
        Q(inviter=invitation.inviter, invitee=user) | Q(inviter=user, invitee=invitation.inviter)
    ).exclude(pk=invitation.pk).update(
        status=Invitation.Status.CANCELLED,
        responded_at=timezone.now(),
    )
    return friendship


def reject_invitation(invitation, user):
    if not invitation.is_pending:
        raise FriendshipError("이미 처리된 친구 요청입니다.")
    if invitation.inviter_id == user.pk:
        invitation.status = Invitation.Status.CANCELLED
    elif invitation.invitee_id in (None, user.pk):
        invitation.invitee = user if invitation.invitee_id is None else invitation.invitee
        invitation.status = Invitation.Status.REJECTED
    else:
        raise FriendshipError("이 친구 요청을 처리할 권한이 없습니다.")
    invitation.responded_at = timezone.now()
    invitation.save(update_fields=["invitee", "status", "responded_at", "updated_at"])
    return invitation


def delete_friend(user, friend):
    first, second = _ordered_users(user, friend)
    deleted_count, _ = Friendship.objects.filter(user1=first, user2=second).delete()
    if not deleted_count:
        raise FriendshipError("친구 관계를 찾을 수 없습니다.")
    return deleted_count
