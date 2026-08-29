# 담당 B: 지도, 장소 검색 및 선택
#
# 화면 1(위치 선택, place_select.html)과 화면 2(지도, map.html)에서
# locations.js/템플릿이 사용하는 뷰들을 모아둔 파일.
# - place_select: 화면 1 렌더링
# - reverse_geocode / search_address: 카카오 REST API를 대신 호출해주는 서버 프록시
#   (REST 키는 여기(서버)에서만 쓰고 절대 클라이언트로 내려보내지 않는다)
# - confirm_place: "네" 클릭 시 Place를 실제로 저장
# - map_view: 화면 2 렌더링 (선택된 Place의 구를 지도에 색칠하기 위한 데이터 전달)

import json

import requests
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_POST

from .models import Place
from .services import set_verified_place

# 카카오 로컬 REST API 공통 base url.
# (좌표->주소 변환은 /geo/coord2address.json, 키워드 검색은 /search/keyword.json 을 이어붙여 사용)
KAKAO_LOCAL_API_BASE = "https://dapi.kakao.com/v2/local"


@ensure_csrf_cookie
@login_required(login_url="accounts:login")
def place_select(request):
    """
    화면 1(위치 선택) 렌더링.

    - @ensure_csrf_cookie:
      locations.js는 <form>이 아니라 fetch로 confirm_place에 직접 POST를 보낸다.
      폼 태그가 없으면 {% csrf_token %}을 렌더링할 곳이 없어서 csrftoken 쿠키가 안 생기고,
      그러면 locations.js의 getCookie("csrftoken")이 계속 None을 반환해 POST가
      403(CSRF 검증 실패)으로 막힌다. 이 데코레이터가 응답에 쿠키를 강제로 심어서 그걸 막아준다.
    - kakao_js_key:
      템플릿의 `<script src="...sdk.js?appkey={{ kakao_js_key }}">`에서 쓰는 값.
      config/settings.py가 .env의 KAKAO_JS_KEY를 읽어 등록해둔 값을 그대로 내려준다.
    """
    return render(
        request,
        "locations/place_select.html",
        {"kakao_js_key": settings.KAKAO_JS_KEY},
    )


@require_GET
def reverse_geocode(request):
    """
    좌표 -> 주소 변환 프록시 뷰. (locations.js: API_ENDPOINTS.reverseGeocode)

    locations.js가 REST API 키를 직접 들고 카카오에 요청하면 브라우저 네트워크 탭에서
    키가 그대로 노출되므로, 반드시 이 서버 뷰가 KAKAO_REST_KEY로 대신 카카오
    coord2address API를 호출하고 필요한 값만 추려서 클라이언트에 돌려준다.

    요청: GET /locations/api/reverse-geocode/?lat=<위도>&lng=<경도>
    응답: {"address": "서울특별시 마포구 ...", "district": "마포구"}
    """
    lat = request.GET.get("lat")
    lng = request.GET.get("lng")

    if not lat or not lng:
        return JsonResponse({"error": "lat, lng 파라미터가 필요합니다."}, status=400)

    response = requests.get(
        f"{KAKAO_LOCAL_API_BASE}/geo/coord2address.json",
        # 카카오 API는 x=경도(longitude), y=위도(latitude) 순서라 lat/lng와 헷갈리기 쉬우니 주의.
        params={"x": lng, "y": lat},
        headers={"Authorization": f"KakaoAK {settings.KAKAO_REST_KEY}"},
        timeout=5,
    )

    if response.status_code != 200:
        # 키가 잘못됐거나(.env 미설정) 카카오 쪽 장애인 경우 등. 502로 클라이언트에 알림.
        return JsonResponse({"error": "카카오 주소 변환 요청이 실패했습니다."}, status=502)

    documents = response.json().get("documents") or []
    if not documents:
        # 바다 위 좌표 등 대응하는 주소가 없는 경우.
        return JsonResponse({"error": "해당 좌표의 주소를 찾을 수 없습니다."}, status=404)

    document = documents[0]
    road_address = document.get("road_address")  # 도로명 주소 (없을 수 있음)
    address = document.get("address")  # 지번 주소 (보통 항상 있음)

    # 화면/저장 값으로는 도로명 주소를 우선 사용하고, 없으면 지번 주소로 대체.
    full_address = (road_address or address or {}).get("address_name", "")

    # "구" 이름은 지번 주소의 region_2depth_name에 들어있다 (예: "마포구").
    # 도로명 주소 쪽에도 같은 필드가 있지만 지번 주소가 항상 오는 편이라 그쪽을 우선 사용.
    # district = (address or road_address or {}).get("region_2depth_name", "")

    # return JsonResponse({"address": full_address, "district": district})

    # 지번 주소 우선 사용.
    region_address = address or road_address or {}

    # 시도명 추출.
    region_1depth_name = region_address.get(
        "region_1depth_name",
        "",
    ).strip()

    # 시군구명 추출.
    district = region_address.get(
        "region_2depth_name",
        "",
    ).strip()

    return JsonResponse(
        {
            "address": full_address,
            "region_1depth_name": region_1depth_name,
            "district": district,
        }
    )

