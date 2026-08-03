// 작성 디테일 페이지 js파일
// ============================================================
// 다이어리 상세 페이지 팝업
// ============================================================
//
// Photo 버튼:
// 해당 기록에 업로드된 사진 팝업을 엽니다.
//
// Read 버튼:
// 해당 기록에 작성된 일기 내용 팝업을 엽니다.
//
// 팝업을 닫는 방법:
// 1. 오른쪽 위 × 버튼
// 2. 팝업 바깥의 어두운 배경
// 3. 키보드 Esc 키
//

document.addEventListener("DOMContentLoaded", () => {
    // 팝업을 열기 직전에 선택되어 있던 버튼을 저장합니다.
    //
    // 팝업을 닫은 후 해당 버튼으로
    // 키보드 초점을 다시 돌려주기 위해 사용합니다.
    let lastFocusedElement = null;


    /**
     * 전달받은 팝업을 엽니다.
     *
     * @param {HTMLElement} modal - 열 팝업 요소
     */
    function openModal(modal) {
        if (!modal) {
            return;
        }

        // 현재 초점이 위치한 버튼을 기억합니다.
        lastFocusedElement = document.activeElement;

        // hidden 속성을 제거하여 팝업을 화면에 표시합니다.
        modal.hidden = false;

        // 보조 기술에 팝업이 열렸음을 알립니다.
        modal.setAttribute("aria-hidden", "false");

        // 팝업이 열렸을 때
        // 뒤쪽 페이지의 스크롤을 막습니다.
        document.body.classList.add(
            "record-content-modal-open"
        );

        // 팝업 안의 닫기 버튼을 찾습니다.
        const closeButton = modal.querySelector(
            ".record-content-modal__close"
        );

        // 키보드 사용자가 바로 닫을 수 있도록
        // 닫기 버튼에 초점을 이동합니다.
        if (closeButton) {
            closeButton.focus();
        }
    }


    /**
     * 전달받은 팝업을 닫습니다.
     *
     * @param {HTMLElement} modal - 닫을 팝업 요소
     */
    function closeModal(modal) {
        if (!modal) {
            return;
        }

        // 팝업을 다시 숨깁니다.
        modal.hidden = true;

        // 보조 기술에 팝업이 닫혔음을 알립니다.
        modal.setAttribute("aria-hidden", "true");

        // 다른 열린 팝업이 있는지 확인합니다.
        const openedModal = document.querySelector(
            '.record-content-modal:not([hidden])'
        );

        // 다른 팝업이 없다면
        // 페이지 스크롤 제한을 해제합니다.
        if (!openedModal) {
            document.body.classList.remove(
                "record-content-modal-open"
            );
        }

        // 팝업을 열었던 버튼으로
        // 키보드 초점을 되돌립니다.
        if (lastFocusedElement) {
            lastFocusedElement.focus();
        }
    }


    // data-modal-open 속성을 가진 모든 버튼을 찾습니다.
    const openButtons = document.querySelectorAll(
        "[data-modal-open]"
    );

    openButtons.forEach((button) => {
        button.addEventListener("click", () => {
            // 예:
            // data-modal-open="photo-modal"
            // → id가 photo-modal인 요소를 찾습니다.
            const modalId = button.dataset.modalOpen;

            const modal = document.getElementById(
                modalId
            );

            openModal(modal);
        });
    });


    // × 버튼과 어두운 배경처럼
    // data-modal-close가 있는 모든 요소를 찾습니다.
    const closeButtons = document.querySelectorAll(
        "[data-modal-close]"
    );

    closeButtons.forEach((button) => {
        button.addEventListener("click", () => {
            // 닫기 버튼이 속한 가장 가까운 팝업을 찾습니다.
            const modal = button.closest(
                ".record-content-modal"
            );

            closeModal(modal);
        });
    });


    // 키보드 Esc를 누르면
    // 현재 열려 있는 팝업을 닫습니다.
    document.addEventListener("keydown", (event) => {
        if (event.key !== "Escape") {
            return;
        }

        const openedModal = document.querySelector(
            '.record-content-modal:not([hidden])'
        );

        if (openedModal) {
            closeModal(openedModal);
        }
    });
});