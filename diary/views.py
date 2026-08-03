# 담당 D: 캘린더 및 다이어리 목록 조회

from collections import Counter
from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django.utils import timezone

# 담당 C가 만든 실제 기록 모델을 가져옵니다.
from records.models import Record


# ============================================================
# 감정 번호별 표시 이름
# ============================================================

EMOTION_NAME_MAP = {
    1: "슬픔",
    2: "사랑",
    3: "따분",
    4: "예민",
    5: "만족",
    6: "슬픔",
    7: "짝사랑",
    8: "심술",
    9: "당황",
    10: "슬픔",
    11: "화남",
    12: "신남",
    13: "아픔",
    14: "놀람",
    15: "행운",
    16: "기쁨",
    17: "질투",
    18: "맛있어!",
    19: "냉철",
    20: "졸림",
}


def get_emotion_name(emotion_number):
    """
    감정 번호를 화면에 표시할 감정 이름으로 변환합니다.

    예:
    1 → "슬픔"
    7 → "짝사랑"
    """

    try:
        # JSONField 값이나 폼 값이 문자열일 수도 있으므로
        # 비교하기 전에 정수로 변환합니다.
        emotion_number = int(emotion_number)

    except (TypeError, ValueError):
        # 값이 없거나 숫자로 바꿀 수 없다면 빈 문자열을 반환합니다.
        return ""

    return EMOTION_NAME_MAP.get(
        emotion_number,
        f"감정 {emotion_number}",
    )


@login_required
def diary_list(request):
    """
    현재 로그인한 사용자가 작성한 실제 Record를 조회하여
    전체 / 감정별 / 장소별 목록 페이지에 전달합니다.
    """

    # ========================================================
    # 1. 현재 선택한 탭과 필터값
    # ========================================================

    selected_tab = request.GET.get("tab", "all")
    selected_sort = request.GET.get("sort", "latest")

    selected_start_date = request.GET.get("start_date", "")
    selected_end_date = request.GET.get("end_date", "")

    if selected_tab not in {"all", "emotion", "location"}:
        selected_tab = "all"

    # ========================================================
    # 2. 현재 사용자의 실제 기록 조회
    # ========================================================

    records_queryset = Record.objects.filter(
        user=request.user,
    )

    # ========================================================
    # 3. 시작일 필터
    # ========================================================

    if selected_start_date:
        try:
            start_date = datetime.strptime(
                selected_start_date,
                "%Y-%m-%d",
            ).date()

            records_queryset = records_queryset.filter(
                created_at__date__gte=start_date,
            )

        except ValueError:
            selected_start_date = ""

    # ========================================================
    # 4. 종료일 필터
    # ========================================================

    if selected_end_date:
        try:
            end_date = datetime.strptime(
                selected_end_date,
                "%Y-%m-%d",
            ).date()

            records_queryset = records_queryset.filter(
                created_at__date__lte=end_date,
            )

        except ValueError:
            selected_end_date = ""

    # ========================================================
    # 5. 정렬
    # ========================================================

    if selected_sort == "oldest":
        records_queryset = records_queryset.order_by(
            "created_at",
        )

    else:
        selected_sort = "latest"

        records_queryset = records_queryset.order_by(
            "-created_at",
        )

    records = list(records_queryset)

    # ========================================================
    # 6. 각 기록에 화면용 감정 이름 추가
    # ========================================================

    for record in records:
        record.main_emotion_name = get_emotion_name(
            record.main_emotion,
        )

    # ========================================================
    # 7. 감정별 기록 횟수 계산
    # ========================================================

    main_emotion_numbers = [
        int(record.main_emotion)
        for record in records
        if record.main_emotion
    ]

    emotion_counts = Counter(
        main_emotion_numbers,
    )

    emotions = []

    for emotion_id, emotion_name in EMOTION_NAME_MAP.items():
        record_count = emotion_counts.get(
            emotion_id,
            0,
        )

        if record_count >= 5:
            size = "large"

        elif record_count >= 2:
            size = "medium"

        else:
            size = "small"

        emotions.append(
            {
                "id": emotion_id,
                "name": emotion_name,
                "record_count": record_count,
                "size": size,
            }
        )

    recorded_emotions = [
        emotion
        for emotion in emotions
        if emotion["record_count"] > 0
    ]

    if recorded_emotions:
        top_emotion = max(
            recorded_emotions,
            key=lambda emotion: emotion["record_count"],
        )

    else:
        top_emotion = None

    # ========================================================
    # 8. 서울 지도용 장소 데이터 계산
    # ========================================================

    district_records = {}

    for record in records:
        place_name = (
            record.place_name.strip()
            if record.place_name
            else ""
        )

        if not place_name.endswith("구"):
            continue

        district_name = place_name
        emotion_name = record.main_emotion_name

        if not emotion_name:
            continue

        if district_name not in district_records:
            district_records[district_name] = []

        district_records[district_name].append(
            {
                "emotion_name": emotion_name,
                "created_at": record.created_at,
            }
        )

    district_map_data = []

    for district_name, district_record_list in district_records.items():
        emotion_names = [
            item["emotion_name"]
            for item in district_record_list
        ]

        emotion_name_counts = Counter(
            emotion_names,
        )

        dominant_emotion = emotion_name_counts.most_common(1)[0][0]

        latest_record = max(
            district_record_list,
            key=lambda item: item["created_at"],
        )

        district_map_data.append(
            {
                "district_name": district_name,
                "visit_count": len(district_record_list),
                "dominant_emotion": dominant_emotion,
                "latest_emotion": latest_record["emotion_name"],
            }
        )

    # ========================================================
    # 9. 장소별 기록 횟수 계산
    # ========================================================

    location_counts = Counter(
        record.place_name
        for record in records
        if record.place_name
    )

    locations = [
        {
            "name": place_name,
            "record_count": count,
        }
        for place_name, count in location_counts.items()
    ]

    locations.sort(
        key=lambda location: location["record_count"],
        reverse=True,
    )

    # ========================================================
    # 10. 템플릿에 데이터 전달
    # ========================================================

    context = {
        "records": records,
        "emotions": emotions,
        "top_emotion": top_emotion,
        "locations": locations,
        "district_map_data": district_map_data,

        "selected_tab": selected_tab,
        "selected_sort": selected_sort,
        "selected_start_date": selected_start_date,
        "selected_end_date": selected_end_date,

        "selected_emotion": request.GET.get(
            "emotion",
            "",
        ),
        "selected_location": request.GET.get(
            "location",
            "",
        ),
    }

    return render(
        request,
        "diary/list.html",
        context,
    )


