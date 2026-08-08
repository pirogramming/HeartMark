from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render
from django.templatetags.static import static
from django.urls import reverse

from friendships.models import Invitation
from friendships.services import (
    get_friends,
    get_or_create_invite_link,
    get_received_requests,
    get_sent_requests,
)


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
    }
    return render(request, "social_hub/friend_management.html", context)


def shared_records(request):
    """공유 백엔드 연결 전 목록 UI 확인을 위한 임시 화면."""
    context = {
        "shared_records": [
            {
                "share_id": 1,
                "sender_name": "홍연우",
                "sender_character_static": "accounts/images/1.png",
                "record_id": 15,
                "record_date": "2026년 8월 7일",
                "main_emotion": "16",
                "main_emotion_name": "기쁨",
                "image_static": "records/images/main-character-writing.png",
                "content_preview": "오늘은 천천히 걸으며 좋아하는 풍경을 오래 바라봤어요.",
                "share_location": True,
                "place_name": "서울숲",
            },
            {
                "share_id": 2,
                "sender_name": "신은아",
                "sender_character_static": "accounts/images/3.png",
                "record_id": 16,
                "record_date": "2026년 8월 6일",
                "main_emotion": "15",
                "main_emotion_name": "행운",
                "image_static": "accounts/images/tutorial-record-write.png",
                "content_preview": "우연히 예쁜 골목을 발견해서 마음자국을 남겼어요.",
                "share_location": False,
                "place_name": "",
            },
            {
                "share_id": 3,
                "sender_name": "한지수",
                "sender_character_static": "accounts/images/5.png",
                "record_id": 17,
                "record_date": "2026년 8월 3일",
                "main_emotion": "05",
                "main_emotion_name": "만족",
                "image_static": "accounts/images/tutorial-calendar.png",
                "content_preview": "기다리던 일을 마무리해서 뿌듯했던 하루였어요.",
                "share_location": True,
                "place_name": "북서울꿈의숲",
            },
        ]
    }
    return render(request, "social_hub/shared_records.html", context)
