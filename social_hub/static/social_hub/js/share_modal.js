document.addEventListener("DOMContentLoaded", () => {
    const modal = document.querySelector("#share-letter-modal");
    if (!modal) return;

    const panel = modal.querySelector(".share-letter");
    const formView = modal.querySelector("[data-share-form-view]");
    const successView = modal.querySelector("[data-share-success]");
    const friendRows = [...modal.querySelectorAll("[data-share-friend]")];
    const checkboxes = friendRows.map((row) => row.querySelector("input[type='checkbox']"));
    const searchInput = modal.querySelector("#share-friend-search");
    const searchEmpty = modal.querySelector("[data-share-search-empty]");
    const chipBox = modal.querySelector("[data-selected-chips]");
    const selectedCount = modal.querySelector("[data-selected-count]");
    const footerCount = modal.querySelector("[data-footer-count]");
    const successCount = modal.querySelector("[data-success-count]");
    const sendButton = modal.querySelector("[data-send-share]");
    const locationInput = modal.querySelector("#share-location");
    const shareForm = modal.querySelector("[data-share-form]");
    const recordSelect = modal.querySelector("[data-share-record-select]");
    let lastFocused = null;

    function selectedFriends() {
        return friendRows.filter((row) => row.querySelector("input").checked);
    }

    function updateSelection() {
        const selected = selectedFriends();
        const count = selected.length;

        friendRows.forEach((row) => {
            row.classList.toggle("is-selected", row.querySelector("input").checked);
        });
        if (selectedCount) selectedCount.textContent = `${count}명`;
        if (footerCount) footerCount.textContent = `${count}명`;

        if (sendButton) {
            sendButton.disabled = count === 0;
            sendButton.textContent = count ? "마음 편지 보내기" : "친구를 선택해 주세요";
        }

        if (!chipBox) return;
        chipBox.replaceChildren();
        if (!count) {
            const empty = document.createElement("p");
            empty.textContent = "아직 선택한 친구가 없어요.";
            chipBox.append(empty);
            return;
        }

        selected.forEach((row) => {
            const input = row.querySelector("input");
            const name = row.querySelector("strong").textContent.trim();
            const image = row.querySelector("img");
            const chip = document.createElement("button");
            chip.type = "button";
            chip.className = "share-selected__chip";
            chip.dataset.removeFriend = input.value;
            chip.setAttribute("aria-label", `${name} 선택 취소`);

            const chipImage = document.createElement("img");
            chipImage.src = image.src;
            chipImage.alt = "";
            const chipName = document.createElement("span");
            chipName.textContent = name;
            const chipClose = document.createElement("b");
            chipClose.setAttribute("aria-hidden", "true");
            chipClose.textContent = "×";
            chip.append(chipImage, chipName, chipClose);
            chipBox.append(chip);
        });
    }

    function resetModal() {
        checkboxes.forEach((checkbox) => (checkbox.checked = false));
        if (locationInput) locationInput.checked = false;
        if (recordSelect) recordSelect.value = "";
        if (searchInput) searchInput.value = "";
        friendRows.forEach((row) => (row.hidden = false));
        if (searchEmpty) searchEmpty.hidden = true;
        if (formView) formView.hidden = false;
        if (successView) successView.hidden = true;
        updateSelection();
    }

    function openModal(preselectId) {
        lastFocused = document.activeElement;
        resetModal();
        const preselected = checkboxes.find((checkbox) => checkbox.value === preselectId);
        if (preselected) preselected.checked = true;
        updateSelection();
        modal.hidden = false;
        document.body.classList.add("share-modal-open");
        window.requestAnimationFrame(() => panel?.classList.add("is-visible"));
        modal.querySelector("[data-close-share-modal]")?.focus();
    }

    function closeModal() {
        panel?.classList.remove("is-visible");
        window.setTimeout(() => {
            modal.hidden = true;
            document.body.classList.remove("share-modal-open");
            lastFocused?.focus();
        }, 180);
    }

    document.querySelectorAll("[data-open-share-modal]").forEach((button) => {
        button.addEventListener("click", () => openModal(button.dataset.preselectFriend || ""));
    });

    modal.querySelectorAll("[data-close-share-modal]").forEach((button) => {
        button.addEventListener("click", closeModal);
    });

    modal.addEventListener("click", (event) => {
        if (event.target === modal) closeModal();
        const removeButton = event.target.closest("[data-remove-friend]");
        if (!removeButton) return;
        const checkbox = checkboxes.find((item) => item.value === removeButton.dataset.removeFriend);
        if (checkbox) checkbox.checked = false;
        updateSelection();
    });

    checkboxes.forEach((checkbox) => checkbox.addEventListener("change", updateSelection));

    searchInput?.addEventListener("input", () => {
        const keyword = searchInput.value.trim().toLocaleLowerCase("ko");
        let visibleCount = 0;
        friendRows.forEach((row) => {
            const visible = row.dataset.friendName.includes(keyword);
            row.hidden = !visible;
            if (visible) visibleCount += 1;
        });
        if (searchEmpty) searchEmpty.hidden = visibleCount !== 0;
    });

    shareForm?.addEventListener("submit", (event) => {
        const count = selectedFriends().length;
        const selectedRecord = recordSelect?.selectedOptions[0];
        const shareUrl = selectedRecord?.dataset.shareUrl;
        if (!count || !shareUrl) {
            event.preventDefault();
            if (recordSelect && !recordSelect.value) recordSelect.focus();
            return;
        }
        shareForm.action = shareUrl;
        sendButton.disabled = true;
        sendButton.textContent = "마음 편지를 보내는 중...";
    });

    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape" && !modal.hidden) closeModal();
    });
});