@login_required
def emotion_calendar(request):
    """
    현재 로그인한 사용자의 기록을 날짜별로 정리하여
    감정 캘린더 페이지에 전달합니다.

    같은 날짜에 기록이 여러 개 있다면
    가장 최근에 작성한 기록의 대표 감정을 사용합니다.
    """

    # 오늘 날짜를 기준으로 캘린더의 최초 연도와 월을 설정합니다.
    today = timezone.localdate()

    # 최신 기록부터 조회합니다.
    #
    # 아래에서 날짜별 데이터에 처음 들어간 기록만 사용하므로
    # 같은 날짜에 여러 기록이 있으면 가장 최신 기록이 남습니다.
    records = Record.objects.filter(
        user=request.user,
    ).order_by(
        "-created_at",
    )

    # JavaScript에 전달할 날짜별 감정 데이터입니다.
    #
    # 결과 예:
    # {
    #     "2026-08-01": {
    #         "number": 7,
    #         "name": "짝사랑",
    #         "image_name": "emotion-07.png"
    #     }
    # }
    calendar_emotions = {}

    for record in records:
        # created_at이 시간대 정보를 가진 경우
        # 한국 시간 기준 날짜로 변환합니다.
        created_date = timezone.localtime(
            record.created_at,
        ).date()

        date_key = created_date.strftime(
            "%Y-%m-%d",
        )

        # 이미 같은 날짜의 최신 기록이 저장되어 있다면
        # 그보다 오래된 기록은 건너뜁니다.
        if date_key in calendar_emotions:
            continue

        try:
            emotion_number = int(
                record.main_emotion,
            )

        except (TypeError, ValueError):
            continue

        calendar_emotions[date_key] = {
            # 감정 이미지 번호
            "number": emotion_number,

            # 이미지의 대체 텍스트와 툴팁에 사용할 감정 이름
            "name": get_emotion_name(
                emotion_number,
            ),

            # 실제 records 이미지 폴더의 파일명
            "image_name": (
                f"emotion-{emotion_number:02d}.png"
            ),

            # 날짜 칸이나 감정 이미지를 눌렀을 때
            # 해당 기록 상세 페이지로 이동할 때 사용할 ID
            "record_id": record.pk,
        }

    context = {
        # 최초 화면에 표시할 연도와 월
        "calendar_year": today.year,
        "calendar_month": today.month,

        # calendar.html의 json_script를 통해
        # JavaScript에 안전하게 전달됩니다.
        "calendar_emotions": calendar_emotions,
    }

    return render(
        request,
        "diary/calendar.html",
        context,
    )

@login_required
def diary_detail(request, pk):
    """
    다이어리 상세 페이지입니다.

    주소 예:
    /diary/5/

    현재 로그인한 사용자의
    id가 5인 기록만 조회합니다.
    """

    record = get_object_or_404(
        Record,
        pk=pk,
        user=request.user,
    )

    # 대표 감정 번호
    main_emotion_number = int(
        record.main_emotion,
    )

    # 대표 감정 정보
    main_emotion = {
        "number": main_emotion_number,
        "name": get_emotion_name(
            main_emotion_number,
        ),
        "image_name": (
            f"emotion-{main_emotion_number:02d}.png"
        ),
    }

    # 대표 감정을 제외한 보조 감정 목록
    secondary_emotions = []

    for emotion_number in record.emotions:
        try:
            emotion_number = int(
                emotion_number,
            )

        except (TypeError, ValueError):
            continue

        if emotion_number == main_emotion_number:
            continue

        secondary_emotions.append(
            {
                "number": emotion_number,
                "name": get_emotion_name(
                    emotion_number,
                ),
                "image_name": (
                    f"emotion-{emotion_number:02d}.png"
                ),
            }
        )

    # 첫 번째 보조 감정
    left_emotion = (
        secondary_emotions[0]
        if len(secondary_emotions) >= 1
        else None
    )

    # 두 번째 보조 감정
    right_emotion = (
        secondary_emotions[1]
        if len(secondary_emotions) >= 2
        else None
    )

    context = {
        "record": record,
        "main_emotion": main_emotion,
        "left_emotion": left_emotion,
        "right_emotion": right_emotion,
    }

    return render(
        request,
        "diary/detail.html",
        context,
    )