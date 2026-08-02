(() => {
    const form = document.querySelector(".record-edit-paper");
    if (!form) return;

    document.body.classList.add("record-edit-open");

    const emotionInputs = [...form.querySelectorAll('input[name="emotions"]')];
    const emotionCount = form.querySelector("#record-edit-emotion-count");
    const mainEmotionInput = form.querySelector("#record-edit-main-emotion");
    const message = form.querySelector("#record-edit-message");
    const imageInput = form.querySelector("#record-edit-image-input");
    const preview = form.querySelector("#record-edit-preview");
    const emptyState = form.querySelector("#record-edit-photo-empty");
    let previewUrl = null;

    const updateEmotions = () => {
        const selected = emotionInputs.filter((input) => input.checked);
        if (mainEmotionInput && !mainEmotionInput.value && selected.length) {
            mainEmotionInput.value = selected[0].value;
        }
        emotionCount.textContent = `${selected.length} / 3`;
        emotionInputs.forEach((input) => {
            input.disabled = selected.length >= 3 && !input.checked;
        });
        message.textContent = selected.length >= 3
            ? "감정은 최대 3개까지 선택할 수 있어요."
            : "";
        emotionInputs.forEach((input) => {
            input.closest(".emotion-option")?.classList.toggle(
                "emotion-option--main",
                input.checked && input.value === mainEmotionInput?.value,
            );
        });
    };

    emotionInputs.forEach((input) => input.addEventListener("change", () => {
        if (mainEmotionInput) {
            if (input.checked && !mainEmotionInput.value) {
                mainEmotionInput.value = input.value;
            } else if (!input.checked && mainEmotionInput.value === input.value) {
                mainEmotionInput.value = emotionInputs.find(
                    (candidate) => candidate.checked
                )?.value || "";
            }
        }
        updateEmotions();
    }));
    updateEmotions();

    imageInput?.addEventListener("change", () => {
        const file = imageInput.files[0];
        if (!file?.type.startsWith("image/")) return;
        if (previewUrl) URL.revokeObjectURL(previewUrl);
        previewUrl = URL.createObjectURL(file);
        preview.src = previewUrl;
        preview.hidden = false;
        emptyState.hidden = true;
    });

    form.addEventListener("submit", (event) => {
        const weather = form.querySelector('input[name="weather"]:checked');
        const content = form.querySelector('textarea[name="content"]');
        const emotions = emotionInputs.filter((input) => input.checked);
        const hasImage = !emptyState || emptyState.hidden || imageInput?.files.length;
        if (!weather || !hasImage || !content.value.trim() || !emotions.length) {
            event.preventDefault();
            message.textContent = "사진, 날씨, 감정과 오늘의 마음을 모두 입력해 주세요.";
        }
    });
})();
