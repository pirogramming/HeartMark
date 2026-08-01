(() => {
    const form = document.querySelector(".record-edit-paper");
    if (!form) return;

    document.body.classList.add("record-edit-open");

    const emotionInputs = [...form.querySelectorAll('input[name="emotions"]')];
    const emotionCount = form.querySelector("#record-edit-emotion-count");
    const message = form.querySelector("#record-edit-message");
    const imageInput = form.querySelector("#record-edit-image-input");
    const preview = form.querySelector("#record-edit-preview");
    const emptyState = form.querySelector("#record-edit-photo-empty");
    let previewUrl = null;

    const updateEmotions = () => {
        const selected = emotionInputs.filter((input) => input.checked);
        emotionCount.textContent = `${selected.length} / 3`;
        emotionInputs.forEach((input) => {
            input.disabled = selected.length >= 3 && !input.checked;
        });
        message.textContent = selected.length >= 3
            ? "감정은 최대 3개까지 선택할 수 있어요."
            : "";
    };

    emotionInputs.forEach((input) => input.addEventListener("change", updateEmotions));
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
        if (!weather || !content.value.trim()) {
            event.preventDefault();
            message.textContent = "날씨와 오늘의 마음을 입력해 주세요.";
        }
    });
})();