@require_GET
def search_address(request):
    """
    주소/장소 검색 프록시 뷰. (locations.js: API_ENDPOINTS.searchAddress, "직접 입력할게요" 흐름)

    사용자가 지번/도로명 주소뿐 아니라 "스타벅스 신촌점" 같은 장소명도 입력할 수 있으므로,
    주소만 찾는 API(address.json) 대신 카카오 "키워드로 장소 검색"(keyword.json)을 사용한다.
    (주소만 정확히 입력해도 keyword.json이 함께 찾아준다.)

    요청: GET /locations/api/search/?query=<검색어>
    응답: [{"name":..., "address":..., "lat":..., "lng":..., "district":..., "kakao_place_id":...}, ...]
    """
    query = request.GET.get("query", "").strip()

    if not query:
        # 빈 검색어는 카카오에 요청 자체를 보내지 않고 빈 목록으로 바로 응답.
        return JsonResponse([], safe=False)

    response = requests.get(
        f"{KAKAO_LOCAL_API_BASE}/search/keyword.json",
        params={"query": query, "size": 10},  # size: 결과 개수 상한. 화면 UI 상 10개면 충분하다고 판단.
        headers={"Authorization": f"KakaoAK {settings.KAKAO_REST_KEY}"},
        timeout=5,
    )

    if response.status_code != 200:
        return JsonResponse({"error": "카카오 검색 요청이 실패했습니다."}, status=502)

    documents = response.json().get("documents") or []

    results = []

    for document in documents:
        address_name = document.get(
            "address_name",
            "",
        )

        (
            region_1depth_name,
            district,
        ) = _extract_region_names(
            address_name,
        )

        results.append(
            {
                "name": document.get(
                    "place_name",
                    "",
                ),
                "address": (
                    document.get("road_address_name")
                    or address_name
                ),
                "lat": document.get("y"),
                "lng": document.get("x"),
                "region_1depth_name": (
                    region_1depth_name
                ),
                "district": district,
                "kakao_place_id": document.get(
                    "id",
                    "",
                ),
            }
        )

    return JsonResponse(results, safe=False)

'''
def _extract_district(address_name):
    """
    "서울 마포구 ~~~" 형태의 지번 주소 문자열에서 "구" 이름만 뽑아낸다.

    coord2address 응답과 달리 keyword.json 검색 응답에는 region_2depth_name 같은
    필드가 따로 오지 않아서, address_name 문자열을 공백 기준으로 쪼개 "구"로 끝나는
    토큰을 직접 찾아야 한다. 서울이 아닌 주소(구가 없는 지역)면 빈 문자열을 반환하며,
    이 경우 화면 2(서울 구 단위 지도)에서는 색칠 대상이 없다는 뜻이 된다.
    """
    for part in address_name.split():
        if part.endswith("구"):
            return part
    return ""
'''
# 전국 지도 수정본
def _normalize_region_1depth_name(region_name):
    """시도 약칭을 정식 명칭으로 변환함."""

    region_name_map = {
        "서울": "서울특별시",
        "부산": "부산광역시",
        "대구": "대구광역시",
        "인천": "인천광역시",
        "광주": "광주광역시",
        "대전": "대전광역시",
        "울산": "울산광역시",
        "세종": "세종특별자치시",
        "경기": "경기도",
        "강원": "강원특별자치도",
        "충북": "충청북도",
        "충남": "충청남도",
        "전북": "전북특별자치도",
        "전남": "전라남도",
        "경북": "경상북도",
        "경남": "경상남도",
        "제주": "제주특별자치도",
    }

    return region_name_map.get(
        region_name,
        region_name,
    )


def _extract_region_names(address_name):
    """주소에서 시도명과 시군구명을 추출함."""

    parts = address_name.split()

    if not parts:
        return "", ""

    region_1depth_name = (
        _normalize_region_1depth_name(parts[0])
    )

    # 세종은 하위 시군구 없이 단일 지역으로 처리.
    if region_1depth_name == "세종특별자치시":
        return (
            region_1depth_name,
            "세종특별자치시",
        )

    if len(parts) < 2:
        return region_1depth_name, ""

    district = parts[1]

    # 일반구가 있는 도시 처리.
    # 예: "경기 수원시 영통구" → "수원시 영통구"
    if (
        len(parts) >= 3
        and parts[1].endswith("시")
        and parts[2].endswith("구")
    ):
        district = (
            f"{parts[1]} {parts[2]}"
        )

    return region_1depth_name, district


