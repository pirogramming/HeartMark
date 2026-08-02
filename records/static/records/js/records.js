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
    const mainEmotionInput = document.querySelector("#main-emotion");
    const fileInputs = [
        ...document.querySelectorAll(
            'input[name="image"]'
        ),
    ];
    const photoPreview = document.querySelector("#record-photo-preview");
    const photoEmpty = document.querySelector("#record-photo-empty");
    const photoRemove = document.querySelector("#record-photo-remove");
    const message = document.querySelector("#record-form-message");
    const completionCard = document.querySelector("#record-completion-card");
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

    const openModal = (event) => {
        event?.preventDefault();
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
        if (mainEmotionInput && !mainEmotionInput.value && selected.length) {
            mainEmotionInput.value = selected[0].value;
        }
        emotionCount.textContent = `${selected.length} / 3`;
        emotionInputs.forEach((input) => {
            input.disabled = selected.length >= 3 && !input.checked;
        });
        message.textContent =
            selected.length >= 3 ? "감정은 최대 3개까지 선택할 수 있어요." : "";
        emotionInputs.forEach((input) => {
            input.closest(".emotion-option")?.classList.toggle(
                "emotion-option--main",
                input.checked && input.value === mainEmotionInput?.value,
            );
        });
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

    const getCompletionState = () => ({
        image: fileInputs.some((input) => input.files.length > 0),
        weather: Boolean(form?.querySelector('input[name="weather"]:checked')),
        content: Boolean(form?.querySelector('textarea[name="content"]')?.value.trim()),
        emotions: emotionInputs.some((input) => input.checked),
    });

    const updateCompletionCard = (showWhenIncomplete = false) => {
        if (!completionCard) return;
        const state = getCompletionState();
        Object.entries(state).forEach(([name, isComplete]) => {
            const item = completionCard.querySelector(`[data-requirement="${name}"]`);
            item?.classList.toggle("is-complete", isComplete);
            const status = item?.querySelector("b");
            if (status) status.textContent = isComplete ? "✓" : "!";
        });
        const isComplete = Object.values(state).every(Boolean);
        completionCard.hidden = isComplete || (!showWhenIncomplete && completionCard.hidden);
        return { state, isComplete };
    };

    openButtons.forEach((button) =>
        button.addEventListener("click", openModal)
    );
    expandButton?.addEventListener("click", toggleFullscreen);
    emotionInputs.forEach((input) =>
        input.addEventListener("change", () => {
            if (mainEmotionInput) {
                if (input.checked && !mainEmotionInput.value) {
                    mainEmotionInput.value = input.value;
                } else if (!input.checked && mainEmotionInput.value === input.value) {
                    mainEmotionInput.value = emotionInputs.find(
                        (candidate) => candidate.checked
                    )?.value || "";
                }
            }
            updateEmotionState();
            updateCompletionCard(!completionCard?.hidden);
        })
    );
    fileInputs.forEach((input) =>
        input.addEventListener("change", () => {
            showPhoto(input.files[0]);
            updateCompletionCard(!completionCard?.hidden);
        })
    );
    photoRemove?.addEventListener("click", () => {
        clearPhoto();
        updateCompletionCard(!completionCard?.hidden);
    });

    overlay.addEventListener("click", (event) => {
        if (event.target === overlay) closeModal();
    });

    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape" && !overlay.hidden) closeModal();
    });

    form?.addEventListener("submit", (event) => {
        const completion = updateCompletionCard(true);
        if (!completion?.isComplete) {
            event.preventDefault();
            completionCard.hidden = false;
        }
    });

    form?.querySelectorAll('input[name="weather"], textarea[name="content"]')
        .forEach((field) => field.addEventListener("input", () => {
            updateCompletionCard(!completionCard?.hidden);
        }));

    setToday();
    updateEmotionState();

    if (document.querySelector("[data-record-preview]")) {
        openModal();
    }
})();
