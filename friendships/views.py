from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.templatetags.static import static
from django.urls import reverse
from django.utils.http import urlencode

from .models import Invitation
from .services import (
    FriendshipError,
    accept_invitation,
    delete_friend,
    get_friends,
    get_or_create_invite_link,
    get_received_requests,
    get_sent_requests,
    reject_invitation,
    send_friend_request,
)


def _display_name(user):
    profile = getattr(user, "profile", None)
    if profile and profile.display_name:
        return profile.display_name
    return user.first_name or user.username


def _character_url(user):
    profile = getattr(user, "profile", None)
    character_id = getattr(profile, "character_id", None)
    if character_id not in range(1, 6):
        character_id = 2
    return static(f"accounts/images/{character_id}.png")


def _login_redirect(request):
    next_url = request.get_full_path()
    query = urlencode({"next": next_url})
    return redirect(f"{reverse('accounts:login')}?{query}")


@login_required(login_url="accounts:login")
def invite_link(request):
    invitation, created = get_or_create_invite_link(request.user)
    invite_url = request.build_absolute_uri(
        reverse("friendships:invite_detail", kwargs={"code": invitation.code})
    )
    if request.method == "POST":
        messages.success(request, "친구 초대 링크를 준비했어요.")
        return redirect("friendships:invite_link")
    return render(
        request,
        "friendships/invite_link.html",
        {
            "invitation": invitation,
            "invite_url": invite_url,
            "created": created,
        },
    )


def invite_detail(request, code):
    invitation = get_object_or_404(
        Invitation.objects.select_related("inviter", "invitee"),
        code=code,
    )
    if not request.user.is_authenticated:
        return _login_redirect(request)

    error = None
    if request.method == "POST":
        action = request.POST.get("action")
        try:
            if action == "accept":
                accept_invitation(invitation, request.user)
                messages.success(request, "친구가 되었어요.")
                return redirect("social_hub:friend_management")
            if action == "reject":
                reject_invitation(invitation, request.user)
                messages.info(request, "친구 요청을 거절했어요.")
                return redirect("common:home")
            error = "알 수 없는 요청입니다."
        except FriendshipError as exc:
            error = str(exc)

    return render(
        request,
        "friendships/invite_detail.html",
        {
            "invitation": invitation,
            "inviter_name": _display_name(invitation.inviter),
            "inviter_character_url": _character_url(invitation.inviter),
            "error": error,
        },
    )


@login_required(login_url="accounts:login")
def friend_list(request):
    return redirect("social_hub:friend_management")


@login_required(login_url="accounts:login")
def send_request(request, user_id):
    target = get_object_or_404(get_user_model(), pk=user_id)
    if request.method != "POST":
        return redirect("friendships:list")
    try:
        send_friend_request(request.user, target)
        messages.success(request, "친구 요청을 보냈어요.")
    except FriendshipError as exc:
        messages.error(request, str(exc))
    return redirect(request.POST.get("next") or "social_hub:friend_management")


@login_required(login_url="accounts:login")
def respond_request(request, pk, action):
    invitation = get_object_or_404(Invitation, pk=pk)
    if request.method != "POST":
        return redirect("friendships:list")
    try:
        if action == "accept":
            accept_invitation(invitation, request.user)
            messages.success(request, "친구 요청을 수락했어요.")
        elif action == "reject":
            reject_invitation(invitation, request.user)
            messages.info(request, "친구 요청을 거절했어요.")
        else:
            messages.error(request, "알 수 없는 요청입니다.")
    except FriendshipError as exc:
        messages.error(request, str(exc))
    return redirect("social_hub:friend_management")


@login_required(login_url="accounts:login")
def friend_delete(request, user_id):
    friend = get_object_or_404(get_user_model(), pk=user_id)
    if request.method == "POST":
        try:
            delete_friend(request.user, friend)
            messages.info(request, "친구를 삭제했어요.")
        except FriendshipError as exc:
            messages.error(request, str(exc))
    return redirect("social_hub:friend_management")
