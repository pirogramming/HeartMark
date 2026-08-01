// 담당 D 전용

document.addEventListener("DOMContentLoaded", () => {
    const emotionColors = {
        "화남": "#ef9a9a",
        "분노": "#ef9a9a",

        "슬픔": "#9fc5e8",
        "불안": "#9fc5e8",
        "걱정": "#9fc5e8",
        "우울": "#9fc5e8",
        "긴장": "#9fc5e8",
        "피로": "#9fc5e8",
        "답답": "#9fc5e8",
        "지침": "#9fc5e8",

        "기쁨": "#f8dc7d",
        "행복": "#f8dc7d",
        "감사": "#f8dc7d",
        "감사함": "#f8dc7d",
        "설렘": "#f8dc7d",
        "평온": "#f8dc7d",
        "안정": "#f8dc7d",

        "뿌듯": "#efb2c7",
        "뿌듯함": "#efb2c7",
        "성취": "#efb2c7",
        "기대": "#efb2c7",
        "자신감": "#efb2c7",

        "외로움": "#b9d99d",
        "민망함": "#b9d99d"
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

    /* HTML 데이터를 JavaScripts 객체로 변환 */
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

    /* 기존 지도 색상 초기화하는 함수 */
    function clearDistrictStyles() {
        document
            .querySelectorAll(".seoul-map path")
            .forEach((path) => {
                path.style.fill = "";
                path.classList.remove("has-record");
            });
    }

    /* 색상 방식 적용 함수 추가 */
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

                /* 노란색 */
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

    /* 점 세 개 메뉴 여닫는 코드 */
    if (mapSettingsButton && mapSettingsMenu) {
        mapSettingsButton.addEventListener("click", () => {
            const isOpen = !mapSettingsMenu.hidden;

            mapSettingsMenu.hidden = isOpen;

            mapSettingsButton.setAttribute(
                "aria-expanded",
                String(!isOpen)
            );
        });
    }

    if (districtDataElements.length > 0) {
        const savedMapMode =
            localStorage.getItem("diaryMapMode")
            || "dominant";

        applyMapMode(savedMapMode);
    }

    /* 색상 방식 클릭 */
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
        if (event.key === "Escape" && !modal.hidden) {
            closeEmotionModal();
        }
    });
});