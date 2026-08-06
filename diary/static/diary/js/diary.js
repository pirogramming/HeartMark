// 담당 D 전용

document.addEventListener("DOMContentLoaded", () => {

    /* =========================================================
       1. 지도 감정 색상 정보
       ========================================================= */

    const emotionColors = {
        "심술": "#ef9a9a",
        "화남": "#ef9a9a",
        "질투": "#ef9a9a",

        "슬픔": "#9fc5e8",
        "아픔": "#9fc5e8",

        "기쁨": "#f8dc7d",
        "만족": "#f8dc7d",
        "신남": "#f8dc7d",
        "행운": "#f8dc7d",
        "맛있어!": "#f8dc7d",

        "사랑": "#efb2c7",
        "짝사랑": "#efb2c7",

        "당황": "#f9c25c",
        "놀람": "#f9c25c",

        "따분": "#b3b2db",
        "졸림": "#b3b2db",
        "예민": "#b3b2db",
        "냉철": "#b3b2db",
    };


    /*
        지도에서 '구별로 다른 색' 모드를 선택했을 때
        각 구에 순서대로 적용할 색상 목록입니다.
    */
    const districtColors = [
        "#f3b7b7",
        "#f2cf87",
        "#b8d8ec",
        "#c6dca7",
        "#d5bee8",
        "#f1bdd0",
        "#abd8cf",
        "#e5c0a6",
        "#c8c3e8",
        "#efd6a6",
        "#aed7ef",
        "#b8dfbe",
        "#e7b9ae",
        "#d4c5a5",
        "#c5d8e5"
    ];


    /* =========================================================
       2. 지도 설정 요소
       ========================================================= */

    /*
        지도 오른쪽 위의 점 세 개 버튼입니다.
    */
    const mapSettingsButton =
        document.querySelector("#map-settings-button");


    /*
        점 세 개 버튼을 눌렀을 때 열리는
        지도 색상 설정 메뉴입니다.
    */
    const mapSettingsMenu =
        document.querySelector("#map-settings-menu");


    /*
        지도 색상 방식을 선택하는 버튼들입니다.

        예:
        - 같은 색으로 통일
        - 가장 많은 감정 색
        - 가장 최근 감정 색
        - 방문 횟수에 따른 농도
        - 구별로 다른 색
    */
    const mapModeButtons =
        document.querySelectorAll("[data-map-mode]");


    /*
        Django가 HTML에 넣어둔 구별 기록 데이터입니다.
    */
    const districtDataElements =
        document.querySelectorAll(
            "#district-map-data [data-district]"
        );


    /* =========================================================
       3. 장소별 기록 팝업 요소
       ========================================================= */

    const locationModal =
        document.querySelector("#location-modal");

    const locationModalName =
        document.querySelector("#location-modal-name");

    const locationModalRecords =
        document.querySelectorAll(".location-modal-record");

    const locationModalEmpty =
        document.querySelector("#location-modal-empty");

    const locationModalCloseButtons =
        document.querySelectorAll(
            "[data-location-modal-close]"
        );


    /* =========================================================
       4. HTML 지도 데이터를 JavaScript 객체로 변환
       ========================================================= */

    function getDistrictMapData() {
        return Array.from(districtDataElements).map((element) => ({
            district: element.dataset.district.trim(),
            count: Number(element.dataset.count),

            dominantEmotion:
                element.dataset.dominantEmotion.trim(),

            latestEmotion:
                element.dataset.latestEmotion.trim()
        }));
    }


    /* =========================================================
       5. 기존 지도 색상 초기화
       ========================================================= */

    function clearDistrictStyles() {
        document
            .querySelectorAll(".seoul-map path")
            .forEach((path) => {

                /*
                    JavaScript로 직접 넣었던 fill 색상을 제거합니다.
                */
                path.style.fill = "";


                /*
                    기록이 있는 구에 붙었던 클래스를 제거합니다.
                */
                path.classList.remove("has-record");
            });
    }


    /* =========================================================
       6. 선택한 지도 색상 방식 적용
       ========================================================= */

    function applyMapMode(mode) {

        /*
            새로운 색상을 적용하기 전에
            이전 지도 색상을 먼저 초기화합니다.
        */
        clearDistrictStyles();


        /*
            HTML에 담긴 구별 데이터를 배열로 가져옵니다.
        */
        const mapData = getDistrictMapData();


        /*
            방문 횟수 농도를 계산하기 위해
            가장 방문 횟수가 많은 구의 기록 수를 구합니다.

            기록이 없을 때 0으로 나누는 문제를 막기 위해
            최소값을 1로 설정합니다.
        */
        const maximumCount = Math.max(
            ...mapData.map((district) => district.count),
            1
        );


        mapData.forEach((district, index) => {

            /*
                district.district와 같은 id를 가진
                서울 지도 SVG path를 찾습니다.

                예:
                district.district가 "성북구"라면
                id="성북구"인 path를 찾습니다.
            */
            const path =
                document.getElementById(district.district);


            if (!path) {
                console.warn(
                    `SVG에서 구를 찾지 못했습니다: ${district.district}`
                );

                return;
            }


            /*
                기록이 있는 구라는 표시를 추가합니다.
            */
            path.classList.add("has-record");


            /*
                모든 기록된 구를 같은 색으로 표시합니다.
            */
            if (mode === "uniform") {
                path.style.fill = "#dce9b7";
            }


            /*
                해당 구에서 가장 많이 기록된 감정의 색상을 사용합니다.
            */
            if (mode === "dominant") {
                path.style.fill =
                    emotionColors[district.dominantEmotion]
                    || "#d4d4d4";
            }


            /*
                해당 구에서 가장 최근에 기록한 감정의 색상을 사용합니다.
            */
            if (mode === "latest") {
                path.style.fill =
                    emotionColors[district.latestEmotion]
                    || "#d4d4d4";
            }


            /*
                방문 횟수가 많을수록 색을 진하게 표시합니다.
            */
            if (mode === "intensity") {
                const minimumOpacity = 0.05;

                const ratio =
                    district.count / maximumCount;

                const opacity =
                    minimumOpacity
                    + ratio * (1 - minimumOpacity);

                path.style.fill =
                    `rgba(245, 196, 80, ${opacity})`;
            }


            /*
                각 구에 서로 다른 색상을 순서대로 적용합니다.
            */
            if (mode === "rainbow") {
                path.style.fill =
                    districtColors[
                        index % districtColors.length
                    ];
            }
        });


        /*
            현재 선택한 지도 색상 방식 버튼에만
            active 클래스를 추가합니다.
        */
        mapModeButtons.forEach((button) => {
            button.classList.toggle(
                "active",
                button.dataset.mapMode === mode
            );
        });


        /*
            새로고침한 뒤에도 선택한 지도 색상 방식이
            유지되도록 브라우저 저장소에 저장합니다.
        */
        localStorage.setItem("diaryMapMode", mode);
    }


    /* =========================================================
       7. 장소별 기록 팝업 열기
       ========================================================= */

    function openLocationModal(locationName) {

        /*
            장소 팝업 요소가 없는 페이지에서는
            아래 코드를 실행하지 않습니다.
        */
        if (!locationModal || !locationModalName) {
            return;
        }


        /*
            선택한 장소와 일치하는 기록의 개수입니다.
        */
        let visibleRecordCount = 0;


        /*
            팝업 제목에 선택한 구 이름을 넣습니다.
        */
        locationModalName.textContent = locationName;


        /*
            해당 구에 작성된 기록만 표시합니다.
        */
        locationModalRecords.forEach((record) => {
            const recordLocation =
                record.dataset.recordLocation.trim();

            const isMatched =
                recordLocation === locationName;

            record.hidden = !isMatched;

            if (isMatched) {
                visibleRecordCount += 1;
            }
        });


        /*
            일치하는 기록이 없다면
            빈 기록 안내 문구를 표시합니다.
        */
        if (locationModalEmpty) {
            locationModalEmpty.hidden =
                visibleRecordCount !== 0;
        }


        /*
            장소별 기록 팝업을 엽니다.
        */
        locationModal.hidden = false;


        /*
            팝업이 열린 동안 뒤쪽 페이지 스크롤을 막습니다.
        */
        document.body.classList.add("modal-open");
    }


    /* =========================================================
       8. 장소별 기록 팝업 닫기
       ========================================================= */

    function closeLocationModal() {
        if (!locationModal) {
            return;
        }

        locationModal.hidden = true;

        document.body.classList.remove("modal-open");
    }


    /* =========================================================
       9. 기록이 있는 서울 구역 클릭 이벤트
       ========================================================= */

    districtDataElements.forEach((element) => {
        const districtName =
            element.dataset.district.trim();

        const districtPath =
            document.getElementById(districtName);


        if (!districtPath) {
            console.warn(
                `클릭 이벤트를 연결할 구를 찾지 못했습니다: ${districtName}`
            );

            return;
        }


        /*
            tabindex는 넣지 않습니다.

            SVG를 클릭했을 때 직사각형 포커스 테두리가
            나타나는 문제를 방지합니다.
        */
        districtPath.addEventListener("click", () => {
            openLocationModal(districtName);
        });
    });


    /* =========================================================
       10. 장소별 기록 팝업 닫기 버튼
       ========================================================= */

    locationModalCloseButtons.forEach((button) => {
        button.addEventListener(
            "click",
            closeLocationModal
        );
    });


    /* =========================================================
       11. 지도 점 세 개 설정 메뉴
       ========================================================= */

    if (mapSettingsButton && mapSettingsMenu) {

        /*
            점 세 개 버튼을 누르면
            지도 설정 메뉴를 열거나 닫습니다.
        */
        mapSettingsButton.addEventListener("click", (event) => {

            /*
                버튼 클릭이 document 클릭 이벤트까지
                전달되는 것을 막습니다.

                이 코드가 없으면 메뉴를 열자마자
                아래 document 클릭 이벤트가 실행되어
                다시 닫힐 수 있습니다.
            */
            event.stopPropagation();


            /*
                현재 메뉴가 숨겨져 있다면 true입니다.
            */
            const willOpen = mapSettingsMenu.hidden;


            /*
                숨겨져 있었다면 열고,
                열려 있었다면 닫습니다.
            */
            mapSettingsMenu.hidden = !willOpen;


            /*
                접근성 상태도 메뉴 상태와 맞춰 변경합니다.
            */
            mapSettingsButton.setAttribute(
                "aria-expanded",
                String(willOpen)
            );
        });


        /*
            설정 메뉴 내부를 클릭했을 때는
            document 클릭 이벤트로 전달되지 않게 합니다.
        */
        mapSettingsMenu.addEventListener("click", (event) => {
            event.stopPropagation();
        });


        /*
            지도 설정 메뉴 바깥을 클릭하면
            설정 메뉴를 닫습니다.
        */
        document.addEventListener("click", () => {
            mapSettingsMenu.hidden = true;

            mapSettingsButton.setAttribute(
                "aria-expanded",
                "false"
            );
        });
    }


    /* =========================================================
       12. 지도 색상 방식 선택
       ========================================================= */

    mapModeButtons.forEach((button) => {
        button.addEventListener("click", () => {

            /*
                클릭한 버튼의 data-map-mode 값을 가져옵니다.
            */
            const selectedMode =
                button.dataset.mapMode;


            /*
                선택한 방식으로 지도 색상을 변경합니다.
            */
            applyMapMode(selectedMode);


            /*
                색상 방식 선택 후 설정 메뉴를 닫습니다.
            */
            if (mapSettingsMenu) {
                mapSettingsMenu.hidden = true;
            }

            if (mapSettingsButton) {
                mapSettingsButton.setAttribute(
                    "aria-expanded",
                    "false"
                );
            }
        });
    });


    /* =========================================================
       13. 페이지 진입 시 저장된 지도 색상 방식 적용
       ========================================================= */

    if (districtDataElements.length > 0) {
        const savedMapMode =
            localStorage.getItem("diaryMapMode")
            || "dominant";

        applyMapMode(savedMapMode);
    }


    /* =========================================================
       14. 전체 기록 정렬 및 기간 설정 요소
       ========================================================= */

    /*
        최신순·과거순 선택창입니다.
    */
    const sortSelect =
        document.querySelector("#diary-sort");


    /*
        최신순과 기간 설정을 포함하는 전체 폼입니다.
    */
    const filterForm =
        document.querySelector("#diary-filter-form");


    /*
        기간 설정창을 여는 버튼입니다.
    */
    const periodToggleButton =
        document.querySelector("#period-toggle-button");


    /*
        시작일·종료일·적용·초기화가 들어 있는
        실제 기간 설정창입니다.
    */
    const periodFilter =
        document.querySelector("#period-filter");


    /* =========================================================
       15. 최신순·과거순 선택 시 자동 제출
       ========================================================= */

    if (sortSelect && filterForm) {
        sortSelect.addEventListener("change", () => {
            filterForm.submit();
        });
    }


    /* =========================================================
       16. 기간 설정창 열기
       ========================================================= */

    function openPeriodFilter() {

        /*
            현재 페이지에 기간 설정 요소가 없다면
            함수를 종료합니다.
        */
        if (!periodToggleButton || !periodFilter) {
            return;
        }


        /*
            hidden 속성을 제거해 기간 설정창을 표시합니다.
        */
        periodFilter.hidden = false;


        /*
            기간 설정 버튼에 active 클래스를 추가합니다.

            CSS의
            .period-toggle-button.active
            스타일이 적용됩니다.
        */
        periodToggleButton.classList.add("active");


        /*
            스크린 리더에 설정창이 열렸다는 것을 전달합니다.
        */
        periodToggleButton.setAttribute(
            "aria-expanded",
            "true"
        );
    }


    /* =========================================================
       17. 기간 설정창 닫기
       ========================================================= */

    function closePeriodFilter() {

        /*
            현재 페이지에 기간 설정 요소가 없다면
            함수를 종료합니다.
        */
        if (!periodToggleButton || !periodFilter) {
            return;
        }


        /*
            hidden 속성을 추가해 기간 설정창을 숨깁니다.
        */
        periodFilter.hidden = true;


        /*
            버튼의 활성화 스타일을 제거합니다.
        */
        periodToggleButton.classList.remove("active");


        /*
            스크린 리더에 설정창이 닫혔다는 것을 전달합니다.
        */
        periodToggleButton.setAttribute(
            "aria-expanded",
            "false"
        );
    }


    /* =========================================================
       18. 기간 설정 버튼 클릭
       ========================================================= */

    if (periodToggleButton && periodFilter) {
        periodToggleButton.addEventListener("click", () => {

            /*
                버튼을 누르기 전에 기간 설정창이
                숨겨져 있었는지 확인합니다.

                true
                → 현재 닫혀 있으므로 열어야 합니다.

                false
                → 현재 열려 있으므로 닫아야 합니다.
            */
            const shouldOpen = periodFilter.hidden;


            if (shouldOpen) {
                openPeriodFilter();
            } else {
                closePeriodFilter();
            }
        });


        /* =====================================================
           19. 기간 설정창 바깥 클릭 시 닫기
           ===================================================== */

        document.addEventListener("click", (event) => {

            /*
                실제로 클릭된 HTML 요소입니다.
            */
            const clickedElement = event.target;


            /*
                클릭한 위치가 기간 설정 버튼 내부인지 확인합니다.

                버튼의 글자 부분을 클릭해도 true가 됩니다.
            */
            const clickedToggleButton =
                periodToggleButton.contains(clickedElement);


            /*
                클릭한 위치가 기간 설정창 내부인지 확인합니다.

                다음 요소를 클릭했을 때 true가 됩니다.

                - 시작 날짜 입력창
                - 종료 날짜 입력창
                - 적용 버튼
                - 초기화 버튼
                - 기간 설정창의 빈 공간
            */
            const clickedInsidePeriodFilter =
                periodFilter.contains(clickedElement);


            /*
                기간 설정 버튼도 아니고,
                기간 설정창 내부도 아니라면
                팝업 바깥을 클릭한 것입니다.
            */
            if (
                !clickedToggleButton
                && !clickedInsidePeriodFilter
            ) {
                closePeriodFilter();
            }
        });
    }


    /* =========================================================
       20. 감정별 기록 팝업 요소
       ========================================================= */

    const emotionButtons =
        document.querySelectorAll(".emotion-bubble");

    const modal =
        document.querySelector("#emotion-modal");

    const modalName =
        document.querySelector("#emotion-modal-name");

    const modalRecords =
        document.querySelectorAll(".emotion-modal-record");

    const modalEmpty =
        document.querySelector("#emotion-modal-empty");

    const closeButtons =
        document.querySelectorAll("[data-modal-close]");


    /* =========================================================
       21. 감정별 기록 팝업 열기
       ========================================================= */

    function openEmotionModal(emotionId, emotionName) {

        /*
            감정별 기록 팝업 요소가 없다면
            함수를 실행하지 않습니다.
        */
        if (!modal || !modalName || !modalEmpty) {
            return;
        }


        let visibleRecordCount = 0;


        /*
            팝업 제목에 선택한 감정 이름을 넣습니다.
        */
        modalName.textContent = emotionName;


        /*
            선택한 감정과 일치하는 기록만 표시합니다.
        */
        modalRecords.forEach((record) => {
            const isMatched =
                record.dataset.recordEmotion === emotionId;

            record.hidden = !isMatched;

            if (isMatched) {
                visibleRecordCount += 1;
            }
        });


        /*
            표시할 기록이 없다면 빈 안내 문구를 표시합니다.
        */
        modalEmpty.hidden = visibleRecordCount !== 0;


        /*
            감정별 기록 팝업을 표시합니다.
        */
        modal.hidden = false;


        /*
            팝업 뒤쪽 페이지의 스크롤을 막습니다.
        */
        document.body.classList.add("modal-open");
    }


    /* =========================================================
       22. 감정별 기록 팝업 닫기
       ========================================================= */

    function closeEmotionModal() {
        if (!modal) {
            return;
        }

        modal.hidden = true;

        document.body.classList.remove("modal-open");
    }


    /* =========================================================
       23. 감정 조약돌 클릭
       ========================================================= */

    emotionButtons.forEach((button) => {
        button.addEventListener("click", () => {
            openEmotionModal(
                button.dataset.emotionId,
                button.dataset.emotionName
            );
        });
    });


    /* =========================================================
       24. 감정 팝업 닫기 버튼 및 배경 클릭
       ========================================================= */

    closeButtons.forEach((button) => {
        button.addEventListener(
            "click",
            closeEmotionModal
        );
    });


    /* =========================================================
       25. Escape 키로 열린 요소 닫기
       ========================================================= */

    document.addEventListener("keydown", (event) => {

        /*
            누른 키가 Escape가 아니라면
            아래 코드를 실행하지 않습니다.
        */
        if (event.key !== "Escape") {
            return;
        }


        /*
            감정별 기록 팝업이 열려 있다면 닫습니다.
        */
        if (modal && !modal.hidden) {
            closeEmotionModal();
        }


        /*
            장소별 기록 팝업이 열려 있다면 닫습니다.
        */
        if (locationModal && !locationModal.hidden) {
            closeLocationModal();
        }


        /*
            지도 점 세 개 설정 메뉴가 열려 있다면 닫습니다.
        */
        if (mapSettingsMenu && !mapSettingsMenu.hidden) {
            mapSettingsMenu.hidden = true;

            if (mapSettingsButton) {
                mapSettingsButton.setAttribute(
                    "aria-expanded",
                    "false"
                );
            }
        }


        /*
            기간 설정창이 열려 있다면 닫습니다.
        */
        if (periodFilter && !periodFilter.hidden) {
            closePeriodFilter();
        }
    });
});