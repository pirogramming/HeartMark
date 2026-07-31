# 담당 D: 캘린더 및 다이어리 목록 조회

from datetime import date
from django.shortcuts import render


def diary_list(request):
    selected_tab = request.GET.get("tab", "all")
    selected_sort = request.GET.get("sort", "latest")
    selected_start_date = request.GET.get("start_date", "")
    selected_end_date = request.GET.get("end_date", "")

    records = [
        {
            "id": 1,
            "title": "2차 회의한 날",
            "created_at": date(2026, 7, 30),
            "image": None,
            "emotion": {
                "id": 1,
                "name": "설렘",
                "image": None,
            },
            "location": {
                "id": 1,
                "name": "성북구",
            },
        },
        {
            "id": 2,
            "title": "친구랑 카페에서 수다",
            "created_at": date(2026, 7, 29),
            "image": None,
            "emotion": {
                "id": 2,
                "name": "행복",
                "image": None,
            },
            "location": {
                "id": 2,
                "name": "마포구",
            },
        },
        {
            "id": 3,
            "title": "산책하면서 많은 생각을 했다",
            "created_at": date(2026, 7, 28),
            "image": None,
            "emotion": {
                "id": 3,
                "name": "평온",
                "image": None,
            },
            "location": {
                "id": 3,
                "name": "성동구",
            },
        },
        {
            "id": 4,
            "title": "작은 성공! 뿌듯한 하루",
            "created_at": date(2026, 7, 27),
            "image": None,
            "emotion": {
                "id": 4,
                "name": "뿌듯함",
                "image": None,
            },
            "location": {
                "id": 1,
                "name": "성북구",
            },
        },
        {
            "id": 5,
            "title": "노을이 너무 예뻤다",
            "created_at": date(2026, 7, 26),
            "image": None,
            "emotion": {
                "id": 2,
                "name": "행복",
                "image": None,
            },
            "location": {
                "id": 4,
                "name": "강남구",
            },
        },
        {
            "id": 6,
            "title": "마음이 편안했던 날",
            "created_at": date(2026, 7, 25),
            "image": None,
            "emotion": {
                "id": 3,
                "name": "평온",
                "image": None,
            },
            "location": {
                "id": 4,
                "name": "강남구",
            },
        },
        {
            "id": 7,
            "title": "집에서 푹 쉬었다",
            "created_at": date(2026, 7, 23),
            "image": None,
            "emotion": {
                "id": 5,
                "name": "지침",
                "image": None,
            },
            "location": {
                "id": 2,
                "name": "마포구",
            },
        },
        {
            "id": 8,
            "title": "왜인지 모르게 우울했다",
            "created_at": date(2026, 7, 22),
            "image": None,
            "emotion": {
                "id": 6,
                "name": "슬픔",
                "image": None,
            },
            "location": {
                "id": 5,
                "name": "명동",
            },
        },
    ]

    emotions = [
        {
            "id": 1,
            "name": "감사",
            "record_count": 8,
            "size": "large",
        },
        {
            "id": 2,
            "name": "설렘",
            "record_count": 6,
            "size": "large",
        },
        {
            "id": 3,
            "name": "행복",
            "record_count": 4,
            "size": "medium",
        },
        {
            "id": 4,
            "name": "기대",
            "record_count": 3,
            "size": "medium",
        },
        {
            "id": 5,
            "name": "불안",
            "record_count": 2,
            "size": "small",
        },
        {
            "id": 6,
            "name": "평온",
            "record_count": 4,
            "size": "medium",
        },
        {
            "id": 7,
            "name": "뿌듯",
            "record_count": 3,
            "size": "medium",
        },
        {
            "id": 8,
            "name": "지침",
            "record_count": 2,
            "size": "small",
        },
    ]

    locations = [
        {"id": 1, "name": "성북구", "record_count": 2},
        {"id": 2, "name": "마포구", "record_count": 2},
        {"id": 3, "name": "성동구", "record_count": 1},
        {"id": 4, "name": "강남구", "record_count": 2},
        {"id": 5, "name": "명동", "record_count": 1},
    ]

    if selected_sort == "oldest":
        records.sort(key=lambda record: record["created_at"])
    else:
        records.sort(
            key=lambda record: record["created_at"],
            reverse=True,
        )

    context = {
        "records": records,
        "emotions": emotions,
        "locations": locations,
        "selected_tab": selected_tab,
        "selected_sort": selected_sort,
        "selected_start_date": selected_start_date,
        "selected_end_date": selected_end_date,
        "selected_emotion": request.GET.get("emotion", ""),
        "selected_location": request.GET.get("location", ""),
    }

    return render(request, "diary/list.html", context)