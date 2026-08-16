# 담당 D: 캘린더 및 다이어리 목록 조회

from collections import Counter
from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from bgm.services import get_available_music

# 담당 C가 만든 실제 기록 모델 가져옴.
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

"""
감정별 기록의 도넛 그래프에서는
감정 하나마다 다른 색을 사용하는 것이 아니라,

비슷한 색상 계열의 감정을
하나의 그래프 조각으로 묶어서 표시함.

예:
사랑, 짝사랑
→ pink 그룹

기쁨, 만족, 신남, 행운, 맛있어!
→ yellow 그룹

중요:
여기서는 감정 이름이 아니라
감정 번호를 기준으로 그룹 지정함.

같은 이름의 감정이 여러 번호에 존재하더라도
번호 기준으로 안정적으로 처리할 수 있음.
"""

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


def get_emotion_name(emotion_number):
    """
    감정 번호를 화면에 표시할 감정 이름으로 변환함.

    예:
    1 → "슬픔"
    7 → "짝사랑"
    """

    try:
        # JSONField 값이나 폼 값이 문자열일 수도 있으므로
        # 비교하기 전에 정수로 변환함.
        emotion_number = int(
            emotion_number,
        )

    except (TypeError, ValueError):
        # 값이 없거나 숫자로 바꿀 수 없다면
        # 빈 문자열 반환함.
        return ""

    return EMOTION_NAME_MAP.get(
        emotion_number,
        f"감정 {emotion_number}",
    )


