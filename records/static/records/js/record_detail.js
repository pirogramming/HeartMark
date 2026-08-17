(() => {
    const detailImage = document.querySelector("[data-record-detail-image]");
    const photoFrame = document.querySelector("[data-record-photo-frame]");
    const detailLayout = document.querySelector("[data-record-detail-layout]");

    if (detailImage && photoFrame) {
        const applyPhotoOrientation = () => {
            const { naturalWidth, naturalHeight } = detailImage;
            if (!naturalWidth || !naturalHeight) return;

            const ratio = naturalWidth / naturalHeight;
            photoFrame.style.setProperty(
                "--record-photo-ratio",
                `${naturalWidth} / ${naturalHeight}`,
            );
            photoFrame.classList.remove(
                "record-detail-photo--landscape",
                "record-detail-photo--square",
            );
            detailLayout?.classList.remove(
                "record-detail-layout--landscape",
                "record-detail-layout--square",
            );

            if (ratio >= 1.15) {
                photoFrame.classList.add("record-detail-photo--landscape");
                detailLayout?.classList.add("record-detail-layout--landscape");
            } else if (ratio > 0.85) {
                photoFrame.classList.add("record-detail-photo--square");
                detailLayout?.classList.add("record-detail-layout--square");
            }
        };

        if (detailImage.complete) {
            applyPhotoOrientation();
        } else {
            detailImage.addEventListener("load", applyPhotoOrientation, { once: true });
        }
    }

    const overlay = document.querySelector("#record-delete-overlay");
    const openButton = document.querySelector("#open-record-delete-modal");
    const closeButton = document.querySelector("#close-record-delete-modal");
    if (!overlay || !openButton || !closeButton) return;

    const openModal = () => {
        overlay.hidden = false;
        document.body.classList.add("record-delete-modal-open");
        closeButton.focus();
    };

    const closeModal = () => {
        overlay.hidden = true;
        document.body.classList.remove("record-delete-modal-open");
        openButton.focus();
    };

    openButton.addEventListener("click", openModal);
    closeButton.addEventListener("click", closeModal);
    overlay.addEventListener("click", (event) => {
        if (event.target === overlay) closeModal();
    });
    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape" && !overlay.hidden) closeModal();
    });
})();
