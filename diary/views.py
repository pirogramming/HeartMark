# 담당 D: 캘린더 및 다이어리 목록 조회

from datetime import date
from django.shortcuts import render
from collections import Counter

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
                "name": "슬픔",
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
                "name": "분노",
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

    district_records = {}

    for record in records:
        location = record.get("location")
        emotion = record.get("emotion")
        created_at = record.get("created_at")

        if not location or not emotion:
            continue

        district_name = location.get("name")
        emotion_name = emotion.get("name")

        if not district_name or not emotion_name:
            continue

        # 서울 자치구만 지도에 표시
        if not district_name.endswith("구"):
            continue

        if district_name not in district_records:
            district_records[district_name] = []

        district_records[district_name].append({
            "emotion_name": emotion_name,
            "created_at": created_at,
        })


    district_map_data = []

    for district_name, district_record_list in district_records.items():
        emotion_names = [
            item["emotion_name"]
            for item in district_record_list
        ]

        emotion_counts = Counter(emotion_names)
        dominant_emotion = emotion_counts.most_common(1)[0][0]

        latest_record = max(
            district_record_list,
            key=lambda item: item["created_at"]
        )

        district_map_data.append({
            "district_name": district_name,
            "visit_count": len(district_record_list),
            "dominant_emotion": dominant_emotion,
            "latest_emotion": latest_record["emotion_name"],
        })

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
        "district_map_data": district_map_data,
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