def get_emotion_color_group(emotion_number):
    """
    감정 번호를 감정별 그래프에서 사용할
    색상 그룹 이름으로 변환함.

    예:
    2 → pink
    11 → red
    16 → yellow
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


@login_required
def diary_list(request):
    """
    현재 로그인한 사용자가 작성한 실제 Record를 조회하여
    전체 / 감정별 / 장소별 목록 페이지에 전달함.
    """

    # ========================================================
    # 1. 현재 선택한 탭과 필터값
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


    # 허용하지 않는 탭 이름이 들어오면
    # 전체 기록 탭으로 돌려놓음.
    if selected_tab not in {
        "all",
        "emotion",
        "location",
    }:
        selected_tab = "all"


    # ========================================================
    # 2. 현재 사용자의 실제 기록 조회
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

            records_queryset = records_queryset.filter(
                created_at__date__gte=start_date,
            )

        except ValueError:
            # 잘못된 날짜 값이 들어오면
            # 필터 무시함.
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


    # QuerySet을 리스트로 변환함.
    #
    # 이후 여러 번 반복하면서
    # 감정 / 장소 데이터를 계산하기 때문에
    # 한 번 리스트로 만들어 사용함.
    records = list(
        records_queryset,
    )


    # ========================================================
    # 6. 각 기록에 화면용 대표 감정 정보 추가
    # ========================================================

    for record in records:

        # 대표 감정 번호를
        # 사람이 읽을 수 있는 이름으로 바꿈.
        record.main_emotion_name = get_emotion_name(
            record.main_emotion,
        )

        # 지도나 다른 화면에서도 필요할 수 있으므로
        # 대표 감정의 색상 그룹도 record에 임시로 추가함.
        record.main_emotion_color_group = (
            get_emotion_color_group(
                record.main_emotion,
            )
        )


    # ========================================================
    # 7. 대표 감정별 기록 횟수 계산
    # ========================================================

    """
    record.emotions 전체를 사용하는 것이 아니라
    record.main_emotion만 사용함.

    따라서 사용자가 기록할 때 선택한 감정이 3개여도
    대표 감정 1개만 감정별 그래프 집계에 포함됨.
    """

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


    # 예:
    #
    # [16, 16, 12, 11]
    #
    # →
    #
    # {
    #     16: 2,
    #     12: 1,
    #     11: 1
    # }

    emotion_counts = Counter(
        main_emotion_numbers,
    )


    # 모든 감정 정보를 담는 목록.
    #
    # 기존 기능과의 호환을 위해
    # 기록 횟수가 0인 감정도 emotions에는 남겨둠.
    emotions = []

    for emotion_id, emotion_name in EMOTION_NAME_MAP.items():

        record_count = emotion_counts.get(
            emotion_id,
            0,
        )

        emotions.append(
            {
                "id": emotion_id,

                "name": emotion_name,

                # 해당 감정이 대표 감정으로
                # 기록된 횟수.
                "record_count": record_count,

                # 도넛 그래프에서 사용할 색상 그룹.
                "color_group": (
                    get_emotion_color_group(
                        emotion_id,
                    )
                ),
            }
        )


    # ========================================================
    # 8. 실제로 기록된 대표 감정만 추리기
    # ========================================================

    """
    도넛 그래프에는
    한 번도 기록되지 않은 감정은 나오면 안 됨.

    따라서 record_count가 1 이상인 감정만
    recorded_emotions에 넣음.
    """

    recorded_emotions = [
        emotion
        for emotion in emotions
        if emotion["record_count"] > 0
    ]

    # 기록 횟수 많은 순으로 정렬함.
    recorded_emotions.sort(
        key=lambda emotion: emotion["record_count"],
        reverse=True,
    )


    # ========================================================
    # 9. 가장 많이 기록한 대표 감정 계산
    # ========================================================

    """
    기존 emotion_modal이나 다른 화면에서
    top_emotions를 사용할 수도 있으므로
    이 데이터는 유지함.
    """

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
    # 10. 도넛 그래프용 색상 그룹 데이터 생성
    # ========================================================

    """
    같은 색상 그룹에 속한 감정들을 하나로 합침.

    예:

    기쁨 2회
    만족 1회
    신남 1회

    모두 yellow 그룹이라면

    yellow:
        count = 4
        emotions = ["만족", "신남", "기쁨"]

    가 됨.

    JavaScript는 이 데이터를 사용하여
    원 그래프 조각 크기를 계산할 수 있음.
    """

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


        # 해당 색상 그룹이 처음 등장하면
        # 기본 구조 생성함.
        if color_group not in emotion_chart_group_dict:

            emotion_chart_group_dict[color_group] = {
                "color_group": color_group,

                # 이 색상 그룹에 속한
                # 대표 감정 기록 수 총합.
                "record_count": 0,

                # hover 시 보여줄 감정 이름 목록.
                "emotion_names": [],
            }


        # 색상 그룹의 전체 기록 수에
        # 현재 감정 기록 수 더함.
        emotion_chart_group_dict[
            color_group
        ]["record_count"] += record_count


        # 같은 이름을 중복해서
        # 툴팁에 표시하지 않도록 함.
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


    # 딕셔너리를 템플릿에서 사용하기 쉬운
    # 리스트 형태로 바꿈.
    emotion_chart_groups = list(
        emotion_chart_group_dict.values()
    )


    # ========================================================
    # 11. 전체 대표 감정 기록 수
    # ========================================================

    total_record_count = sum(
        emotion["record_count"]
        for emotion in recorded_emotions
    )


    # ========================================================
    # 12. 서울 지도용 장소 데이터 계산
    # ========================================================

    district_records = {}


    for record in records:

        # Record에 연결된 Place가 없으면
        # 지도에 표시할 수 없으므로 제외함.
        if not record.place:
            continue


        # Place 모델의 district에는
        # "성북구", "강남구"와 같은
        # 서울 자치구 이름이 저장됨.
        district_name = (
            record.place.district.strip()
            if record.place.district
            else ""
        )


        # 구 이름이 없다면 제외함.
        if not district_name:
            continue


        emotion_name = (
            record.main_emotion_name
        )


        # 대표 감정 정보가 없으면
        # 지도 감정 색상을 정할 수 없으므로 제외함.
        if not emotion_name:
            continue


        if district_name not in district_records:

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

        # 해당 구에서 기록된
        # 대표 감정 이름 목록.
        emotion_names = [
            item["emotion_name"]
            for item in district_record_list
        ]


        # 가장 많이 기록된 감정 계산함.
        emotion_name_counts = Counter(
            emotion_names,
        )

        dominant_emotion = (
            emotion_name_counts
            .most_common(1)[0][0]
        )


        # 가장 최근 기록 계산함.
        latest_record = max(
            district_record_list,
            key=lambda item: item[
                "created_at"
            ],
        )


        district_map_data.append(
            {
                # SVG path의 id와 비교할 구 이름.
                "district_name": district_name,

                # 해당 구에서 작성한 기록 수.
                "visit_count": len(
                    district_record_list,
                ),

                # 해당 구에서 가장 많이 기록된 감정.
                "dominant_emotion": (
                    dominant_emotion
                ),

                # 해당 구에서 가장 최근 대표 감정.
                "latest_emotion": (
                    latest_record[
                        "emotion_name"
                    ]
                ),
            }
        )


    # ========================================================
    # 13. 장소별 기록 횟수 계산
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
    # 14. 템플릿에 데이터 전달
    # ========================================================

    context = {
        # ----------------------------------------------------
        # 공통 기록
        # ----------------------------------------------------
        "records": records,


        # ----------------------------------------------------
        # 감정별 기록
        # ----------------------------------------------------

        # 모든 감정.
        "emotions": emotions,

        # 실제 대표 감정으로 기록된 감정만.
        "recorded_emotions": recorded_emotions,

        # 가장 많이 기록한 대표 감정.
        "top_emotions": top_emotions,

        # 도넛 그래프용 색상 그룹 데이터.
        "emotion_chart_groups": emotion_chart_groups,

        # 도넛 그래프 가운데 표시할 전체 기록 수.
        "total_record_count": total_record_count,


        # ----------------------------------------------------
        # 장소별 기록
        # ----------------------------------------------------
        "locations": locations,

        "district_map_data": (
            district_map_data
        ),


        # ----------------------------------------------------
        # 현재 탭 및 필터 상태
        # ----------------------------------------------------
        "selected_tab": selected_tab,

        "selected_sort": selected_sort,

        "selected_start_date": (
            selected_start_date
        ),

        "selected_end_date": (
            selected_end_date
        ),

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
    감정 캘린더 페이지에 전달함.

    같은 날짜에 기록이 여러 개라면
    가장 최근에 작성한 기록의 대표 감정을 사용함.
    """

    # 오늘 날짜를 기준으로
    # 캘린더 최초 연도와 월 설정함.
    today = timezone.localdate()


    # 최신 기록부터 조회함.
    #
    # 아래에서 날짜별 데이터에
    # 처음 들어간 기록만 사용하므로
    # 같은 날짜에 여러 기록이 있으면
    # 가장 최신 기록이 남음.
    records = Record.objects.filter(
        user=request.user,
    ).order_by(
        "-created_at",
    )


    # JavaScript에 전달할
    # 날짜별 감정 데이터.
    calendar_emotions = {}


    for record in records:

        # created_at을
        # 한국 시간 기준 날짜로 변환함.
        created_date = timezone.localtime(
            record.created_at,
        ).date()


        date_key = created_date.strftime(
            "%Y-%m-%d",
        )


        # 이미 같은 날짜의 최신 기록이 있다면
        # 오래된 기록은 건너뜀.
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
            # 감정 번호.
            "number": emotion_number,

            # 감정 이름.
            "name": get_emotion_name(
                emotion_number,
            ),

            # 감정 이미지 파일명.
            "image_name": (
                f"emotion-{emotion_number:02d}.png"
            ),

            # 상세 페이지 이동용 기록 ID.
            #
            # 같은 날짜의 기록 중
            # 가장 최근 기록의 ID가 저장됨.
            "record_id": record.pk,
        }


    context = {
        # 최초 화면에 표시할 연도.
        "calendar_year": today.year,

        # 최초 화면에 표시할 월.
        "calendar_month": today.month,

        # 날짜별 대표 감정 데이터.
        "calendar_emotions": (
            calendar_emotions
        ),
    }


    return render(
        request,
        "diary/calendar.html",
        context,
    )


