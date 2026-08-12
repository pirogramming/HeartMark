document.addEventListener("DOMContentLoaded", () => {
    const copyButton = document.querySelector("[data-copy-invite]");
    const inviteInput = document.querySelector("#invite-url");
    const status = document.querySelector("[data-copy-status]");

    if (!copyButton || !inviteInput) return;

    copyButton.addEventListener("click", async () => {
        const originalLabel = copyButton.dataset.copyLabel || "링크 복사";
        try {
            await navigator.clipboard.writeText(inviteInput.value);
        } catch (error) {
            inviteInput.select();
            document.execCommand("copy");
        }

        copyButton.textContent = "복사 완료 ✓";
        if (status) status.textContent = "초대 링크를 복사했어요.";

        window.setTimeout(() => {
            copyButton.textContent = originalLabel;
            if (status) status.textContent = "";
        }, 1800);
    });
});
