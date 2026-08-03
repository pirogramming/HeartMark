from django.urls import path

from . import views

app_name = "locations"

urlpatterns = [
    # 화면 1: 위치 선택 페이지 (locations/templates/locations/place_select.html 렌더링)
    # 최종 경로: /locations/select/
    path("select/", views.place_select, name="place_select"),

    # 아래 3개는 화면이 아니라, locations.js가 fetch로 호출하는 서버 프록시/저장용 API.
    # 경로를 바꾸면 locations.js의 API_ENDPOINTS 상수도 반드시 같이 수정해야 한다.
    path("api/reverse-geocode/", views.reverse_geocode, name="reverse_geocode"),
    path("api/search/", views.search_address, name="search_address"),
    path("api/places/", views.confirm_place, name="confirm_place"),

    # 화면 2: 구 단위 지도 페이지 (locations/templates/locations/map.html 렌더링)
    # 최종 경로: /locations/map/?place=<Place.id>
    # views.confirm_place가 reverse("locations:map")으로 이 이름을 그대로 참조하므로
    # name="map"은 유지할 것 (바꾸면 confirm_place도 같이 고쳐야 함).
    path("map/", views.map_view, name="map"),
]

