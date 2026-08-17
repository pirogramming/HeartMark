# 담당 D: 캘린더 및 다이어리 목록 조회

from collections import Counter
from datetime import datetime, timedelta

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django.utils import timezone

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


# ============================================================
# 감정 번호별 색상 그룹
# ============================================================

EMOTION_COLOR_GROUP_MAP = {
    1: "blue",
    2: "pink",
    3: "purple",
    4: "purple",
    5: "yellow",
    6: "blue",
    7: "pink",
    8: "red",
    9: "orange",
    10: "blue",
    11: "red",
    12: "yellow",
    13: "blue",
    14: "orange",
    15: "yellow",
    16: "yellow",
    17: "red",
    18: "yellow",
    19: "purple",
    20: "purple",
}


# ============================================================
# 감정 번호 → 감정 이름
# ============================================================

def get_emotion_name(emotion_number):
    """
    감정 번호를 화면에 표시할 이름으로 변환함.
    """

    try:
        emotion_number = int(
            emotion_number,
        )

    except (TypeError, ValueError):
        return ""

    return EMOTION_NAME_MAP.get(
        emotion_number,
        f"감정 {emotion_number}",
    )


# ============================================================
# 감정 번호 → 색상 그룹
# ============================================================

def get_emotion_color_group(emotion_number):
    """
    감정 번호를 그래프용 색상 그룹으로 변환함.
    """

    try:
        emotion_number = int(
            emotion_number,
        )

    except (TypeError, ValueError):
        return "default"

    return EMOTION_COLOR_GROUP_MAP.get(
        emotion_number,
        "default",
    )


# ============================================================
# 전체 / 감정별 / 장소별 기록
# ============================================================

