from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import redirect, render


def login_view(request):
    if request.user.is_authenticated:
        return redirect("common:home")

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
                return redirect("common:home")

    return render(request, "accounts/login.html", {"errors": errors, "username": username})


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
            login(request, user)
            return redirect("common:home")

    return render(request, "accounts/signup.html", {"errors": errors, "username": username})


def logout_view(request):
    logout(request)
    return redirect("common:home")
