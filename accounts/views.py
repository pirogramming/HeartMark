from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import redirect, render

from .models import UserProfile


CHARACTER_CHOICES = [
    {"id": 1, "image": "1.png", "label": "초록 마음"},
    {"id": 2, "image": "2.png", "label": "노랑 기록"},
    {"id": 3, "image": "3.png", "label": "여행자"},
    {"id": 4, "image": "4.png", "label": "카메라"},
    {"id": 5, "image": "5.png", "label": "지도"},
]


def login_view(request):
    if request.user.is_authenticated:
        return redirect("accounts:post_login_redirect")

    errors = {}
    username = ""

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        if not username:
            errors["username"] = "아이디를 입력해주세요."
        if not password:
            errors["password"] = "비밀번호를 입력해주세요."

        if not errors:
            user = authenticate(request, username=username, password=password)

            if user is None:
                errors["password"] = "아이디 또는 비밀번호가 올바르지 않습니다."
            else:
                login(request, user)
                return redirect("accounts:post_login_redirect")

    return render(request, "accounts/login.html", {"errors": errors, "username": username})


@login_required(login_url="accounts:login")
def post_login_redirect_view(request):
    profile, _ = UserProfile.objects.get_or_create(
        user=request.user,
        defaults={"display_name": request.user.get_username()},
    )

    if not profile.display_name:
        profile.display_name = request.user.get_username()
        profile.save(update_fields=["display_name", "updated_at"])

    if not profile.onboarding_completed:
        return redirect("accounts:character_select")

    return redirect("common:home")


def signup_view(request):
    if request.user.is_authenticated:
        return redirect("common:home")

    errors = {}
    username = ""

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        password_confirm = request.POST.get("password_confirm", "")

        if not username:
            errors["username"] = "아이디를 입력해주세요."
        elif User.objects.filter(username=username).exists():
            errors["username"] = "이미 사용 중인 아이디입니다."

        if not password:
            errors["password"] = "비밀번호를 입력해주세요."
        elif len(password) < 8:
            errors["password"] = "비밀번호는 8자 이상이어야 합니다."

        if not password_confirm:
            errors["password_confirm"] = "비밀번호를 다시 입력해주세요."
        elif password != password_confirm:
            errors["password_confirm"] = "비밀번호가 일치하지 않습니다."

        if not errors:
            user = User.objects.create_user(username=username, password=password)
            UserProfile.objects.create(user=user, display_name=username)
            login(
                request,
                user,
                backend="django.contrib.auth.backends.ModelBackend",
            )
            return redirect("accounts:character_select")

    return render(request, "accounts/signup.html", {"errors": errors, "username": username})


@login_required(login_url="accounts:login")
def character_select_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user, defaults={"display_name": request.user.username})
    errors = {}
    is_editing = request.GET.get("edit") == "1"

    if profile.onboarding_completed and not is_editing:
        return redirect("common:home")

    if request.method == "POST":
        display_name = request.POST.get("display_name", "").strip()
        character_id = request.POST.get("character_id", "")

        if not display_name:
            errors["display_name"] = "프로필 이름을 입력해주세요."

        try:
            character_id = int(character_id)
        except ValueError:
            character_id = None

        if character_id not in [choice["id"] for choice in CHARACTER_CHOICES]:
            errors["character_id"] = "사용할 캐릭터를 선택해주세요."

        if not errors:
            profile.display_name = display_name
            profile.character_id = character_id
            profile.onboarding_completed = True
            profile.save()
            return redirect("common:home")

    selected_character = profile.character_id or 2
    display_name = profile.display_name or request.user.username

    return render(
        request,
        "accounts/character_select.html",
        {
            "characters": CHARACTER_CHOICES,
            "display_name": display_name,
            "selected_character": selected_character,
            "errors": errors,
        },
    )


def logout_view(request):
    logout(request)
    return redirect("common:home")
