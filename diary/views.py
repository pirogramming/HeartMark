# 담당 D: 캘린더 및 다이어리 목록 조회

from collections import Counter
from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

# 담당 C가 만든 실제 기록 모델을 가져옵니다.
from records.models import Record


# ============================================================
# 감정 번호별 표시 이름
# ============================================================
#
# 현재 records 앱에서는 감정을 실제 이름이 아니라
# 1~20 사이의 숫자로 저장하고 있습니다.
#
# 예:
# record.main_emotion = 3
# record.emotions = [3, 7, 11]
#
# 그런데 담당 C의 forms.py에도 실제 감정 이름이 없고
# "감정 1", "감정 2"처럼만 정의되어 있습니다.
#
# 따라서 실제 감정 이름과 번호 순서가 확정되면
# 아래 값만 수정하면 됩니다.
#
EMOTION_NAME_MAP = {
    1: "감정 1",
    2: "감정 2",
    3: "감정 3",
    4: "감정 4",
    5: "감정 5",
    6: "감정 6",
    7: "감정 7",
    8: "감정 8",
    9: "감정 9",
    10: "감정 10",
    11: "감정 11",
    12: "감정 12",
    13: "감정 13",
    14: "감정 14",
    15: "감정 15",
    16: "감정 16",
    17: "감정 17",
    18: "감정 18",
    19: "감정 19",
    20: "감정 20",
}


def get_emotion_name(emotion_number):
    """
    감정 번호를 화면에 표시할 감정 이름으로 변환합니다.

    예:
    1 → 감정 1
    5 → 감정 5

    실제 감정 이름이 정해지면 EMOTION_NAME_MAP만 수정하면 됩니다.
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

    # 주소 예:
    # /diary/?tab=all
    # /diary/?tab=emotion
    # /diary/?tab=location
    selected_tab = request.GET.get("tab", "all")

    # 최신순 또는 과거순
    selected_sort = request.GET.get("sort", "latest")

    # 기간 필터
    selected_start_date = request.GET.get("start_date", "")
    selected_end_date = request.GET.get("end_date", "")

    # 허용하지 않은 탭 이름이 들어오면 전체 탭으로 변경합니다.
    if selected_tab not in {"all", "emotion", "location"}:
        selected_tab = "all"

    # ========================================================
    # 2. 현재 사용자의 실제 기록 조회
    # ========================================================

    # user=request.user가 없으면 다른 사용자의 기록도 함께 나올 수 있습니다.
    records_queryset = Record.objects.filter(
        user=request.user,
    )

    # ========================================================
    # 3. 시작일 필터
    # ========================================================

    if selected_start_date:
        try:
            # HTML의 date input 값은 "2026-08-03" 형태로 전달됩니다.
            start_date = datetime.strptime(
                selected_start_date,
                "%Y-%m-%d",
            ).date()

            # 시작일 당일을 포함해 그 이후의 기록만 남깁니다.
            records_queryset = records_queryset.filter(
                created_at__date__gte=start_date,
            )

        except ValueError:
            # 잘못된 날짜 문자열이면 필터값을 비웁니다.
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

            # 종료일 당일을 포함해 그 이전의 기록만 남깁니다.
            records_queryset = records_queryset.filter(
                created_at__date__lte=end_date,
            )

        except ValueError:
            selected_end_date = ""

    # ========================================================
    # 5. 정렬
    # ========================================================

    if selected_sort == "oldest":
        # 오래된 기록이 위로 오도록 정렬합니다.
        records_queryset = records_queryset.order_by(
            "created_at",
        )

    else:
        # 이상한 값이 들어오면 최신순으로 처리합니다.
        selected_sort = "latest"

        # 최근 기록이 위로 오도록 정렬합니다.
        records_queryset = records_queryset.order_by(
            "-created_at",
        )

    # QuerySet을 리스트로 변환합니다.
    #
    # 아래에서 감정 집계, 장소 집계 등으로 여러 번 반복해서 쓰므로
    # 한 번 조회한 결과를 재사용합니다.
    records = list(records_queryset)

    # ========================================================
    # 6. 각 기록에 화면용 감정 이름 추가
    # ========================================================
    #
    # Record 모델에는 main_emotion_name이라는 실제 필드가 없습니다.
    # 데이터베이스에는 저장하지 않고, 화면 표시용으로만
    # 파이썬 객체에 임시 속성을 추가합니다.
    #
    for record in records:
        record.main_emotion_name = get_emotion_name(
            record.main_emotion,
        )

    # ========================================================
    # 7. 감정별 기록 횟수 계산
    # ========================================================

    # 현재 기록들의 대표 감정 번호를 모읍니다.
    main_emotion_numbers = [
        int(record.main_emotion)
        for record in records
        if record.main_emotion
    ]

    # 예:
    # [1, 1, 3, 5, 1]
    # → Counter({1: 3, 3: 1, 5: 1})
    emotion_counts = Counter(
        main_emotion_numbers,
    )

    emotions = []

    for emotion_id, emotion_name in EMOTION_NAME_MAP.items():
        # 해당 감정이 대표 감정으로 사용된 횟수입니다.
        record_count = emotion_counts.get(
            emotion_id,
            0,
        )

        # 감정 조약돌 크기 결정
        #
        # 이 숫자를 변경하면 각 조약돌의 크기 기준이 바뀝니다.
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

    # 기록 횟수가 1개 이상인 감정만 따로 모읍니다.
    recorded_emotions = [
        emotion
        for emotion in emotions
        if emotion["record_count"] > 0
    ]

    # 가장 많이 기록한 감정을 찾습니다.
    if recorded_emotions:
        top_emotion = max(
            recorded_emotions,
            key=lambda emotion: emotion["record_count"],
        )

    else:
        # 작성한 기록이 아직 없으면 None으로 전달합니다.
        top_emotion = None

    # ========================================================
    # 8. 서울 지도용 장소 데이터 계산
    # ========================================================
    #
    # 현재 Record 모델에는 장소 ForeignKey나 district 필드가 없고
    # place_name 문자열만 존재합니다.
    #
    # 그래서 현재 단계에서는 place_name이 정확히
    # "성북구", "강남구"처럼 '구'로 끝나는 경우만
    # 서울 지도 데이터로 사용할 수 있습니다.
    #
    district_records = {}

    for record in records:
        place_name = (
            record.place_name.strip()
            if record.place_name
            else ""
        )

        # "성북구", "마포구" 같은 값만 지도에 표시합니다.
        #
        # "성신여대입구역", "명동 카페" 등은
        # 어느 자치구인지 알 수 없어 지도에서는 제외됩니다.
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
        # 해당 구에서 기록된 대표 감정 이름 목록
        emotion_names = [
            item["emotion_name"]
            for item in district_record_list
        ]

        # 가장 많이 기록한 감정을 계산합니다.
        emotion_name_counts = Counter(
            emotion_names,
        )

        dominant_emotion = emotion_name_counts.most_common(1)[0][0]

        # 해당 구의 가장 최근 기록을 찾습니다.
        latest_record = max(
            district_record_list,
            key=lambda item: item["created_at"],
        )

        district_map_data.append(
            {
                # 지도 SVG의 구 이름과 비교되는 값
                "district_name": district_name,

                # 해당 구에서 작성한 기록 개수
                "visit_count": len(district_record_list),

                # 해당 구에서 가장 많이 기록한 감정
                "dominant_emotion": dominant_emotion,

                # 해당 구에서 가장 최근에 기록한 감정
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

    # 기록이 많은 장소부터 정렬합니다.
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