@login_required
def diary_detail(request, pk):
    """
    현재 로그인한 사용자가 작성한 기록 하나를 조회하여
    다이어리 상세 페이지에 전달함.

    같은 날짜에 여러 개의 기록이 존재하면
    최신 기록부터 과거 기록 순으로 이동할 수 있도록
    같은 날짜의 기록 정보도 함께 전달함.

    pk는 기록의 고유 번호.

    예:
    /diary/2/
    → id가 2인 Record 조회함.
    """

    # ========================================================
    # 1. 현재 상세 기록 조회
    # ========================================================

    # 다른 사용자의 기록을
    # 주소로 직접 접근하지 못하도록
    # user=request.user 조건 함께 사용함.
    record = get_object_or_404(
        Record,
        pk=pk,
        user=request.user,
    )


    # ========================================================
    # 2. 현재 사용할 수 있는 BGM 조회
    # ========================================================

    # 기존 Listen 기능 유지함.
    musics = get_available_music()


    # ========================================================
    # 3. 현재 기록의 날짜 계산
    # ========================================================

    # created_at은 시간까지 가지고 있으므로
    # 현재 시간대 기준 날짜만 추출함.
    #
    # 예:
    # 2026-08-16 21:35
    # →
    # 2026-08-16
    record_date = timezone.localtime(
        record.created_at,
    ).date()


    # ========================================================
    # 4. 같은 날짜의 모든 기록 조회
    # ========================================================

    # 현재 기록과 같은 날 작성된 기록만 조회함.
    #
    # -created_at을 사용하여
    # 가장 최근 기록부터 과거 기록 순으로 정렬함.
    #
    # 예:
    #
    # 20:30
    # 15:40
    # 10:20
    same_day_records = list(
        Record.objects
        .filter(
            user=request.user,
            created_at__date=record_date,
        )
        .order_by(
            "-created_at",
        )
    )


    # ========================================================
    # 5. 현재 기록이 몇 번째 기록인지 찾기
    # ========================================================

    # 같은 날짜의 기록 목록 안에서
    # 현재 보고 있는 record 위치 저장함.
    current_record_index = 0


    for index, same_day_record in enumerate(
        same_day_records,
    ):

        if same_day_record.pk == record.pk:

            current_record_index = index

            break


    # ========================================================
    # 6. 왼쪽 화살표용 더 최근 기록
    # ========================================================

    # 목록이 최신순이므로
    #
    # index 0 → 가장 최근
    # index 1 → 두 번째
    # index 2 → 세 번째
    #
    # 현재 index보다 하나 작은 기록이
    # 더 최근 기록임.
    newer_record = None


    if current_record_index > 0:

        newer_record = same_day_records[
            current_record_index - 1
        ]


    # ========================================================
    # 7. 오른쪽 화살표용 더 과거 기록
    # ========================================================

    # 현재 index보다 하나 큰 기록이
    # 더 과거의 기록임.
    older_record = None


    if (
        current_record_index
        < len(same_day_records) - 1
    ):

        older_record = same_day_records[
            current_record_index + 1
        ]


    # ========================================================
    # 8. 현재 기록 번호와 전체 기록 수
    # ========================================================

    # Python index는 0부터 시작하지만
    # 화면에는 1부터 표시함.
    #
    # index 0 → 1 / 3
    # index 1 → 2 / 3
    # index 2 → 3 / 3
    current_record_number = (
        current_record_index + 1
    )


    same_day_record_count = len(
        same_day_records,
    )


    # ========================================================
    # 9. 대표 감정
    # ========================================================

    # Record.main_emotion에는
    # 1~20 사이 번호가 저장됨.
    main_emotion_number = int(
        record.main_emotion,
    )


    main_emotion = {
        # 감정 번호.
        "number": main_emotion_number,

        # 화면에 표시할 감정 이름.
        "name": get_emotion_name(
            main_emotion_number,
        ),

        # 실제 감정 이미지 파일명.
        "image_name": (
            f"emotion-{main_emotion_number:02d}.png"
        ),
    }


    # ========================================================
    # 10. 보조 감정
    # ========================================================

    secondary_emotions = []


    for emotion_number in record.emotions:

        try:
            emotion_number = int(
                emotion_number,
            )

        except (TypeError, ValueError):
            continue


        # 대표 감정은 가운데에서 따로 표시하므로
        # 보조 감정 목록에서는 제외함.
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


    # ========================================================
    # 11. 왼쪽 / 오른쪽 보조 감정 지정
    # ========================================================

    # 감정은 최대 3개이므로
    # 대표 감정 제외 후 보조 감정은 최대 2개임.
    left_emotion = (
        secondary_emotions[0]
        if len(secondary_emotions) >= 1
        else None
    )


    right_emotion = (
        secondary_emotions[1]
        if len(secondary_emotions) >= 2
        else None
    )


    # ========================================================
    # 12. 템플릿에 전달할 데이터
    # ========================================================

    context = {
        # ----------------------------------------------------
        # 현재 기록
        # ----------------------------------------------------
        "record": record,


        # ----------------------------------------------------
        # 감정 정보
        # ----------------------------------------------------

        # 가운데 대표 감정.
        "main_emotion": main_emotion,

        # 왼쪽 보조 감정.
        "left_emotion": left_emotion,

        # 오른쪽 보조 감정.
        "right_emotion": right_emotion,


        # ----------------------------------------------------
        # 같은 날짜 기록 이동
        # ----------------------------------------------------

        # 왼쪽 화살표:
        # 현재 기록보다 더 최근 기록.
        "newer_record": newer_record,

        # 오른쪽 화살표:
        # 현재 기록보다 더 과거 기록.
        "older_record": older_record,

        # 현재 몇 번째 기록인지.
        "current_record_number": (
            current_record_number
        ),

        # 같은 날짜의 전체 기록 개수.
        "same_day_record_count": (
            same_day_record_count
        ),


        # ----------------------------------------------------
        # 음악
        # ----------------------------------------------------
        "musics": musics,
    }


    return render(
        request,
        "diary/detail.html",
        context,
    )