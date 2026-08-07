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
       20. 감정 도넛 그래프 요소
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
       21. 감정 데이터를 색상 그룹별로 합치기
       ========================================================= */

    function getEmotionChartGroups() {

        // 색상 그룹별 임시 저장 객체
        const groupedData = {};


        emotionChartDataItems.forEach(
            (element) => {

                // 감정 이름
                const emotionName =
                    element.dataset.emotionName.trim();


                // 대표 감정 기록 횟수
                const emotionCount =
                    Number(
                        element.dataset.emotionCount
                    );


                // 색상 그룹 이름
                const colorGroup =
                    element.dataset.emotionColorGroup.trim();


                // 잘못된 데이터 제외
                if (
                    !emotionName
                    || emotionCount <= 0
                ) {
                    return;
                }


                // 최초 색상 그룹 생성
                if (!groupedData[colorGroup]) {

                    groupedData[colorGroup] = {
                        colorGroup: colorGroup,
                        count: 0,
                        emotionNames: [],
                    };
                }


                // 기록 횟수 합산
                groupedData[colorGroup].count +=
                    emotionCount;


                // 감정 이름 중복 제거 후 추가
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


        // 객체를 배열로 변환
        return Object.values(
            groupedData
        );
    }


    /* =========================================================
       22. 감정 그래프 툴팁 표시
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


        // 감정 이름만 표시
        emotionChartTooltip.textContent =
            emotionNames.join(" · ");


        // 툴팁 표시
        emotionChartTooltip.hidden = false;


        // wrapper 위치 계산
        const wrapperRect =
            emotionChartWrapper.getBoundingClientRect();


        // 마우스 기준 툴팁 위치
        const tooltipX =
            event.clientX
            - wrapperRect.left;

        const tooltipY =
            event.clientY
            - wrapperRect.top;


        // 마우스보다 약간 위쪽에 배치
        emotionChartTooltip.style.left =
            `${tooltipX}px`;

        emotionChartTooltip.style.top =
            `${tooltipY - 16}px`;
    }


    /* =========================================================
       23. 감정 그래프 툴팁 숨기기
       ========================================================= */

    function hideEmotionChartTooltip() {

        // 툴팁 없는 경우 종료
        if (!emotionChartTooltip) {
            return;
        }


        // 툴팁 숨김
        emotionChartTooltip.hidden = true;
    }


    /* =========================================================
       24. 감정 SVG 도넛 그래프 생성
       ========================================================= */

    function renderEmotionChart() {

        // 그래프 요소 없는 경우 종료
        if (
            !emotionChart
            || !emotionChartSegments
        ) {
            return;
        }


        // 기존 그래프 조각 제거
        emotionChartSegments.innerHTML = "";


        // 색상 그룹별 데이터 생성
        const chartGroups =
            getEmotionChartGroups();


        // 기록 없는 경우 종료
        if (chartGroups.length === 0) {
            return;
        }


        // 전체 대표 감정 기록 수 계산
        const totalCount =
            chartGroups.reduce(
                (sum, group) =>
                    sum + group.count,
                0
            );


        // 전체 기록 없는 경우 종료
        if (totalCount <= 0) {
            return;
        }


        /*
            SVG 원 정보

            emotion_list.html:
            cx = 160
            cy = 160
            r  = 110
        */
        const centerX = 160;
        const centerY = 160;
        const radius = 110;


        // 원 둘레 계산
        const circumference =
            2 * Math.PI * radius;


        /*
            조각 사이 간격

            값 증가
            → 조각 사이 간격 증가

            값 감소
            → 조각 사이 간격 감소
        */
        const segmentGap = 7;


        /*
            시작 위치

            SVG 원은 기본적으로 오른쪽에서 시작함.

            -circumference / 4 적용
            → 그래프 시작점을 12시 방향으로 이동
        */
        let currentOffset =
            -circumference / 4;


        chartGroups.forEach((group) => {

            // 그룹 비율 계산
            const ratio =
                group.count / totalCount;


            // 그룹이 차지하는 원 둘레 길이
            const segmentLength =
                circumference * ratio;


            /*
                실제 표시 길이에서 간격 제거

                너무 작은 조각이 사라지는 문제 방지용
                최소 길이 1 적용
            */
            const visibleLength =
                Math.max(
                    segmentLength
                    - segmentGap,
                    1
                );


            // SVG circle 생성
            const segment =
                document.createElementNS(
                    "http://www.w3.org/2000/svg",
                    "circle"
                );


            // 기본 원 위치 설정
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


            // CSS 클래스 추가
            segment.classList.add(
                "emotion-chart-segment"
            );


            // 색상 그룹 클래스 추가
            segment.classList.add(
                `emotion-chart-segment--${group.colorGroup}`
            );


            // 실제 stroke 색상 적용
            segment.style.stroke =
                emotionChartColors[
                    group.colorGroup
                ]
                || emotionChartColors.default;


            /*
                현재 조각 길이 설정

                첫 번째 값
                → 실제 표시되는 선 길이

                두 번째 값
                → 나머지 비어 있는 선 길이
            */
            segment.style.strokeDasharray =
                `${visibleLength} ${
                    circumference
                    - visibleLength
                }`;


            // 현재 조각 시작 위치 설정
            segment.style.strokeDashoffset =
                `${-currentOffset}`;


            /*
                hover에서 사용할 감정 이름 저장

                예:
                "기쁨|만족|신남"
            */
            segment.dataset.emotionNames =
                group.emotionNames.join("|");


            /*
                마우스 진입 시 툴팁 표시
            */
            segment.addEventListener(
                "mouseenter",
                (event) => {

                    showEmotionChartTooltip(
                        group.emotionNames,
                        event
                    );
                }
            );


            /*
                조각 위에서 마우스 이동 시
                툴팁 위치도 함께 이동
            */
            segment.addEventListener(
                "mousemove",
                (event) => {

                    showEmotionChartTooltip(
                        group.emotionNames,
                        event
                    );
                }
            );


            /*
                마우스 이탈 시 툴팁 제거
            */
            segment.addEventListener(
                "mouseleave",
                hideEmotionChartTooltip
            );


            // SVG에 조각 추가
            emotionChartSegments.appendChild(
                segment
            );


            // 다음 조각 시작 위치 계산
            currentOffset +=
                segmentLength;
        });
    }


    /* =========================================================
       25. 감정 도넛 그래프 초기 생성
       ========================================================= */

    renderEmotionChart();


    /* =========================================================
       26. 감정별 기록 팝업 요소
       ========================================================= */

    /*
        기존 emotion_modal.html 기능 유지.

        현재 도넛 그래프에서는
        감정 클릭 기능을 연결하지 않음.

        추후 그래프 클릭 또는 별도 감정 버튼 추가 시
        openEmotionModal() 재사용 가능.
    */

    const modal =
        document.querySelector(
            "#emotion-modal"
        );

    const modalName =
        document.querySelector(
            "#emotion-modal-name"
        );

    const modalRecords =
        document.querySelectorAll(
            ".emotion-modal-record"
        );

    const modalEmpty =
        document.querySelector(
            "#emotion-modal-empty"
        );

    const closeButtons =
        document.querySelectorAll(
            "[data-modal-close]"
        );


    /* =========================================================
       27. 감정별 기록 팝업 열기
       ========================================================= */

    function openEmotionModal(
        emotionId,
        emotionName
    ) {

        // 팝업 요소 없는 경우 종료
        if (
            !modal
            || !modalName
            || !modalEmpty
        ) {
            return;
        }


        let visibleRecordCount = 0;


        // 팝업 감정 이름 설정
        modalName.textContent =
            emotionName;


        // 선택 감정 기록만 표시
        modalRecords.forEach((record) => {

            const isMatched =
                record.dataset.recordEmotion
                === emotionId;


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
       28. 감정별 기록 팝업 닫기
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
       29. 감정 팝업 닫기
       ========================================================= */

    closeButtons.forEach((button) => {

        button.addEventListener(
            "click",
            closeEmotionModal
        );
    });


    /* =========================================================
       30. Escape 키 처리
       ========================================================= */

    document.addEventListener(
        "keydown",
        (event) => {

            // Escape 아닌 경우 종료
            if (event.key !== "Escape") {
                return;
            }


            // 감정 팝업 닫기
            if (
                modal
                && !modal.hidden
            ) {
                closeEmotionModal();
            }


            // 장소 팝업 닫기
            if (
                locationModal
                && !locationModal.hidden
            ) {
                closeLocationModal();
            }


            // 지도 설정 메뉴 닫기
            if (
                mapSettingsMenu
                && !mapSettingsMenu.hidden
            ) {
                mapSettingsMenu.hidden = true;


                if (mapSettingsButton) {

                    mapSettingsButton.setAttribute(
                        "aria-expanded",
                        "false"
                    );
                }
            }


            // 기간 설정창 닫기
            if (
                periodFilter
                && !periodFilter.hidden
            ) {
                closePeriodFilter();
            }


            // 감정 툴팁 제거
            hideEmotionChartTooltip();
        }
    );
});