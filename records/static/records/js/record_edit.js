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
    const photoFrame = form.querySelector("#record-edit-photo");
    const editMain = form.querySelector(".record-edit-main");
    const emptyState = form.querySelector("#record-edit-photo-empty");
    let previewUrl = null;
    let showRequiredMessage = false;

    const applyPhotoOrientation = () => {
        if (!preview?.naturalWidth || !preview?.naturalHeight) return;
        const ratio = preview.naturalWidth / preview.naturalHeight;
        photoFrame?.classList.remove(
            "record-edit-photo--landscape",
            "record-edit-photo--square",
        );
        editMain?.classList.remove("record-edit-main--landscape");
        if (ratio >= 1.15) {
            photoFrame?.classList.add("record-edit-photo--landscape");
            editMain?.classList.add("record-edit-main--landscape");
        } else if (ratio > 0.85) {
            photoFrame?.classList.add("record-edit-photo--square");
        }
    };

    if (preview && !preview.hidden) {
        if (preview.complete) applyPhotoOrientation();
        else preview.addEventListener("load", applyPhotoOrientation, { once: true });
    }

    const keepOnlyFirstPhoto = (input) => {
        const selectedFiles = Array.from(input.files || []);
        if (selectedFiles.length <= 1) return selectedFiles[0] || null;

        try {
            const singleFile = new DataTransfer();
            singleFile.items.add(selectedFiles[0]);
            input.files = singleFile.files;
            return input.files[0];
        } catch (error) {
            input.value = "";
            return null;
        }
    };

    const getMissingLabels = () => {
        const weather = form.querySelector('input[name="weather"]:checked');
        const content = form.querySelector('textarea[name="content"]');
        const emotions = emotionInputs.filter((input) => input.checked);
        const missing = [];
        if (!weather) missing.push("날씨");
        if (!content?.value.trim()) missing.push("오늘의 마음");
        if (!emotions.length) missing.push("감정");
        return missing;
    };

    const updateRequiredMessage = () => {
        const missing = getMissingLabels();
        if (showRequiredMessage) {
            message.textContent = missing.length
                ? `${missing.join(" · ")} 입력이 필요해요.`
                : "";
        }
        return missing.length === 0;
    };

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
        updateRequiredMessage();
    }));
    updateEmotions();

    imageInput?.removeAttribute("multiple");
    imageInput?.addEventListener("change", () => {
        const file = keepOnlyFirstPhoto(imageInput);
        if (!file?.type.startsWith("image/")) return;
        if (previewUrl) URL.revokeObjectURL(previewUrl);
        previewUrl = URL.createObjectURL(file);
        preview.src = previewUrl;
        preview.onload = applyPhotoOrientation;
        preview.hidden = false;
        emptyState.hidden = true;
        updateRequiredMessage();
    });

    form.addEventListener("submit", (event) => {
        showRequiredMessage = true;
        if (!updateRequiredMessage()) {
            event.preventDefault();
        }
    });

    form.querySelectorAll('input[name="weather"], textarea[name="content"]')
        .forEach((field) => field.addEventListener("input", updateRequiredMessage));
})();
