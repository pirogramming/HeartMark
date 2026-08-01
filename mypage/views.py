from datetime import timedelta

from django.apps import apps
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils import timezone


def _get_record_model():
    """기록 브랜치가 합쳐진 뒤 Record 모델을 자동으로 연결합니다."""
    try:
        return apps.get_model("records", "Record")
    except LookupError:
        return None


def _get_character_url(user):
    """accounts의 캐릭터 규격이 확정되면 이 함수만 맞춰 수정합니다."""
    for relation_name in ("character", "selected_character"):
        try:
            character = getattr(user, relation_name, None)
        except Exception:
            character = None
        if not character:
            continue
        for image_name in ("image", "image_url"):
            image = getattr(character, image_name, None)
            if not image:
                continue
            return getattr(image, "url", image)
    return None


def _build_attendance(user):
    today = timezone.localdate()
    joined_at = user.date_joined
    if timezone.is_aware(joined_at):
        joined_at = timezone.localtime(joined_at)
    first_day = min(joined_at.date(), today)
    record_by_date = {}
    record_model = _get_record_model()

    if record_model is not None:
        try:
            records = record_model.objects.filter(
                user=user,
                created_at__date__gte=first_day,
                created_at__date__lte=today,
            ).order_by("-created_at")
            for record in records:
                record_day = timezone.localtime(record.created_at).date()
                record_by_date.setdefault(record_day, record)
        except Exception:
            # Record 규격이 합쳐지는 과정에서도 마이페이지 자체는 렌더링합니다.
            record_by_date = {}

    attendance_days = []
    elapsed_day_count = (today - first_day).days + 1
    slot_count = ((elapsed_day_count + 13) // 14) * 14
    for offset in range(slot_count):
        day = first_day + timedelta(days=offset)
        is_future = day > today
        record = None if is_future else record_by_date.get(day)
        emotion_number = None
        if record:
            emotions = getattr(record, "emotions", []) or []
            if emotions:
                try:
                    emotion_number = f"{int(emotions[0]):02d}"
                except (TypeError, ValueError):
                    emotion_number = None
        attendance_days.append({
            "date": day,
            "record": record,
            "emotion_number": emotion_number,
            "is_future": is_future,
        })
    return attendance_days, len(record_by_date)


@login_required
def mypage(request):
    if request.method == "POST":
        display_name = request.POST.get("display_name", "").strip()
        if display_name and len(display_name) <= 30:
            request.user.first_name = display_name
            request.user.save(update_fields=["first_name"])
        return redirect("mypage:home")

    attendance_days, attendance_count = _build_attendance(request.user)
    attendance_pages = []
    for start in range(0, len(attendance_days), 14):
        page_days = attendance_days[start:start + 14]
        attendance_pages.append({
            "days": page_days,
            "label": (
                f"{page_days[0]['date']:%m/%d} - {page_days[-1]['date']:%m/%d}"
            ),
        })
    return render(request, "mypage/mypage.html", {
        "attendance_pages": attendance_pages,
        "attendance_count": attendance_count,
        "character_url": _get_character_url(request.user),
    })
