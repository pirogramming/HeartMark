from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST


@ensure_csrf_cookie
def home(request):
    selected_character_image = "5.png"
    show_onboarding_tutorial = False

    if request.user.is_authenticated:
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