@login_required
def diary_list(request):
    """
    현재 로그인한 사용자의 기록을 조회하여
    전체 / 감정별 / 장소별 목록 페이지에 전달함.
    """

    # ========================================================
    # 1. 탭과 필터값
    # ========================================================

    selected_tab = request.GET.get(
        "tab",
        "all",
    )

    selected_sort = request.GET.get(
        "sort",
        "latest",
    )

    selected_start_date = request.GET.get(
        "start_date",
        "",
    )

    selected_end_date = request.GET.get(
        "end_date",
        "",
    )


    if selected_tab not in {
        "all",
        "emotion",
        "location",
    }:
        selected_tab = "all"


    # ========================================================
    # 2. 현재 사용자의 기록 조회
    # ========================================================

    records_queryset = (
        Record.objects
        .filter(
            user=request.user,
        )
        .select_related(
            "place",
        )
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

            records_queryset = (
                records_queryset.filter(
                    created_at__date__gte=start_date,
                )
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

            records_queryset = (
                records_queryset.filter(
                    created_at__date__lte=end_date,
                )
            )

        except ValueError:
            selected_end_date = ""


    # ========================================================
    # 5. 기록 정렬
    # ========================================================

    if selected_sort == "oldest":

        records_queryset = (
            records_queryset.order_by(
                "created_at",
            )
        )

    else:
        selected_sort = "latest"

        records_queryset = (
            records_queryset.order_by(
                "-created_at",
            )
        )


    # 여러 번 반복 사용하므로 리스트로 변환함.
    records = list(
        records_queryset,
    )


    # ========================================================
    # 6. 화면용 대표 감정 정보 추가
    # ========================================================

    for record in records:

        record.main_emotion_name = (
            get_emotion_name(
                record.main_emotion,
            )
        )

        record.main_emotion_color_group = (
            get_emotion_color_group(
                record.main_emotion,
            )
        )


    # ========================================================
    # 7. 대표 감정별 기록 횟수
    # ========================================================

    main_emotion_numbers = []


    for record in records:

        try:
            emotion_number = int(
                record.main_emotion,
            )

        except (TypeError, ValueError):
            continue


        main_emotion_numbers.append(
            emotion_number,
        )


    emotion_counts = Counter(
        main_emotion_numbers,
    )


    # ========================================================
    # 8. 전체 감정 목록 생성
    # ========================================================

    emotions = []


    for (
        emotion_id,
        emotion_name,
    ) in EMOTION_NAME_MAP.items():

        record_count = emotion_counts.get(
            emotion_id,
            0,
        )


        emotions.append(
            {
                "id": emotion_id,

                "name": emotion_name,

                "record_count": record_count,

                "color_group": (
                    get_emotion_color_group(
                        emotion_id,
                    )
                ),
            }
        )


    # ========================================================
    # 9. 실제 기록된 감정만 추림
    # ========================================================

    recorded_emotions = [
        emotion
        for emotion in emotions
        if emotion["record_count"] > 0
    ]


    recorded_emotions.sort(
        key=lambda emotion: (
            emotion["record_count"]
        ),
        reverse=True,
    )


    # ========================================================
    # 10. 가장 많이 기록된 감정
    # ========================================================

    if recorded_emotions:

        maximum_emotion_count = max(
            emotion["record_count"]
            for emotion in recorded_emotions
        )


        top_emotions = [
            emotion
            for emotion in recorded_emotions
            if (
                emotion["record_count"]
                == maximum_emotion_count
            )
        ]

    else:
        top_emotions = []


    # ========================================================
    # 11. 도넛 그래프용 색상 그룹
    # ========================================================

    emotion_chart_group_dict = {}


    for emotion in recorded_emotions:

        color_group = emotion[
            "color_group"
        ]

        emotion_name = emotion[
            "name"
        ]

        record_count = emotion[
            "record_count"
        ]


        if (
            color_group
            not in emotion_chart_group_dict
        ):

            emotion_chart_group_dict[
                color_group
            ] = {
                "color_group": color_group,

                "record_count": 0,

                "emotion_names": [],
            }


        emotion_chart_group_dict[
            color_group
        ]["record_count"] += record_count


        if (
            emotion_name
            not in emotion_chart_group_dict[
                color_group
            ]["emotion_names"]
        ):

            emotion_chart_group_dict[
                color_group
            ]["emotion_names"].append(
                emotion_name,
            )


    emotion_chart_groups = list(
        emotion_chart_group_dict.values()
    )


    # ========================================================
    # 12. 전체 대표 감정 기록 수
    # ========================================================

    total_record_count = sum(
        emotion["record_count"]
        for emotion in recorded_emotions
    )


    # ========================================================
    # 13. 서울 지도용 장소 데이터
    # ========================================================

    district_records = {}


    for record in records:

        if not record.place:
            continue


        district_name = (
            record.place.district.strip()
            if record.place.district
            else ""
        )


        if not district_name:
            continue


        emotion_name = (
            record.main_emotion_name
        )


        if not emotion_name:
            continue


        if (
            district_name
            not in district_records
        ):
            district_records[
                district_name
            ] = []


        district_records[
            district_name
        ].append(
            {
                "emotion_name": emotion_name,

                "created_at": (
                    record.created_at
                ),
            }
        )


    district_map_data = []


    for (
        district_name,
        district_record_list,
    ) in district_records.items():

        emotion_names = [
            item["emotion_name"]
            for item in district_record_list
        ]


        emotion_name_counts = Counter(
            emotion_names,
        )


        dominant_emotion = (
            emotion_name_counts
            .most_common(1)[0][0]
        )


        latest_record = max(
            district_record_list,
            key=lambda item: (
                item["created_at"]
            ),
        )


        district_map_data.append(
            {
                "district_name": (
                    district_name
                ),

                "visit_count": len(
                    district_record_list,
                ),

                "dominant_emotion": (
                    dominant_emotion
                ),

                "latest_emotion": (
                    latest_record[
                        "emotion_name"
                    ]
                ),
            }
        )


    # ========================================================
    # 14. 장소별 기록 횟수
    # ========================================================

    location_counts = Counter(
        record.place.district
        for record in records
        if (
            record.place
            and record.place.district
        )
    )


    locations = [
        {
            "name": place_name,

            "record_count": count,
        }

        for (
            place_name,
            count,
        ) in location_counts.items()
    ]


    locations.sort(
        key=lambda location: (
            location["record_count"]
        ),
        reverse=True,
    )


    # ========================================================
    # 15. 템플릿 데이터
    # ========================================================

    context = {
        # 전체 기록
        "records": records,


        # 감정별 기록
        "emotions": emotions,

        "recorded_emotions": (
            recorded_emotions
        ),

        "top_emotions": top_emotions,

        "emotion_chart_groups": (
            emotion_chart_groups
        ),

        "total_record_count": (
            total_record_count
        ),


        # 장소별 기록
        "locations": locations,

        "district_map_data": (
            district_map_data
        ),


        # 필터 상태
        "selected_tab": selected_tab,

        "selected_sort": selected_sort,

        "selected_start_date": (
            selected_start_date
        ),

        "selected_end_date": (
            selected_end_date
        ),

        "selected_emotion": (
            request.GET.get(
                "emotion",
                "",
            )
        ),

        "selected_location": (
            request.GET.get(
                "location",
                "",
            )
        ),
    }


    return render(
        request,
        "diary/list.html",
        context,
    )


# ============================================================
# 감정 캘린더
# ============================================================

@login_required
def emotion_calendar(request):
    """
    현재 로그인한 사용자의 기록을 날짜별로 정리함.

    같은 날짜에 여러 기록이 있으면
    가장 최근 기록의 대표 감정을 캘린더에 표시함.
    """

    today = timezone.localdate()


    # 최신 기록부터 조회함.
    records = (
        Record.objects
        .filter(
            user=request.user,
        )
        .order_by(
            "-created_at",
        )
    )


    calendar_emotions = {}


    for record in records:

        created_date = timezone.localtime(
            record.created_at,
        ).date()


        date_key = created_date.strftime(
            "%Y-%m-%d",
        )


        # 이미 해당 날짜의 최신 기록이 저장되었다면 건너뜀.
        if date_key in calendar_emotions:
            continue


        try:
            emotion_number = int(
                record.main_emotion,
            )

        except (TypeError, ValueError):
            continue


        calendar_emotions[
            date_key
        ] = {
            "number": emotion_number,

            "name": get_emotion_name(
                emotion_number,
            ),

            "image_name": (
                f"emotion-{emotion_number:02d}.png"
            ),

            # 캘린더 클릭 시
            # 해당 날짜의 최신 기록 상세로 이동함.
            "record_id": record.pk,
        }


    context = {
        "calendar_year": today.year,

        "calendar_month": today.month,

        "calendar_emotions": (
            calendar_emotions
        ),
    }


    return render(
        request,
        "diary/calendar.html",
        context,
    )


# ============================================================
# 기록 상세
# ============================================================

@login_required
def diary_detail(request, pk):
    """
    기록 상세 페이지를 표시함.

    같은 날짜의 기록이 여러 개라면
    최신 기록부터 과거 기록 순으로 이동할 수 있음.
    """

    # ========================================================
    # 1. 현재 기록 조회
    # ========================================================

    record = get_object_or_404(
        Record.objects.select_related(
            "place",
        ),
        pk=pk,
        user=request.user,
    )


    # ========================================================
    # 2. 화면에 표시할 장소명
    # ========================================================

    if (
        record.place
        and record.place.name
    ):
        display_place_name = (
            record.place.name
        )

    elif getattr(
        record,
        "place_name",
        "",
    ):
        display_place_name = (
            record.place_name
        )

    else:
        display_place_name = (
            "장소 정보 없음"
        )


    # ========================================================
    # 3. 현재 기록 날짜
    # ========================================================

    record_date = timezone.localtime(
        record.created_at,
    ).date()


    # ========================================================
    # 4. 해당 날짜 시간 범위
    # ========================================================

    current_timezone = (
        timezone.get_current_timezone()
    )


    day_start = timezone.make_aware(
        datetime.combine(
            record_date,
            datetime.min.time(),
        ),
        current_timezone,
    )


    next_date = (
        record_date
        + timedelta(days=1)
    )


    day_end = timezone.make_aware(
        datetime.combine(
            next_date,
            datetime.min.time(),
        ),
        current_timezone,
    )


    # ========================================================
    # 5. 같은 날짜의 모든 기록
    # ========================================================

    same_day_records = list(
        Record.objects
        .filter(
            user=request.user,

            created_at__gte=day_start,

            created_at__lt=day_end,
        )
        .order_by(
            "-created_at",
        )
    )


    # ========================================================
    # 6. 현재 기록 위치
    # ========================================================

    current_record_index = next(
        (
            index

            for (
                index,
                same_day_record,
            ) in enumerate(
                same_day_records,
            )

            if (
                same_day_record.pk
                == record.pk
            )
        ),
        0,
    )


    same_day_record_count = len(
        same_day_records,
    )


    # ========================================================
    # 7. 더 최근 / 더 과거 기록
    # ========================================================

    newer_record = (
        same_day_records[
            current_record_index - 1
        ]
        if current_record_index > 0
        else None
    )


    older_record = (
        same_day_records[
            current_record_index + 1
        ]
        if (
            current_record_index
            < same_day_record_count - 1
        )
        else None
    )


    current_record_number = (
        current_record_index + 1
    )


    # ========================================================
    # 8. 대표 감정
    # ========================================================

    main_emotion_number = int(
        record.main_emotion,
    )


    main_emotion = {
        "number": (
            main_emotion_number
        ),

        "name": get_emotion_name(
            main_emotion_number,
        ),

        "image_name": (
            f"emotion-{main_emotion_number:02d}.png"
        ),
    }


    # ========================================================
    # 9. 보조 감정
    # ========================================================

    secondary_emotions = []


    for emotion_number in record.emotions:

        try:
            emotion_number = int(
                emotion_number,
            )

        except (TypeError, ValueError):
            continue


        if (
            emotion_number
            == main_emotion_number
        ):
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


    left_emotion = (
        secondary_emotions[0]
        if secondary_emotions
        else None
    )


    right_emotion = (
        secondary_emotions[1]
        if len(secondary_emotions) >= 2
        else None
    )


    # ========================================================
    # 10. 템플릿 데이터
    # ========================================================

    context = {
        "record": record,

        "display_place_name": (
            display_place_name
        ),

        "main_emotion": (
            main_emotion
        ),

        "left_emotion": (
            left_emotion
        ),

        "right_emotion": (
            right_emotion
        ),

        "newer_record": (
            newer_record
        ),

        "older_record": (
            older_record
        ),

        "current_record_number": (
            current_record_number
        ),

        "same_day_record_count": (
            same_day_record_count
        ),
    }


    return render(
        request,
        "diary/detail.html",
        context,
    )