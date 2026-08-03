document.addEventListener("DOMContentLoaded", () => {
    const form = document.querySelector(".auth-form");
    const passwordToggles = document.querySelectorAll(".password-toggle");
    const characterCards = document.querySelectorAll(".character-card");

    passwordToggles.forEach((passwordToggle) => {
        const field = passwordToggle.closest(".auth-field");
        const passwordInput = field ? field.querySelector("input") : null;

        if (!passwordInput) {
            return;
        }

        passwordToggle.addEventListener("click", () => {
            const isHidden = passwordInput.type === "password";
            const icon = passwordToggle.querySelector("img");
            passwordInput.type = isHidden ? "text" : "password";
            if (icon) {
                icon.src = isHidden ? icon.dataset.eyeOpen : icon.dataset.eyeClosed;
            }
            passwordToggle.setAttribute("aria-label", isHidden ? "비밀번호 숨기기" : "비밀번호 보기");
        });
    });

    characterCards.forEach((card) => {
        const radio = card.querySelector('input[type="radio"]');

        card.addEventListener("click", () => {
            characterCards.forEach((item) => item.classList.remove("is-selected"));
            card.classList.add("is-selected");

            if (radio) {
                radio.checked = true;
            }
        });
    });

    if (!form) {
        return;
    }

    form.addEventListener("submit", (event) => {
        let isValid = true;
        const requiredInputs = form.querySelectorAll("input[required]");

        requiredInputs.forEach((input) => {
            const field = input.closest(".auth-field");
            const message = field.querySelector(".field-message");
            const empty = input.value.trim() === "";

            field.classList.toggle("has-error", empty);
            message.textContent = empty ? "필수 입력 항목입니다." : "";
            isValid = isValid && !empty;
        });

        const password = form.querySelector('input[name="password"]');
        const passwordConfirm = form.querySelector('input[name="password_confirm"]');

        if (password && passwordConfirm && passwordConfirm.value.trim() !== "" && password.value !== passwordConfirm.value) {
            const field = passwordConfirm.closest(".auth-field");
            const message = field.querySelector(".field-message");

            field.classList.add("has-error");
            message.textContent = "비밀번호가 일치하지 않습니다.";
            isValid = false;
        }

        if (!isValid) {
            event.preventDefault();
        }
    });
});
