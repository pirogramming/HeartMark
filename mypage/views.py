from collections import Counter
from datetime import timedelta

from django.apps import apps
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils import timezone


EMOTION_LABELS = {
    "01": "슬픔", "02": "애정", "03": "우울", "04": "분노",
    "05": "뿌듯함", "06": "불안", "07": "수줍음", "08": "못마땅함",
    "09": "놀람", "10": "눈물", "11": "화남", "12": "긴장",
    "13": "아픔", "14": "당황", "15": "편안함", "16": "행복",
    "17": "지루함", "18": "신남", "19": "추움", "20": "졸림",
}


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


def _record_day(record):
    created_at = getattr(record, "created_at", None)
    if created_at is None:
        return None
    if hasattr(created_at, "date"):
        if timezone.is_aware(created_at):
            created_at = timezone.localtime(created_at)
        return created_at.date()
    return created_at


def _record_emotion(record):
    main_emotion = getattr(record, "main_emotion", None)
    emotions = getattr(record, "emotions", []) or []
    value = main_emotion or (emotions[0] if emotions else None)
    if not value:
        return None
    try:
        return f"{int(value):02d}"
    except (TypeError, ValueError):
        return None


def _record_place_name(record):
    for field_name in ("place_name", "location_name"):
        value = getattr(record, field_name, None)
        if value:
            return str(value)

    for relation_name in ("place", "location"):
        try:
            place = getattr(record, relation_name, None)
        except Exception:
            place = None
        if not place:
            continue
        for field_name in ("name", "place_name", "address_name", "address"):
            value = getattr(place, field_name, None)
            if value:
                return str(value)
        label = str(place).strip()
        if label and label != "None":
            return label
    return None


def _get_user_records(user):
    record_model = _get_record_model()
    if record_model is None:
        return []
    try:
        return list(record_model.objects.filter(user=user).order_by("-created_at"))
    except Exception:
        return []


def _build_insights(records):
    today = timezone.localdate()
    week_start = today - timedelta(days=today.weekday())
    record_dates = {day for day in map(_record_day, records) if day}

    streak = 0
    cursor = today if today in record_dates else today - timedelta(days=1)
    while cursor in record_dates:
        streak += 1
        cursor -= timedelta(days=1)

    weekly_emotions = [
        emotion
        for record in records
        if (record_day := _record_day(record))
        and week_start <= record_day <= today
        and (emotion := _record_emotion(record))
    ]
    weekly_emotion = Counter(weekly_emotions).most_common(1)[0][0] if weekly_emotions else None

    place_names = [name for record in records if (name := _record_place_name(record))]
    frequent_place_data = Counter(place_names).most_common(1)[0] if place_names else None
    frequent_place = frequent_place_data[0] if frequent_place_data else None
    frequent_place_count = frequent_place_data[1] if frequent_place_data else 0

    if weekly_emotion:
        weekly_message = "이번 주에는 이 마음을 가장 자주 남겼어요. 내 마음을 천천히 돌아봐 주세요."
    else:
        weekly_message = "아직 이번 주에 남긴 마음이 없어요. 오늘의 마음자국을 남겨 볼까요?"

    return {
        "weekly_emotion": weekly_emotion,
        "weekly_emotion_label": EMOTION_LABELS.get(weekly_emotion, "대표 감정"),
        "weekly_message": weekly_message,
        "record_streak": streak,
        "total_record_count": len(records),
        "frequent_place": frequent_place,
        "frequent_place_count": frequent_place_count,
    }


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
                record_day = _record_day(record)
                if record_day is None:
                    continue
                record_by_date.setdefault(record_day, record)
        except Exception:
            # Record 규격이 합쳐지는 과정에서도 마이페이지 자체는 렌더링합니다.
            record_by_date = {}

    attendance_days = []
    elapsed_day_count = (today - first_day).days + 1
    # 오늘이 포함된 기간 다음의 미래 14일까지 탐색할 수 있게 한 페이지를 더 둡니다.
    slot_count = (((elapsed_day_count + 13) // 14) + 1) * 14
    for offset in range(slot_count):
        day = first_day + timedelta(days=offset)
        is_future = day > today
        record = None if is_future else record_by_date.get(day)
        emotion_number = None
        if record:
            emotion_number = _record_emotion(record)
        attendance_days.append({
            "date": day,
            "record": record,
            "emotion_number": emotion_number,
            "is_future": is_future,
            "is_today": day == today,
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

    user_records = _get_user_records(request.user)
    insights = _build_insights(user_records)
    attendance_days, attendance_count = _build_attendance(request.user)
    attendance_pages = []
    current_page_index = 0
    for start in range(0, len(attendance_days), 14):
        page_days = attendance_days[start:start + 14]
        if any(day["is_today"] for day in page_days):
            current_page_index = len(attendance_pages)
        attendance_pages.append({
            "days": page_days,
            "label": (
                f"{page_days[0]['date']:%m/%d} - {page_days[-1]['date']:%m/%d}"
            ),
        })
    context = {
        "attendance_pages": attendance_pages,
        "attendance_count": attendance_count,
        "current_page_index": current_page_index,
        "character_url": _get_character_url(request.user),
        **insights,
    }
    return render(request, "mypage/mypage.html", context)
