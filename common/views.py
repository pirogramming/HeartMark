from random import choice

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST


HOME_PROMPTS = (
    "오늘의 기분은 어때?",
    "특별하지 않아도 좋아, 오늘 하루는 어땠어?",
    "오늘 가장 기억에 남는 일은 뭐야?",
    "오늘은 어디를 다녀왔어?",
    "오늘 하루, 너를 웃게 만든 순간이 궁금해!",
    "오늘 다시 돌아가 보고 싶은 순간이 있어?",
    "지금 네 마음은 어떤 색과 닮았어?",
    "오늘 마음속에 오래 남은 말이 있어?",
    "오늘 놓아주고 싶은 마음이 있어?",
    "오늘 이야기를 천천히 들려줄래?",
    "가장 기억에 남는 장면을 기록해볼까?",
    "지금 마음의 날씨는 어떤가요?",
    "지친 마음도, 기쁜 마음도 여기에 다 털어놓아봐!",
    "오늘 남긴 발자국에는 어떤 기분이 담겼을까?",
    "지금 서 있는 이곳에 너만의 마음자국을 찍어봐!",
    "오늘 걸어온 길 끝에는 어떤 감정이 남아있니?",
)


@ensure_csrf_cookie
def home(request):
    selected_character_image = "5.png"
    show_onboarding_tutorial = False
    home_prompt = ""

    if request.user.is_authenticated:
        home_prompt = choice(HOME_PROMPTS)
        profile = getattr(request.user, "profile", None)
        if profile and profile.character_id:
            selected_character_image = f"{profile.character_id}.png"
            show_onboarding_tutorial = not profile.tutorial_completed

    return render(
        request,
        "common/home.html",
        {
            "selected_character_image": selected_character_image,
            "show_onboarding_tutorial": show_onboarding_tutorial,
            "home_prompt": home_prompt,
        },
    )


@login_required
@require_POST
def complete_home_tutorial(request):
    profile = getattr(request.user, "profile", None)
    if profile:
        profile.tutorial_completed = True
        profile.save(update_fields=["tutorial_completed", "updated_at"])
    return JsonResponse({"ok": True})
