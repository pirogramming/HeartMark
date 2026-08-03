// 담당 B 전용
//
// 화면 1(위치 선택, locations/templates/locations/place_select.html)의 동작을 담당하는 스크립트.
// - Geolocation으로 현재 좌표 획득
// - 카카오맵 SDK로 지도 렌더링 + 현재 위치 마커 표시
// - 서버 프록시 뷰(REST API 키는 서버에서만 사용)로 좌표->주소 변환, 주소/장소 검색
// - "네" 클릭 시 Place 저장 요청 -> 화면 2(구 단위 지도)로 이동


(function () {
    "use strict";

    // ---------------------------------------------------------------------
    // 0. place_select.html 안에서 사용할 DOM 요소를 미리 찾아둠.
    //    id는 place_select.html에 정의된 것과 반드시 동일해야 한다.
    // ---------------------------------------------------------------------
    const mapContainer = document.getElementById("kakao-map");
    const addressEl = document.getElementById("place-address");
    const confirmBtn = document.getElementById("btn-confirm-location");
    const manualBtn = document.getElementById("btn-manual-address");
    const searchSection = document.getElementById("place-search");
    const searchInput = document.getElementById("place-search-input");
    const searchBtn = document.getElementById("btn-search-address");
    const searchResultsEl = document.getElementById("place-search-results");

    // 이 스크립트는 base.html의 extra_js 블록을 통해 다른 화면에서도 로드될 수 있으므로,
    // 화면 1 전용 요소(#kakao-map, #place-address)가 없는 페이지에서는 아래 로직을 실행하지 않는다.
    if (!mapContainer || !addressEl) {
        return;
    }

    // ---------------------------------------------------------------------
    // 1. 서버 프록시 엔드포인트.
    //    REST API 키(KAKAO_REST_KEY, config/settings.py)는 브라우저에 절대 내려보내면 안 되므로,
    //    좌표->주소 변환/주소 검색은 반드시 이 서버 엔드포인트를 거쳐서 호출해야 한다.
    // ---------------------------------------------------------------------
    const API_ENDPOINTS = {
        reverseGeocode: "/locations/api/reverse-geocode/", // GET ?lat=&lng= -> { address, district }
        searchAddress: "/locations/api/search/", // GET ?query= -> [{ name, address, lat, lng, district, kakao_place_id }, ...]
        confirmPlace: "/locations/api/places/", // POST {latitude, longitude, address, district, name, kakao_place_id} -> { id, redirect_url }
    };

    // 현재 화면에 표시 중인 "확정 대상" 장소 상태.
    // reverse geocoding 응답이 오거나, 검색 결과 중 하나를 선택하면 갱신되고
    // #place-address의 data-* 속성에도 그대로 반영된다 (Place 모델 필드와 1:1 대응).
    let currentPlace = {
        latitude: null,
        longitude: null,
        address: "",
        district: "",
        name: "",
        kakaoPlaceId: "",
    };

    let map = null; // 카카오맵 인스턴스 (kakao.maps.Map)
    let marker = null; // 현재 위치/선택 위치를 가리키는 마커

    // ---------------------------------------------------------------------
    // 2. Django CSRF 토큰 읽기 (fetch로 POST할 때 X-CSRFToken 헤더에 실어 보내야 함).
    //    csrftoken 쿠키가 존재하려면 페이지 어딘가에 {% csrf_token %}이 렌더링되어 있거나,
    //    뷰에 @ensure_csrf_cookie가 걸려 있어야 한다.
    // ---------------------------------------------------------------------
    function getCookie(name) {
        const match = document.cookie.match(
            new RegExp("(?:^|; )" + name + "=([^;]*)")
        );
        return match ? decodeURIComponent(match[1]) : null;
    }

    // ---------------------------------------------------------------------
    // 3. 초기 진입 지점.
    //    현재 좌표 획득 -> 지도 초기화 -> 좌표->주소 변환 요청까지 순서대로 실행.
    // ---------------------------------------------------------------------
    function init() {
        if (!("geolocation" in navigator)) {
            // Geolocation 자체를 지원하지 않는 브라우저: 지도 없이 직접 입력으로 유도.
            showAddressMessage("이 브라우저는 위치 정보를 지원하지 않습니다. 직접 입력해주세요.");
            return;
        }

        navigator.geolocation.getCurrentPosition(
            function onSuccess(position) {
                const latitude = position.coords.latitude;
                const longitude = position.coords.longitude;
                initMap(latitude, longitude);
                fetchReverseGeocode(latitude, longitude);
            },
            function onError(error) {
                // 사용자가 위치 권한을 거부했거나 획득에 실패한 경우.
                // 지도/현재위치 흐름은 못 쓰지만 "직접 입력할게요"로는 계속 진행할 수 있게 안내만 표시.
                console.error("[locations] geolocation 실패:", error);
                showAddressMessage("현재 위치를 가져오지 못했습니다. 직접 입력해주세요.");
            },
            { enableHighAccuracy: true, timeout: 8000 }
        );
    }

    // ---------------------------------------------------------------------
    // 4. 카카오맵 SDK 초기화 + 지도 렌더링 + 현재 위치 마커 표시.
    //    place_select.html에서 SDK를 autoload=false로 불러왔기 때문에,
    //    kakao.maps.load(callback)으로 SDK 준비가 끝난 뒤에 지도를 생성해야 한다.
    // ---------------------------------------------------------------------
    function initMap(latitude, longitude) {
        if (typeof kakao === "undefined" || !kakao.maps) {
            console.error("[locations] 카카오맵 SDK를 불러오지 못했습니다. appkey(KAKAO_JS_KEY)를 확인하세요.");
            return;
        }

        kakao.maps.load(function () {
            const center = new kakao.maps.LatLng(latitude, longitude);

            map = new kakao.maps.Map(mapContainer, {
                center: center,
                level: 3, // 숫자가 작을수록 확대. 동네 수준으로 보이도록 우선 3으로 설정, 필요하면 조정.
            });

            marker = new kakao.maps.Marker({ position: center });
            marker.setMap(map);
        });
    }

    // 지도를 다시 만들지 않고 중심/마커만 새 좌표로 옮길 때 사용 (주소 검색 결과 선택 시).
    function moveMapTo(latitude, longitude) {
        if (!map || typeof kakao === "undefined") return;

        const position = new kakao.maps.LatLng(latitude, longitude);
        map.setCenter(position);

        if (marker) {
            marker.setPosition(position);
        } else {
            marker = new kakao.maps.Marker({ position: position });
            marker.setMap(map);
        }
    }

    // ---------------------------------------------------------------------
    // 5. 좌표 -> 주소 변환 (reverse geocoding).
    //    REST 키가 필요한 호출이라 카카오에 직접 요청하지 않고 반드시 서버 프록시를 거친다.
    // ---------------------------------------------------------------------
    function fetchReverseGeocode(latitude, longitude) {
        showAddressMessage("위치를 확인하는 중입니다...");

        const url = API_ENDPOINTS.reverseGeocode + "?lat=" + latitude + "&lng=" + longitude;

        fetch(url)
            .then(function (response) {
                if (!response.ok) throw new Error("reverse geocode 요청 실패");
                return response.json();
            })
            .then(function (data) {
                // 서버 프록시 뷰가 { address: "서울특별시 마포구 ...", district: "마포구" } 형태로
                // 응답한다고 가정 (카카오 coord2address 응답을 뷰에서 이 형태로 가공해줘야 함).
                setCurrentPlace({
                    latitude: latitude,
                    longitude: longitude,
                    address: data.address,
                    district: data.district,
                    name: "", // 현재 위치 기반 확정이라 장소명은 없음 (Place.name blank=True와 동일)
                    kakaoPlaceId: "",
                });
            })
            .catch(function (error) {
                console.error("[locations] 주소 변환 실패:", error);
                showAddressMessage("주소를 불러오지 못했습니다. 직접 입력해주세요.");
            });
    }

    // ---------------------------------------------------------------------
    // 6. 확정 대상 장소 정보 갱신: 상태값 저장 + 화면(#place-address) 반영 + "네" 버튼 활성화.
    // ---------------------------------------------------------------------
    function setCurrentPlace(place) {
        currentPlace = place;

        addressEl.textContent = place.address;
        addressEl.dataset.latitude = place.latitude;
        addressEl.dataset.longitude = place.longitude;
        addressEl.dataset.district = place.district;
        addressEl.dataset.name = place.name || "";
        addressEl.dataset.kakaoPlaceId = place.kakaoPlaceId || "";

        confirmBtn.disabled = false;
    }

    // 주소 대신 안내 문구를 보여줄 때 (로딩 중/실패 시) 사용. "네" 버튼은 다시 비활성화.
    function showAddressMessage(message) {
        addressEl.textContent = message;
        confirmBtn.disabled = true;
    }

    // ---------------------------------------------------------------------
    // 7. "직접 입력할게요" 토글: 주소 검색 영역을 보이거나 숨김.
    // ---------------------------------------------------------------------
    function toggleSearchSection() {
        searchSection.classList.toggle("hidden");
        if (!searchSection.classList.contains("hidden")) {
            searchInput.focus();
        }
    }

    // ---------------------------------------------------------------------
    // 8. 주소/장소 검색 -> 결과 목록 요청.
    // ---------------------------------------------------------------------
    function searchAddress() {
        const query = searchInput.value.trim();
        if (!query) return;

        const url = API_ENDPOINTS.searchAddress + "?query=" + encodeURIComponent(query);

        fetch(url)
            .then(function (response) {
                if (!response.ok) throw new Error("주소 검색 요청 실패");
                return response.json();
            })
            .then(function (results) {
                renderSearchResults(results);
            })
            .catch(function (error) {
                console.error("[locations] 주소 검색 실패:", error);
            });
    }

    // 검색 결과(results)를 #place-search-results 안에 <li>로 채워 넣고,
    // 각 항목을 클릭하면 그 장소로 지도/주소 상태를 갱신하도록 클릭 핸들러를 연결한다.
    function renderSearchResults(results) {
        searchResultsEl.innerHTML = "";

        if (!results || results.length === 0) {
            const empty = document.createElement("li");
            empty.className = "place-select-search-empty";
            empty.textContent = "검색 결과가 없습니다.";
            searchResultsEl.appendChild(empty);
            return;
        }

        results.forEach(function (result) {
            const item = document.createElement("li");
            item.className = "place-select-search-item";
            item.textContent = result.name
                ? result.name + " (" + result.address + ")"
                : result.address;

            item.addEventListener("click", function () {
                setCurrentPlace({
                    latitude: result.lat,
                    longitude: result.lng,
                    address: result.address,
                    district: result.district,
                    name: result.name || "",
                    kakaoPlaceId: result.kakao_place_id || "",
                });
                moveMapTo(result.lat, result.lng);
                searchSection.classList.add("hidden"); // 선택 완료했으니 검색 영역은 다시 숨김
            });

            searchResultsEl.appendChild(item);
        });
    }

    // ---------------------------------------------------------------------
    // 9. "네" 클릭: 확정된 장소를 서버에 저장(Place 생성) 후 화면 2(구 단위 지도)로 이동.
    // ---------------------------------------------------------------------
    function confirmPlace() {
        // 좌표가 아직 없으면(로딩/실패 상태) 버튼이 disabled라 원래 여기까지 오지 않지만,
        // 방어적으로 한 번 더 확인.
        if (!currentPlace.latitude || !currentPlace.longitude) return;

        confirmBtn.disabled = true; // 중복 클릭 방지

        fetch(API_ENDPOINTS.confirmPlace, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie("csrftoken"),
            },
            body: JSON.stringify({
                latitude: currentPlace.latitude,
                longitude: currentPlace.longitude,
                address: currentPlace.address,
                district: currentPlace.district,
                name: currentPlace.name,
                kakao_place_id: currentPlace.kakaoPlaceId,
            }),
        })
            .then(function (response) {
                if (!response.ok) throw new Error("장소 저장 실패");
                return response.json();
            })
            .then(function (data) {
                // 서버 응답이 { id, redirect_url }을 내려준다고 가정.
                window.location.href = data.redirect_url || "/locations/map/?place=" + data.id;
            })
            .catch(function (error) {
                console.error("[locations] 장소 저장 실패:", error);
                confirmBtn.disabled = false; // 실패했으니 다시 시도할 수 있게 원복
            });
    }

    // ---------------------------------------------------------------------
    // 10. 이벤트 연결 + 초기 실행.
    // ---------------------------------------------------------------------
    manualBtn.addEventListener("click", toggleSearchSection);
    searchBtn.addEventListener("click", searchAddress);
    searchInput.addEventListener("keydown", function (event) {
        // 검색창에서 Enter 입력 시 폼 제출 대신 검색 함수를 바로 실행.
        if (event.key === "Enter") {
            event.preventDefault();
            searchAddress();
        }
    });
    confirmBtn.addEventListener("click", confirmPlace);

    init();
})();

