(() => {
    const overlay = document.querySelector("[data-record-modal]");
    if (!overlay) return;

    const modal = overlay.querySelector(".record-modal");
    const openButtons = document.querySelectorAll(
        "#open-record-modal, [data-open-record-modal]"
    );
    const expandButton = document.querySelector("#record-modal-expand");
    const form = document.querySelector("#record-create-form");
    const today = document.querySelector("#record-today");
    const emotionInputs = [
        ...document.querySelectorAll('input[name="emotions"]'),
    ];
    const emotionCount = document.querySelector("#emotion-count");
    const fileInputs = [
        ...document.querySelectorAll(
            'input[name="gallery_image"]'
        ),
    ];
    const photoPreview = document.querySelector("#record-photo-preview");
    const photoEmpty = document.querySelector("#record-photo-empty");
    const photoRemove = document.querySelector("#record-photo-remove");
    const message = document.querySelector("#record-form-message");
    let lastFocusedElement = null;
    let previewUrl = null;

    const setToday = () => {
        if (!today) return;
        today.textContent = new Intl.DateTimeFormat("ko-KR", {
            year: "numeric",
            month: "long",
            day: "numeric",
            weekday: "long",
        }).format(new Date());
    };

    const openModal = () => {
        lastFocusedElement = document.activeElement;
        overlay.hidden = false;
        document.body.classList.add("record-modal-open");
        expandButton?.focus();
    };

    const closeModal = () => {
        overlay.hidden = true;
        modal?.classList.remove("record-modal--fullscreen");
        expandButton?.setAttribute("aria-pressed", "false");
        document.body.classList.remove("record-modal-open");
        lastFocusedElement?.focus();
    };

    const toggleFullscreen = () => {
        const isFullscreen = modal.classList.toggle(
            "record-modal--fullscreen"
        );
        expandButton.setAttribute("aria-pressed", String(isFullscreen));
        expandButton.title = isFullscreen ? "창 크기로 보기" : "전체 화면";
    };

    const updateEmotionState = () => {
        const selected = emotionInputs.filter((input) => input.checked);
        emotionCount.textContent = `${selected.length} / 3`;
        emotionInputs.forEach((input) => {
            input.disabled = selected.length >= 3 && !input.checked;
        });
        message.textContent =
            selected.length >= 3 ? "감정은 최대 3개까지 선택할 수 있어요." : "";
    };

    const showPhoto = (file) => {
        if (!file?.type.startsWith("image/")) return;
        if (previewUrl) URL.revokeObjectURL(previewUrl);
        previewUrl = URL.createObjectURL(file);
        photoPreview.src = previewUrl;
        photoPreview.hidden = false;
        photoEmpty.hidden = true;
        photoRemove.hidden = false;
    };

    const clearPhoto = () => {
        if (previewUrl) URL.revokeObjectURL(previewUrl);
        previewUrl = null;
        photoPreview.removeAttribute("src");
        photoPreview.hidden = true;
        photoEmpty.hidden = false;
        photoRemove.hidden = true;
        fileInputs.forEach((input) => {
            input.value = "";
        });
    };

    openButtons.forEach((button) =>
        button.addEventListener("click", openModal)
    );
    expandButton?.addEventListener("click", toggleFullscreen);
    emotionInputs.forEach((input) =>
        input.addEventListener("change", updateEmotionState)
    );
    fileInputs.forEach((input) =>
        input.addEventListener("change", () => showPhoto(input.files[0]))
    );
    photoRemove?.addEventListener("click", clearPhoto);

    overlay.addEventListener("click", (event) => {
        if (event.target === overlay) closeModal();
    });

    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape" && !overlay.hidden) closeModal();
    });

    form?.addEventListener("submit", (event) => {
        const weather = form.querySelector('input[name="weather"]:checked');
        const content = form.querySelector('textarea[name="content"]');
        if (!weather || !content.value.trim()) {
            event.preventDefault();
            message.textContent = "날씨와 오늘의 마음을 입력해 주세요.";
        }
    });

    setToday();
    updateEmotionState();

    if (document.querySelector("[data-record-preview]")) {
        openModal();
    }
})();
