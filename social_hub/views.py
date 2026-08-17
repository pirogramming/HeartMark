from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render
from django.templatetags.static import static
from django.urls import reverse
from django.utils.formats import date_format
from django.utils import timezone

from friendships.models import Invitation
from friendships.services import (
    get_friends,
    get_or_create_invite_link,
    get_received_requests,
    get_sent_requests,
)
from record_sharing.services import get_sent_records, get_shared_place_data, get_shared_records
from records.models import EMOTION_NAMES, Record


def _display_name(user):
    profile = getattr(user, "profile", None)
    return getattr(profile, "display_name", "") or user.first_name or user.username


def _character_url(user):
    profile = getattr(user, "profile", None)
    character_id = getattr(profile, "character_id", None)
    if character_id not in range(1, 6):
        character_id = 2
    return static(f"accounts/images/{character_id}.png")


def _friend_item(user):
    return {
        "id": user.pk,
        "name": _display_name(user),
        "character_url": _character_url(user),
        "message": "함께 마음자국을 나누는 친구예요.",
        "delete_url": reverse("friendships:friend_delete", args=[user.pk]),
    }


def _request_item(invitation, counterpart, received=False):
    return {
        "id": invitation.pk,
        "name": _display_name(counterpart),
        "character_url": _character_url(counterpart),
        "message": invitation.message or (
            "마음자국 친구가 되고 싶대요."
            if received
            else "친구의 답장을 기다리고 있어요."
        ),
        "accept_url": reverse("friendships:respond_request", args=[invitation.pk, "accept"]),
        "reject_url": reverse("friendships:respond_request", args=[invitation.pk, "reject"]),
    }


def _search_member_item(user, friend_ids, sent_ids, received_ids):
    if user.pk in friend_ids:
        status = "friend"
    elif user.pk in sent_ids:
        status = "sent"
    elif user.pk in received_ids:
        status = "received"
    else:
        status = "none"

    return {
        "id": user.pk,
        "username": user.username,
        "name": _display_name(user),
        "character_url": _character_url(user),
        "status": status,
        "request_url": reverse("friendships:send_request", args=[user.pk]),
    }


@login_required(login_url="accounts:login")
def friend_management(request):
    friend_users = list(get_friends(request.user))
    friends = [_friend_item(user) for user in friend_users]
    received_requests = [
        _request_item(invitation, invitation.inviter, received=True)
        for invitation in get_received_requests(request.user)
    ]
    sent_requests = [
        _request_item(invitation, invitation.invitee)
        for invitation in get_sent_requests(request.user)
        if invitation.invitee_id
    ]
    invitation, _ = get_or_create_invite_link(request.user)
    member_query = request.GET.get("q", "").strip()
    member_results = []
    if member_query:
        pending_invitations = Invitation.objects.filter(
            status=Invitation.Status.PENDING,
        ).filter(
            Q(inviter=request.user) | Q(invitee=request.user)
        )
        sent_ids = {
            item.invitee_id
            for item in pending_invitations
            if item.inviter_id == request.user.pk and item.invitee_id
        }
        received_ids = {
            item.inviter_id
            for item in pending_invitations
            if item.invitee_id == request.user.pk
        }
        friend_ids = {user.pk for user in friend_users}
        matched_users = (
            get_user_model().objects.filter(
                Q(username__icontains=member_query)
                | Q(first_name__icontains=member_query)
                | Q(profile__display_name__icontains=member_query)
            )
            .exclude(pk=request.user.pk)
            .select_related("profile")
            .distinct()
            .order_by("username")[:12]
        )
        member_results = [
            _search_member_item(user, friend_ids, sent_ids, received_ids)
            for user in matched_users
        ]

    context = {
        "invite_url": request.build_absolute_uri(
            reverse("friendships:invite_detail", args=[invitation.code])
        ),
        "friends": friends,
        "received_requests": received_requests,
        "sent_requests": sent_requests,
        "member_query": member_query,
        "member_results": member_results,
        "member_search_performed": bool(member_query),
        "next_url": request.get_full_path(),
        "share_records": Record.objects.filter(user=request.user).order_by("-created_at"),
    }
    return render(request, "social_hub/friend_management.html", context)


@login_required(login_url="accounts:login")
def shared_records(request):
    """은아의 공유 서비스가 허용한 기록과 장소 정보만 화면 형태로 변환한다."""
    items = []
    open_comment_share = request.GET.get("comments")
    for share in get_shared_records(request.user):
        record = share.record
        place = get_shared_place_data(share, request.user)
        items.append(
            {
                "share_id": share.pk,
                "sender_name": _display_name(share.sender),
                "sender_character_url": _character_url(share.sender),
                "record_id": record.pk,
                "title": record.title or "오늘의 기록",
                "record_date": date_format(record.created_at, "Y년 n월 j일"),
                "main_emotion": f"{record.main_emotion:02d}",
                "main_emotion_name": EMOTION_NAMES.get(record.main_emotion, f"감정 {record.main_emotion}"),
                "image_url": record.image.url if record.image else "",
                "content_preview": record.content,
                "share_location": bool(place and place["is_visible"]),
                "place_name": place["name"] if place and place["is_visible"] else "",
                "detail_url": reverse("record_sharing:shared_detail", args=[share.pk]),
                "comment_url": reverse("record_sharing:comment_create", args=[share.pk]),
                "comments_open": open_comment_share == str(share.pk),
                "comments": [
                    {
                        "author_name": _display_name(comment.author),
                        "content": comment.content,
                        "created_at": date_format(timezone.localtime(comment.created_at), "n/j H:i"),
                        "is_mine": comment.author_id == request.user.pk,
                        "delete_url": reverse(
                            "record_sharing:comment_delete",
                            args=[share.pk, comment.pk],
                        ),
                    }
                    for comment in share.comments.select_related("author").all()
                ],
            }
        )

    context = {"shared_records": items}
    return render(request, "social_hub/shared_records.html", context)


@login_required(login_url="accounts:login")
def sent_records(request):
    """내가 누구에게 어떤 기록을 보냈는지 확인하고 공유를 취소한다."""
    items = []
    for share in get_sent_records(request.user):
        record = share.record
        items.append(
            {
                "share_id": share.pk,
                "receiver_id": share.receiver_id,
                "receiver_name": _display_name(share.receiver),
                "receiver_character_url": _character_url(share.receiver),
                "record_id": record.pk,
                "title": record.title or "오늘의 기록",
                "record_date": date_format(record.created_at, "Y년 n월 j일"),
                "shared_at": date_format(timezone.localtime(share.created_at), "Y년 n월 j일 H:i"),
                "main_emotion": f"{record.main_emotion:02d}",
                "main_emotion_name": EMOTION_NAMES.get(
                    record.main_emotion,
                    f"감정 {record.main_emotion}",
                ),
                "image_url": record.image.url if record.image else "",
                "content_preview": record.content,
                "share_location": share.share_location,
                "detail_url": reverse("records:detail", args=[record.pk]),
                "revoke_url": reverse("record_sharing:revoke", args=[record.pk]),
            }
        )

    return render(
        request,
        "social_hub/sent_records.html",
        {"sent_records": items, "next_url": request.get_full_path()},
    )
