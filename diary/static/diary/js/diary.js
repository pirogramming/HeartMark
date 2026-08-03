// 담당 D 전용

document.addEventListener("DOMContentLoaded", () => {
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


    /* =========================
            장소 팝업 요소
    ========================= */

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


    /* HTML 데이터를 JavaScript 객체로 변환 */

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


    /* 기존 지도 색상 초기화 */

    function clearDistrictStyles() {
        document
            .querySelectorAll(".seoul-map path")
            .forEach((path) => {
                path.style.fill = "";
                path.classList.remove("has-record");
            });
    }


    /* 선택한 지도 색상 방식 적용 */

    function applyMapMode(mode) {
        clearDistrictStyles();

        const mapData = getDistrictMapData();

        const maximumCount = Math.max(
            ...mapData.map((district) => district.count),
            1
        );

        mapData.forEach((district, index) => {
            const path =
                document.getElementById(district.district);

            if (!path) {
                console.warn(
                    `SVG에서 구를 찾지 못했습니다: ${district.district}`
                );
                return;
            }

            path.classList.add("has-record");

            if (mode === "uniform") {
                path.style.fill = "#dce9b7";
            }

            if (mode === "dominant") {
                path.style.fill =
                    emotionColors[district.dominantEmotion]
                    || "#d4d4d4";
            }

            if (mode === "latest") {
                path.style.fill =
                    emotionColors[district.latestEmotion]
                    || "#d4d4d4";
            }

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

            if (mode === "rainbow") {
                path.style.fill =
                    districtColors[
                        index % districtColors.length
                    ];
            }
        });

        mapModeButtons.forEach((button) => {
            button.classList.toggle(
                "active",
                button.dataset.mapMode === mode
            );
        });

        localStorage.setItem("diaryMapMode", mode);
    }


    /* =========================
            장소 팝업
    ========================= */

    function openLocationModal(locationName) {
        if (!locationModal || !locationModalName) {
            return;
        }

        let visibleRecordCount = 0;

        locationModalName.textContent = locationName;

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

        if (locationModalEmpty) {
            locationModalEmpty.hidden =
                visibleRecordCount !== 0;
        }

        locationModal.hidden = false;
        document.body.classList.add("modal-open");
    }


    function closeLocationModal() {
        if (!locationModal) {
            return;
        }

        locationModal.hidden = true;
        document.body.classList.remove("modal-open");
    }


    /* 기록이 있는 구에 클릭 이벤트 연결 */

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
        * tabindex를 넣지 않습니다.
        * SVG에 직사각형 포커스 테두리가 나타나는 것을 방지합니다.
        */
        districtPath.addEventListener("click", () => {
            openLocationModal(districtName);
        });
    });


    /* 장소 팝업 닫기 */

    locationModalCloseButtons.forEach((button) => {
        button.addEventListener(
            "click",
            closeLocationModal
        );
    });


    /* =========================
            점 세 개 메뉴
    ========================= */

    if (mapSettingsButton && mapSettingsMenu) {
        mapSettingsButton.addEventListener("click", (event) => {
            event.stopPropagation();

            const willOpen = mapSettingsMenu.hidden;

            mapSettingsMenu.hidden = !willOpen;

            mapSettingsButton.setAttribute(
                "aria-expanded",
                String(willOpen)
            );
        });

        mapSettingsMenu.addEventListener("click", (event) => {
            event.stopPropagation();
        });

        document.addEventListener("click", () => {
            mapSettingsMenu.hidden = true;

            mapSettingsButton.setAttribute(
                "aria-expanded",
                "false"
            );
        });
    }


    /* 지도 색상 방식 선택 */

    mapModeButtons.forEach((button) => {
        button.addEventListener("click", () => {
            const selectedMode =
                button.dataset.mapMode;

            applyMapMode(selectedMode);

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


    /* 페이지 진입 시 저장된 색상 모드 적용 */

    if (districtDataElements.length > 0) {
        const savedMapMode =
            localStorage.getItem("diaryMapMode")
            || "dominant";

        applyMapMode(savedMapMode);
    }

    const sortSelect = document.querySelector("#diary-sort");
    const filterForm = document.querySelector("#diary-filter-form");

    const periodToggleButton = document.querySelector(
        "#period-toggle-button"
    );
    const periodFilter = document.querySelector("#period-filter");

    if (sortSelect && filterForm) {
        sortSelect.addEventListener("change", () => {
            filterForm.submit();
        });
    }

    if (periodToggleButton && periodFilter) {
        periodToggleButton.addEventListener("click", () => {
            const isOpen = !periodFilter.hidden;

            periodFilter.hidden = isOpen;
            periodToggleButton.classList.toggle("active", !isOpen);
            periodToggleButton.setAttribute(
                "aria-expanded",
                String(!isOpen)
            );
        });
    }
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

    function openEmotionModal(emotionId, emotionName) {
        let visibleRecordCount = 0;

        modalName.textContent = emotionName;

        modalRecords.forEach((record) => {
            const isMatched =
                record.dataset.recordEmotion === emotionId;

            record.hidden = !isMatched;

            if (isMatched) {
                visibleRecordCount += 1;
            }
        });

        modalEmpty.hidden = visibleRecordCount !== 0;
        modal.hidden = false;

        document.body.classList.add("modal-open");
    }

    function closeEmotionModal() {
        modal.hidden = true;
        document.body.classList.remove("modal-open");
    }

    emotionButtons.forEach((button) => {
        button.addEventListener("click", () => {
            openEmotionModal(
                button.dataset.emotionId,
                button.dataset.emotionName
            );
        });
    });

    closeButtons.forEach((button) => {
        button.addEventListener("click", closeEmotionModal);
    });

    document.addEventListener("keydown", (event) => {
        if (event.key !== "Escape") {
            return;
        }

        if (modal && !modal.hidden) {
            closeEmotionModal();
        }

        if (locationModal && !locationModal.hidden) {
            closeLocationModal();
        }

        if (mapSettingsMenu && !mapSettingsMenu.hidden) {
            mapSettingsMenu.hidden = true;

            if (mapSettingsButton) {
                mapSettingsButton.setAttribute(
                    "aria-expanded",
                    "false"
                );
            }
        }
    });
});