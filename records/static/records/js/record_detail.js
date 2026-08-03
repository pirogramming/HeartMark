(() => {
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
