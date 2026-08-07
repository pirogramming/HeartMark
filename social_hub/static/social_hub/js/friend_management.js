document.addEventListener("DOMContentLoaded", () => {
    const tabs = [...document.querySelectorAll("[data-friend-tab]")];
    const panels = [...document.querySelectorAll("[data-friend-panel]")];
    const searchInput = document.querySelector("#friend-search");
    const confirmLayer = document.querySelector("#friend-confirm");
    const confirmMessage = document.querySelector("#friend-confirm-message");
    const deleteForm = document.querySelector("#friend-delete-form");

    function selectTab(tabName) {
        tabs.forEach((tab) => {
            const selected = tab.dataset.friendTab === tabName;
            tab.classList.toggle("is-active", selected);
            tab.setAttribute("aria-selected", String(selected));
        });
        panels.forEach((panel) => {
            const selected = panel.dataset.friendPanel === tabName;
            panel.classList.toggle("is-active", selected);
            panel.hidden = !selected;
        });
        if (searchInput) {
            searchInput.value = "";
            searchInput.dispatchEvent(new Event("input"));
        }
    }

    tabs.forEach((tab) => tab.addEventListener("click", () => selectTab(tab.dataset.friendTab)));

    searchInput?.addEventListener("input", () => {
        const keyword = searchInput.value.trim().toLocaleLowerCase("ko");
        const activePanel = document.querySelector("[data-friend-panel].is-active");
        activePanel?.querySelectorAll("[data-person-card]").forEach((card) => {
            card.hidden = !card.dataset.personName.includes(keyword);
        });
    });

    document.addEventListener("click", (event) => {
        const deleteButton = event.target.closest("[data-delete-friend]");
        if (deleteButton && confirmLayer) {
            const pendingDeleteCard = deleteButton.closest("[data-person-card]");
            const name = pendingDeleteCard?.querySelector(".person-card__copy strong")?.textContent.trim();
            if (confirmMessage) confirmMessage.textContent = `${name}님을 삭제하면 더 이상 기록을 공유할 수 없어요.`;
            if (deleteForm) deleteForm.action = deleteButton.dataset.deleteUrl;
            confirmLayer.hidden = false;
            document.body.classList.add("friend-dialog-open");
        }
    });

    confirmLayer?.querySelector("[data-confirm-cancel]")?.addEventListener("click", closeConfirm);
    confirmLayer?.addEventListener("click", (event) => {
        if (event.target === confirmLayer) closeConfirm();
    });

    function closeConfirm() {
        if (confirmLayer) confirmLayer.hidden = true;
        if (deleteForm) deleteForm.removeAttribute("action");
        document.body.classList.remove("friend-dialog-open");
    }
});
