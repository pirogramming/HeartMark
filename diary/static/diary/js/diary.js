// 담당 D 전용

document.addEventListener("DOMContentLoaded", () => {

    /* =========================================================
       1. 감정 색상 정보
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
        감정별 도넛 그래프 색상
    */
    const emotionChartColors = {
        red: "#ef9a9a",
        blue: "#9fc5e8",
        yellow: "#f8dc7d",
        pink: "#efb2c7",
        orange: "#f9c25c",
        purple: "#b3b2db",
        default: "#d4d4d4",
    };


    /*
        구별 색상 모드용 색상 목록
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

    const mapSettingsButton =
        document.querySelector("#map-settings-button");

    const mapSettingsMenu =
        document.querySelector("#map-settings-menu");

    const mapModeButtons =
        document.querySelectorAll("[data-map-mode]");

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

            count: Number(
                element.dataset.count
            ),

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

                // JavaScript fill 제거
                path.style.fill = "";

                // 기록 표시 클래스 제거
                path.classList.remove("has-record");
            });
    }


    /* =========================================================
       6. 선택한 지도 색상 방식 적용
       ========================================================= */

    function applyMapMode(mode) {

        // 기존 지도 색상 초기화
        clearDistrictStyles();


        // 구별 기록 데이터 가져오기
        const mapData =
            getDistrictMapData();


        // 최대 방문 횟수 계산
        const maximumCount = Math.max(
            ...mapData.map(
                (district) => district.count
            ),
            1
        );


        mapData.forEach((district, index) => {

            // 구 이름과 같은 SVG path 탐색
            const path =
                document.getElementById(
                    district.district
                );


            // SVG path가 없는 경우 제외
            if (!path) {
                console.warn(
                    `SVG에서 구를 찾지 못했습니다: ${district.district}`
                );

                return;
            }


            // 기록 있는 구 표시
            path.classList.add("has-record");


            // 동일 색상 모드
            if (mode === "uniform") {
                path.style.fill = "#dce9b7";
            }


            // 최다 감정 색상 모드
            if (mode === "dominant") {
                path.style.fill =
                    emotionColors[
                        district.dominantEmotion
                    ]
                    || "#d4d4d4";
            }


            // 최근 감정 색상 모드
            if (mode === "latest") {
                path.style.fill =
                    emotionColors[
                        district.latestEmotion
                    ]
                    || "#d4d4d4";
            }


            // 방문 횟수 농도 모드
            if (mode === "intensity") {

                const minimumOpacity = 0.05;

                const ratio =
                    district.count
                    / maximumCount;

                const opacity =
                    minimumOpacity
                    + ratio
                    * (1 - minimumOpacity);

                path.style.fill =
                    `rgba(245, 196, 80, ${opacity})`;
            }


            // 구별 다른 색상 모드
            if (mode === "rainbow") {
                path.style.fill =
                    districtColors[
                        index
                        % districtColors.length
                    ];
            }
        });


        // 선택 버튼 active 처리
        mapModeButtons.forEach((button) => {
            button.classList.toggle(
                "active",
                button.dataset.mapMode === mode
            );
        });


        // 선택 모드 저장
        localStorage.setItem(
            "diaryMapMode",
            mode
        );
    }


    /* =========================================================
       7. 장소별 기록 팝업 열기
       ========================================================= */

    function openLocationModal(locationName) {

        // 팝업 요소 없는 경우 종료
        if (
            !locationModal
            || !locationModalName
        ) {
            return;
        }


        let visibleRecordCount = 0;


        // 팝업 장소명 설정
        locationModalName.textContent =
            locationName;


        // 선택한 장소 기록만 표시
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


        // 기록 없음 문구 처리
        if (locationModalEmpty) {
            locationModalEmpty.hidden =
                visibleRecordCount !== 0;
        }


        // 팝업 표시
        locationModal.hidden = false;


        // 배경 스크롤 차단
        document.body.classList.add(
            "modal-open"
        );
    }


    /* =========================================================
       8. 장소별 기록 팝업 닫기
       ========================================================= */

    function closeLocationModal() {

        // 팝업 없는 경우 종료
        if (!locationModal) {
            return;
        }


        // 팝업 숨김
        locationModal.hidden = true;


        // 배경 스크롤 복구
        document.body.classList.remove(
            "modal-open"
        );
    }


    /* =========================================================
       9. 기록 있는 서울 구역 클릭
       ========================================================= */

    districtDataElements.forEach((element) => {

        const districtName =
            element.dataset.district.trim();

        const districtPath =
            document.getElementById(
                districtName
            );


        // SVG path 없는 경우 제외
        if (!districtPath) {
            console.warn(
                `클릭 이벤트를 연결할 구를 찾지 못했습니다: ${districtName}`
            );

            return;
        }


        // 장소 팝업 열기
        districtPath.addEventListener(
            "click",
            () => {
                openLocationModal(
                    districtName
                );
            }
        );
    });


    /* =========================================================
       10. 장소 팝업 닫기
       ========================================================= */

    locationModalCloseButtons.forEach(
        (button) => {

            button.addEventListener(
                "click",
                closeLocationModal
            );
        }
    );


    /* =========================================================
       11. 지도 설정 메뉴
       ========================================================= */

    if (
        mapSettingsButton
        && mapSettingsMenu
    ) {

        // 점 세 개 버튼 클릭
        mapSettingsButton.addEventListener(
            "click",
            (event) => {

                // document 클릭 이벤트 전달 차단
                event.stopPropagation();


                // 변경 후 열림 상태 계산
                const willOpen =
                    mapSettingsMenu.hidden;


                // 메뉴 열기/닫기
                mapSettingsMenu.hidden =
                    !willOpen;


                // 접근성 상태 변경
                mapSettingsButton.setAttribute(
                    "aria-expanded",
                    String(willOpen)
                );
            }
        );


        // 메뉴 내부 클릭 전파 차단
        mapSettingsMenu.addEventListener(
            "click",
            (event) => {
                event.stopPropagation();
            }
        );


        // 메뉴 바깥 클릭 시 닫기
        document.addEventListener(
            "click",
            () => {

                mapSettingsMenu.hidden = true;

                mapSettingsButton.setAttribute(
                    "aria-expanded",
                    "false"
                );
            }
        );
    }


    /* =========================================================
       12. 지도 색상 방식 선택
       ========================================================= */

    mapModeButtons.forEach((button) => {

        button.addEventListener(
            "click",
            () => {

                // 선택 모드 가져오기
                const selectedMode =
                    button.dataset.mapMode;


                // 지도 색상 변경
                applyMapMode(
                    selectedMode
                );


                // 설정 메뉴 닫기
                if (mapSettingsMenu) {
                    mapSettingsMenu.hidden = true;
                }


                // 접근성 상태 변경
                if (mapSettingsButton) {
                    mapSettingsButton.setAttribute(
                        "aria-expanded",
                        "false"
                    );
                }
            }
        );
    });


    /* =========================================================
       13. 저장된 지도 색상 적용
       ========================================================= */

    if (districtDataElements.length > 0) {

        const savedMapMode =
            localStorage.getItem(
                "diaryMapMode"
            )
            || "dominant";


        applyMapMode(
            savedMapMode
        );
    }


    /* =========================================================
       14. 전체 기록 필터 요소
       ========================================================= */

    const sortSelect =
        document.querySelector("#diary-sort");

    const filterForm =
        document.querySelector(
            "#diary-filter-form"
        );

    const periodToggleButton =
        document.querySelector(
            "#period-toggle-button"
        );

    const periodFilter =
        document.querySelector(
            "#period-filter"
        );


    /* =========================================================
       15. 최신순·과거순 변경
       ========================================================= */

    if (
        sortSelect
        && filterForm
    ) {

        sortSelect.addEventListener(
            "change",
            () => {
                filterForm.submit();
            }
        );
    }


    /* =========================================================
       16. 기간 설정창 열기
       ========================================================= */

    function openPeriodFilter() {

        // 필수 요소 없는 경우 종료
        if (
            !periodToggleButton
            || !periodFilter
        ) {
            return;
        }


        // 기간 설정창 표시
        periodFilter.hidden = false;


        // 버튼 활성화
        periodToggleButton.classList.add(
            "active"
        );


        // 접근성 상태 변경
        periodToggleButton.setAttribute(
            "aria-expanded",
            "true"
        );
    }


    /* =========================================================
       17. 기간 설정창 닫기
       ========================================================= */

    function closePeriodFilter() {

        // 필수 요소 없는 경우 종료
        if (
            !periodToggleButton
            || !periodFilter
        ) {
            return;
        }


        // 기간 설정창 숨김
        periodFilter.hidden = true;


        // 버튼 활성화 제거
        periodToggleButton.classList.remove(
            "active"
        );


        // 접근성 상태 변경
        periodToggleButton.setAttribute(
            "aria-expanded",
            "false"
        );
    }


    /* =========================================================
       18. 기간 설정 버튼 클릭
       ========================================================= */

    if (
        periodToggleButton
        && periodFilter
    ) {

        periodToggleButton.addEventListener(
            "click",
            () => {

                const shouldOpen =
                    periodFilter.hidden;


                if (shouldOpen) {
                    openPeriodFilter();
                } else {
                    closePeriodFilter();
                }
            }
        );


        /* =====================================================
           19. 기간 설정창 바깥 클릭
           ===================================================== */

        document.addEventListener(
            "click",
            (event) => {

                const clickedElement =
                    event.target;


                // 기간 설정 버튼 클릭 여부
                const clickedToggleButton =
                    periodToggleButton.contains(
                        clickedElement
                    );


                // 기간 설정창 내부 클릭 여부
                const clickedInsidePeriodFilter =
                    periodFilter.contains(
                        clickedElement
                    );


                // 외부 클릭 시 닫기
                if (
                    !clickedToggleButton
                    && !clickedInsidePeriodFilter
                ) {
                    closePeriodFilter();
                }
            }
        );
    }

            /* =========================================================
       20. 감정별 기록 팝업 요소
       ========================================================= */

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

    function openEmotionModal(
        emotionIds,
        emotionNames
    ) {

        // 필수 요소 없는 경우 종료
        if (
            !modal
            || !modalName
            || !modalEmpty
        ) {
            return;
        }


        // 단일 ID도 배열로 변환
        const normalizedIds =
            Array.isArray(emotionIds)
                ? emotionIds.map(String)
                : [String(emotionIds)];


        // 감정명도 배열로 변환
        const normalizedNames =
            Array.isArray(emotionNames)
                ? emotionNames
                : [emotionNames];


        let visibleRecordCount = 0;


        // 팝업 제목 설정
        modalName.textContent =
            normalizedNames.join(" · ");


        // 선택 감정 그룹 기록 표시
        modalRecords.forEach((record) => {

            const recordEmotion =
                String(
                    record.dataset.recordEmotion
                );


            const isMatched =
                normalizedIds.includes(
                    recordEmotion
                );


            record.hidden =
                !isMatched;


            if (isMatched) {
                visibleRecordCount += 1;
            }
        });


        // 기록 없음 문구 처리
        modalEmpty.hidden =
            visibleRecordCount !== 0;


        // 팝업 표시
        modal.hidden = false;


        // 배경 스크롤 차단
        document.body.classList.add(
            "modal-open"
        );
    }


    /* =========================================================
       22. 감정별 기록 팝업 닫기
       ========================================================= */

    function closeEmotionModal() {

        // 팝업 없는 경우 종료
        if (!modal) {
            return;
        }


        // 팝업 숨김
        modal.hidden = true;


        // 배경 스크롤 복구
        document.body.classList.remove(
            "modal-open"
        );
    }


    /* =========================================================
       23. 감정 도넛 그래프 요소
       ========================================================= */

    const emotionChart =
        document.querySelector(
            "#emotion-chart"
        );

    const emotionChartSegments =
        document.querySelector(
            "#emotion-chart-segments"
        );

    const emotionChartWrapper =
        document.querySelector(
            "#emotion-chart-wrapper"
        );

    const emotionChartTooltip =
        document.querySelector(
            "#emotion-chart-tooltip"
        );

    const emotionChartDataItems =
        document.querySelectorAll(
            "#emotion-chart-data .emotion-chart-data-item"
        );


    /* =========================================================
       24. 색상 그룹별 감정 데이터 생성
       ========================================================= */

    function getEmotionChartGroups() {

        const groupedData = {};


        emotionChartDataItems.forEach(
            (element) => {

                const emotionId =
                    element.dataset.emotionId.trim();

                const emotionName =
                    element.dataset.emotionName.trim();

                const emotionCount =
                    Number(
                        element.dataset.emotionCount
                    );

                const colorGroup =
                    element.dataset.emotionColorGroup.trim();


                // 잘못된 데이터 제외
                if (
                    !emotionId
                    || !emotionName
                    || emotionCount <= 0
                ) {
                    return;
                }


                // 색상 그룹 최초 생성
                if (!groupedData[colorGroup]) {

                    groupedData[colorGroup] = {
                        colorGroup,
                        count: 0,
                        emotionIds: [],
                        emotionNames: [],
                    };
                }


                // 기록 횟수 합산
                groupedData[colorGroup].count +=
                    emotionCount;


                // 감정 ID 추가
                if (
                    !groupedData[
                        colorGroup
                    ].emotionIds.includes(
                        emotionId
                    )
                ) {
                    groupedData[
                        colorGroup
                    ].emotionIds.push(
                        emotionId
                    );
                }


                // 감정 이름 추가
                if (
                    !groupedData[
                        colorGroup
                    ].emotionNames.includes(
                        emotionName
                    )
                ) {
                    groupedData[
                        colorGroup
                    ].emotionNames.push(
                        emotionName
                    );
                }
            }
        );


        return Object.values(
            groupedData
        );
    }


    /* =========================================================
       25. 도넛 그래프 툴팁 표시
       ========================================================= */

    function showEmotionChartTooltip(
        emotionNames,
        event
    ) {

        // 필수 요소 없는 경우 종료
        if (
            !emotionChartTooltip
            || !emotionChartWrapper
        ) {
            return;
        }


        // 감정 이름 표시
        emotionChartTooltip.textContent =
            emotionNames.join(" · ");


        // 툴팁 표시
        emotionChartTooltip.hidden = false;


        const wrapperRect =
            emotionChartWrapper.getBoundingClientRect();


        const tooltipX =
            event.clientX
            - wrapperRect.left;

        const tooltipY =
            event.clientY
            - wrapperRect.top;


        // 마우스 위쪽 배치
        emotionChartTooltip.style.left =
            `${tooltipX}px`;

        emotionChartTooltip.style.top =
            `${tooltipY - 18}px`;
    }


    /* =========================================================
       26. 도넛 그래프 툴팁 제거
       ========================================================= */

    function hideEmotionChartTooltip() {

        if (!emotionChartTooltip) {
            return;
        }


        emotionChartTooltip.hidden = true;
    }


    /* =========================================================
       27. SVG 도넛 그래프 생성
       ========================================================= */

    function renderEmotionChart() {

        // 그래프 없는 경우 종료
        if (
            !emotionChart
            || !emotionChartSegments
        ) {
            return;
        }


        // 기존 조각 제거
        emotionChartSegments.innerHTML = "";


        const chartGroups =
            getEmotionChartGroups();


        // 데이터 없는 경우 종료
        if (chartGroups.length === 0) {
            return;
        }


        // 전체 기록 수 계산
        const totalCount =
            chartGroups.reduce(
                (sum, group) =>
                    sum + group.count,
                0
            );


        if (totalCount <= 0) {
            return;
        }


        // SVG 원 정보
        const centerX = 160;
        const centerY = 160;
        const radius = 112;


        // 전체 원 둘레
        const circumference =
            2 * Math.PI * radius;


        /*
            조각 사이 간격

            값 증가
            → 조각 사이 흰색 간격 증가
        */
        const segmentGap = 5;


        /*
            12시 방향 시작

            기본 circle 시작점은 오른쪽이므로
            rotate(-90deg) 적용
        */
        let currentLength = 0;


        chartGroups.forEach((group) => {

            const ratio =
                group.count
                / totalCount;


            // 실제 그룹 길이
            const segmentLength =
                circumference * ratio;


            // 흰색 간격 제외
            const visibleLength =
                Math.max(
                    segmentLength
                    - segmentGap,
                    1
                );


            const segment =
                document.createElementNS(
                    "http://www.w3.org/2000/svg",
                    "circle"
                );


            segment.setAttribute(
                "cx",
                centerX
            );

            segment.setAttribute(
                "cy",
                centerY
            );

            segment.setAttribute(
                "r",
                radius
            );


            segment.classList.add(
                "emotion-chart-segment"
            );


            segment.classList.add(
                `emotion-chart-segment--${group.colorGroup}`
            );


            /*
                현재 조각만 표시

                visibleLength
                → 보이는 부분

                나머지
                → 숨겨지는 부분
            */
            segment.style.strokeDasharray =
                `${visibleLength} ${
                    circumference - visibleLength
                }`;


            /*
                조각 시작 위치 이동
            */
            segment.style.strokeDashoffset =
                `${-currentLength}`;


            // hover 데이터 저장
            segment.dataset.emotionIds =
                group.emotionIds.join(",");

            segment.dataset.emotionNames =
                group.emotionNames.join("|");


            // hover 툴팁 표시
            segment.addEventListener(
                "mouseenter",
                (event) => {

                    showEmotionChartTooltip(
                        group.emotionNames,
                        event
                    );
                }
            );


            // 툴팁 위치 이동
            segment.addEventListener(
                "mousemove",
                (event) => {

                    showEmotionChartTooltip(
                        group.emotionNames,
                        event
                    );
                }
            );


            // 툴팁 제거
            segment.addEventListener(
                "mouseleave",
                hideEmotionChartTooltip
            );


            /*
                색상 조각 클릭

                해당 그룹에 포함된 모든 대표 감정 기록 표시
            */
            segment.addEventListener(
                "click",
                () => {

                    hideEmotionChartTooltip();


                    openEmotionModal(
                        group.emotionIds,
                        group.emotionNames
                    );
                }
            );


            emotionChartSegments.appendChild(
                segment
            );


            // 다음 조각 시작 위치 계산
            currentLength +=
                segmentLength;
        });
    }


    /* =========================================================
       28. 도넛 그래프 생성
       ========================================================= */

    renderEmotionChart();


    /* =========================================================
       29. 감정 카드 클릭
       ========================================================= */

    const emotionRecordCards =
        document.querySelectorAll(
            "[data-emotion-card]"
        );


    emotionRecordCards.forEach(
        (card) => {

            card.addEventListener(
                "click",
                () => {

                    openEmotionModal(
                        card.dataset.emotionId,
                        card.dataset.emotionName
                    );
                }
            );
        }
    );

        /* =========================================================
       감정 카드 한 줄 표시 개수 계산
       ========================================================= */

        /* =========================================================
       감정 카드 한 줄 표시 개수 계산
       ========================================================= */

    function updateVisibleEmotionCards() {

        const cardList =
            document.querySelector(
                ".emotion-record-card-list"
            );


        // 카드 목록 없는 경우 종료
        if (!cardList) {
            return;
        }


        const cards =
            Array.from(
                emotionRecordCards
            );


        // 카드 없는 경우 종료
        if (cards.length === 0) {
            return;
        }


        // 모든 카드 우선 표시
        cards.forEach((card) => {
            card.hidden = false;
        });


        // 카드 목록 실제 너비
        const containerWidth =
            cardList.clientWidth;


        // 카드 사이 간격 계산
        const computedStyle =
            window.getComputedStyle(
                cardList
            );

        const gap =
            parseFloat(
                computedStyle.gap
            )
            || 0;


        let usedWidth = 0;

        let overflowStarted = false;


        cards.forEach((card, index) => {

            /*
                이미 앞 카드에서 공간 초과 발생한 경우
                이후 카드 전부 숨김
            */
            if (overflowStarted) {
                card.hidden = true;

                return;
            }


            // 현재 카드 실제 너비
            const cardWidth =
                card.getBoundingClientRect().width;


            /*
                첫 번째 카드 제외
                앞 카드와의 gap 포함
            */
            const requiredWidth =
                cardWidth
                + (
                    index > 0
                        ? gap
                        : 0
                );


            /*
                현재 카드를 추가했을 때
                한 줄 영역을 넘는 경우
            */
            if (
                usedWidth
                + requiredWidth
                > containerWidth
            ) {
                // 현재 카드 숨김
                card.hidden = true;

                // 이후 카드도 모두 숨기도록 표시
                overflowStarted = true;

                return;
            }


            // 현재 카드 너비 누적
            usedWidth +=
                requiredWidth;
        });
    }

        /* =========================================================
       감정 카드 최초 표시 개수 계산
       ========================================================= */

    updateVisibleEmotionCards();


    /* =========================================================
       화면 크기 변경 시 감정 카드 재계산
       ========================================================= */

    window.addEventListener(
        "resize",
        updateVisibleEmotionCards
    );


    /* =========================================================
       30. 감정 팝업 닫기
       ========================================================= */

    closeButtons.forEach((button) => {

        button.addEventListener(
            "click",
            closeEmotionModal
        );
    });

});    