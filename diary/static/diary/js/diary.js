// 담당 D 전용

document.addEventListener("DOMContentLoaded", () => {
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