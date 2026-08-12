// ============================================================
// 다이어리 상세 페이지 팝업
// ============================================================
//
// Photo 버튼:
// 해당 기록의 사진 팝업 표시.
//
// Read 버튼:
// 해당 기록의 일기 내용 팝업 표시.
//
// 팝업 닫기:
// 1. × 버튼
// 2. 팝업 바깥 배경
// 3. Esc
// ============================================================

document.addEventListener("DOMContentLoaded", () => {
    // 팝업을 열기 직전 초점 요소 저장함.
    let lastFocusedElement = null;


    /**
     * 팝업 열기.
     *
     * @param {HTMLElement} modal 열 팝업 요소
     */
    function openModal(modal) {
        if (!modal) {
            return;
        }

        // 현재 초점 요소 저장함.
        lastFocusedElement = document.activeElement;

        // 팝업 표시함.
        modal.hidden = false;

        // 접근성 상태 변경함.
        modal.setAttribute(
            "aria-hidden",
            "false",
        );

        // 뒤쪽 페이지 스크롤 막음.
        document.body.classList.add(
            "record-content-modal-open",
        );

        // 팝업 닫기 버튼 찾음.
        const closeButton = modal.querySelector(
            ".record-content-modal__close",
        );

        // 닫기 버튼으로 초점 이동함.
        if (closeButton) {
            closeButton.focus();
        }
    }


    /**
     * 팝업 닫기.
     *
     * @param {HTMLElement} modal 닫을 팝업 요소
     */
    function closeModal(modal) {
        if (!modal) {
            return;
        }

        // 팝업 숨김.
        modal.hidden = true;

        // 접근성 상태 변경함.
        modal.setAttribute(
            "aria-hidden",
            "true",
        );

        // 다른 열린 팝업 확인함.
        const openedModal = document.querySelector(
            ".record-content-modal:not([hidden])",
        );

        // 열린 팝업이 없으면 스크롤 제한 해제함.
        if (!openedModal) {
            document.body.classList.remove(
                "record-content-modal-open",
            );
        }

        // 기존 버튼으로 초점 복귀함.
        if (lastFocusedElement) {
            lastFocusedElement.focus();
        }
    }


    // Photo / Read 팝업 버튼 찾음.
    const openButtons = document.querySelectorAll(
        "[data-modal-open]",
    );

    openButtons.forEach((button) => {
        button.addEventListener(
            "click",
            () => {
                const modalId = button.dataset.modalOpen;

                const modal = document.getElementById(
                    modalId,
                );

                openModal(modal);
            },
        );
    });


    // 팝업 닫기 요소 찾음.
    const closeButtons = document.querySelectorAll(
        "[data-modal-close]",
    );

    closeButtons.forEach((button) => {
        button.addEventListener(
            "click",
            () => {
                const modal = button.closest(
                    ".record-content-modal",
                );

                closeModal(modal);
            },
        );
    });


    // Esc 입력 시 현재 팝업 닫음.
    document.addEventListener(
        "keydown",
        (event) => {
            if (event.key !== "Escape") {
                return;
            }

            const openedModal = document.querySelector(
                ".record-content-modal:not([hidden])",
            );

            if (openedModal) {
                closeModal(openedModal);
            }
        },
    );
});