@require_POST
@login_required(login_url="accounts:login")
def confirm_place(request):
    """
    위치 확정("네" 클릭) 시 Place를 저장하는 뷰. (locations.js: API_ENDPOINTS.confirmPlace)

    locations.js가 JSON body로 좌표/주소/구/장소명/카카오 장소 id를 보내면 그대로 Place를
    생성하고, 화면 2(구 단위 지도)로 이동할 수 있게 redirect_url을 함께 응답한다.

    요청: POST /locations/api/places/
          body(JSON): {latitude, longitude, address, district, name, kakao_place_id}
    응답: {"id": <Place.id>, "redirect_url": "/locations/map/?place=<id>"}
    """
    try:
        payload = json.loads(request.body)
    except (json.JSONDecodeError, TypeError):
        return JsonResponse({"error": "잘못된 요청 본문입니다."}, status=400)

    latitude = payload.get("latitude")
    longitude = payload.get("longitude")
    address = payload.get("address")
    district = payload.get("district")
    region_1depth_name = payload.get(
        "region_1depth_name",
        "",
    ).strip()

    # Place 모델에서 필수(blank=False)인 필드들은 저장 전에 미리 검증해서
    # 빈 값으로 DB 에러가 나는 대신 명확한 400 응답을 준다.
    if not latitude or not longitude or not address or not district:
        return JsonResponse(
            {"error": "latitude, longitude, address, district는 필수입니다."},
            status=400,
        )

    place = Place.objects.create(
        name=payload.get("name", ""),
        address=address,
        region_1depth_name=region_1depth_name,
        district=district,
        latitude=latitude,
        longitude=longitude,
        kakao_place_id=payload.get(
            "kakao_place_id",
            "",
        ),
    )

    set_verified_place(request, place)

    # reverse("locations:map")으로 URL을 하드코딩하지 않고 urls.py에 등록된 이름으로 구성.
    # urls.py에서 map 뷰의 경로/이름이 바뀌어도 여기는 고칠 필요가 없다.
    return JsonResponse(
        {
            "id": place.id,
            "redirect_url": f"{reverse('locations:map')}?place={place.id}",
        }
    )


@require_GET
def map_view(request):
    """
    화면 2(구 단위 지도) 렌더링. (locations/templates/locations/map.html)

    confirm_place 뷰가 저장 성공 후 "<map url>?place=<Place.id>"로 리다이렉트시키는 걸
    받는 뷰. place 쿼리 파라미터로 넘어온 id로 Place를 조회해서 그 장소가 속한 구(district)를
    템플릿에 내려주고, 템플릿/locations.js가 그 구를 지도에서 색칠하는 데 사용한다.

    요청: GET /locations/map/?place=<Place.id>  (place는 선택 사항)

    place 파라미터가 없거나, 존재하지 않는 id면(예: /locations/map/으로 그냥 들어온 경우)
    에러를 내지 않고 그냥 아무 구도 선택되지 않은 지도를 보여준다 — 지도 자체는
    place 확정 여부와 상관없이 열람 가능한 화면이라고 판단했기 때문.
    """
    place_id = request.GET.get("place")
    place = Place.objects.filter(pk=place_id).first() if place_id else None

    # 와이어프레임(참고/지도.PNG)은 주소 문자열에서 "서울특별시 OO구"까지만 강조 색으로
    # 보여주고 나머지(상세 주소)는 일반 텍스트로 표시한다. address 필드는 하나의 문자열이라
    # 템플릿에서 부분 색칠이 불가능하므로, 여기서 district 이름이 끝나는 지점까지 잘라
    # prefix/suffix 두 조각으로 나눠서 내려준다.
    address_prefix, address_suffix = "", ""
    if place:
        cut = place.address.find(place.district)
        if cut != -1:
            cut += len(place.district)
            address_prefix, address_suffix = place.address[:cut], place.address[cut:]
        else:
            # district 이름이 address 문자열 안에 그대로 없는 경우(직접 입력 등) 대비.
            address_suffix = place.address

    return render(
        request,
        "locations/map.html",
        {
            "selected_district": place.district if place else "",
            "selected_place_id": place.id if place else "",
            "selected_address_prefix": address_prefix,
            "selected_address_suffix": address_suffix,
        },
    )
