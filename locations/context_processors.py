from django.urls import reverse

from .services import get_verified_place


def location_verification(request):
    """
    기록 작성 진입점과 모달 렌더링 여부를 모든 템플릿에 내려주는 컨텍스트 프로세서.

    - record_entry_url:
      "기록작성" 링크는 이미 오늘 위치를 인증했더라도 항상 화면 1(위치 선택)로 보낸다.
      기록 하나하나가 "그때 그 장소"의 기록이어야 하므로, 인증 결과를 재사용해
      위치 선택을 건너뛰면 안 된다. (모달은 화면 2(지도)의 "기록하러 가기"에서만 연다.)
    - can_create_record:
      진입 경로가 아니라 "지금 이 페이지에서 모달을 열 수 있는가"를 뜻한다.
      base.html이 이 값으로 record_modal.html / records.css / records.js 포함 여부를
      결정하므로, 위치 확정 후 넘어오는 지도 화면에서 모달이 렌더링되려면 필요하다.
    """
    verified_place = get_verified_place(request) if request.user.is_authenticated else None
    return {
        "can_create_record": verified_place is not None,
        "verified_place": verified_place,
        "record_entry_url": reverse("locations:place_select"),
    }
