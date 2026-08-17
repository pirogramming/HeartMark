document.addEventListener("DOMContentLoaded", () => {
    const modal = document.querySelector("#share-letter-modal");
    if (!modal) return;
    const panel = modal.querySelector(".share-letter");
    const form = modal.querySelector("[data-share-form]");
    const formView = modal.querySelector("[data-share-form-view]");
    const successView = modal.querySelector("[data-share-success]");
    const rows = [...modal.querySelectorAll("[data-share-friend]")];
    const boxes = rows.map((row) => row.querySelector("input[type=checkbox]"));
    const search = modal.querySelector("#share-friend-search");
    const empty = modal.querySelector("[data-share-search-empty]");
    const chipBox = modal.querySelector("[data-selected-chips]");
    const footerCount = modal.querySelector("[data-footer-count]");
    const send = modal.querySelector("[data-send-share]");
    const recordRows = [...modal.querySelectorAll("[data-share-record]")];
    const recordBoxes = recordRows.map((row) => row.querySelector("input[type=checkbox]"));
    const recordCount = modal.querySelector("[data-record-count]");
    const location = modal.querySelector("#share-location");
    let lastFocus;

    const selected = () => rows.filter((row) => row.querySelector("input").checked);
    function update() {
        const chosen = selected();
        rows.forEach((row) => row.classList.toggle("is-selected", row.querySelector("input").checked));
        const records = recordBoxes.filter((box) => box.checked);
        recordRows.forEach((row) => row.classList.toggle("is-selected", row.querySelector("input").checked));
        if (recordCount) recordCount.textContent = `${records.length}개 선택`;
        if (footerCount) footerCount.textContent = `${chosen.length}명`;
        if (send) { send.disabled = chosen.length === 0 || records.length === 0; send.textContent = chosen.length && records.length ? "마음 편지 보내기" : "기록과 친구를 선택해 주세요"; }
        if (!chipBox) return;
        chipBox.replaceChildren();
        if (!chosen.length) { const p = document.createElement("p"); p.textContent = "친구를 선택하면 여기에 표시돼요."; chipBox.append(p); return; }
        chosen.forEach((row) => { const input = row.querySelector("input"), chip = document.createElement("button"); chip.type = "button"; chip.className = "share-selected__chip"; chip.dataset.removeFriend = input.value; chip.textContent = row.querySelector("strong").textContent.trim() + " ×"; chipBox.append(chip); });
    }
    function reset() { boxes.forEach((box) => box.checked = false); recordBoxes.forEach((box, index) => box.checked = index === 0); if (location) location.checked = false; if (search) search.value = ""; rows.forEach((row) => row.hidden = false); if (empty) empty.hidden = true; if (formView) formView.hidden = false; if (successView) successView.hidden = true; update(); }
    function open(preselect) { lastFocus = document.activeElement; reset(); const box = boxes.find((item) => item.value === preselect); if (box) box.checked = true; update(); modal.hidden = false; document.body.classList.add("share-modal-open"); requestAnimationFrame(() => panel?.classList.add("is-visible")); modal.querySelector("[data-close-share-modal]")?.focus(); }
    function close() { panel?.classList.remove("is-visible"); setTimeout(() => { modal.hidden = true; document.body.classList.remove("share-modal-open"); lastFocus?.focus(); }, 180); }
    document.querySelectorAll("[data-open-share-modal]").forEach((button) => button.addEventListener("click", () => open(button.dataset.preselectFriend || "")));
    modal.querySelectorAll("[data-close-share-modal]").forEach((button) => button.addEventListener("click", close));
    modal.addEventListener("click", (event) => { if (event.target === modal) close(); const chip = event.target.closest("[data-remove-friend]"); if (chip) { const box = boxes.find((item) => item.value === chip.dataset.removeFriend); if (box) box.checked = false; update(); } });
    boxes.forEach((box) => box.addEventListener("change", update));
    recordBoxes.forEach((box) => box.addEventListener("change", update));
    search?.addEventListener("input", () => { const key = search.value.trim().toLocaleLowerCase("ko"); let count = 0; rows.forEach((row) => { const visible = row.dataset.friendName.includes(key); row.hidden = !visible; if (visible) count += 1; }); if (empty) empty.hidden = count !== 0; });
    form?.addEventListener("submit", (event) => { const first = recordBoxes.find((box) => box.checked); const url = first?.dataset.shareUrl; if (!selected().length || !first || !url) { event.preventDefault(); return; } form.action = url; send.disabled = true; send.textContent = "보내는 중..."; });
    document.addEventListener("keydown", (event) => { if (event.key === "Escape" && !modal.hidden) close(); });
});