// =========================================================================
// 화면 2. 지도 (locations/templates/locations/map.html) 전용 로직.
//
// 위 IIFE와 이 파일을 공유해서 쓰기 때문에 별도 함수로 분리했고, 화면 1 전용 요소를
// 먼저 찾아보는 위 블록과 마찬가지로 이 블록도 화면 2 전용 요소(#seoul-map-wrap)가
// 없는 페이지에서는 조용히 아무 것도 하지 않고 끝난다.
// =========================================================================
(function () {
    "use strict";

    const mapWrap = document.getElementById("seoul-map-wrap");
    if (!mapWrap) {
        return;
    }

    // map_view(views.py)가 Place.district 값을 그대로 내려준 것.
    // 화면 1을 거치지 않고 곧장 /locations/map/으로 들어온 경우 등은 빈 문자열일 수 있음.
    const selectedDistrict = mapWrap.dataset.selectedDistrict;

    if (!selectedDistrict) {
        // 색칠할 구가 없는 상태(place 파라미터 없음/무효) — 지도는 그냥 기본 색으로 둔다.
        return;
    }

    // seoul_map.html(TODO: 나중에 팀 합의된 SVG로 교체 예정, map.html의 TODO 주석 참고)의
    // 각 <path id="구이름">은 Place.district 값과 정확히 같은 문자열을 id로 가지고 있어서
    // getElementById로 바로 찾을 수 있다.
    // (CSS 선택자 대신 getElementById를 쓰는 이유: id가 한글이라 querySelector에 그대로
    //  넣으면 이스케이프 처리가 필요해서 더 번거롭다.)
    const districtPath = document.getElementById(selectedDistrict);

    if (!districtPath) {
        // SVG 안에 해당 구 이름의 path가 없는 경우(오타, 서울 밖 주소 등). 조용히 무시.
        console.warn("[locations] 지도에서 해당 구를 찾을 수 없습니다:", selectedDistrict);
        return;
    }

    districtPath.classList.add("district-selected");
})();
