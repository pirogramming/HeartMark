from django.shortcuts import render


def home(request):
    selected_character_image = "5.png"

    if request.user.is_authenticated:
        profile = getattr(request.user, "profile", None)
        if profile and profile.character_id:
            selected_character_image = f"{profile.character_id}.png"

    return render(request, "common/home.html", {"selected_character_image": selected_character_image})
