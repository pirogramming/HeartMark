(() => {
    const yearSelect = document.querySelector('[name="attendance_year"]');
    const monthSelect = document.querySelector("#attendance-month-select");
    const daySelect = document.querySelector("#attendance-day-select");
    const periodForm = document.querySelector(".attendance-calendar-filter");
    const updatePeriodSelects = () => {
        if (!yearSelect || !monthSelect || !daySelect) return;
        monthSelect.disabled = !yearSelect.value;
        daySelect.disabled = !yearSelect.value || !monthSelect.value;

        if (daySelect.disabled) {
            daySelect.value = "";
            return;
        }

        const lastDay = new Date(
            Number(yearSelect.value),
            Number(monthSelect.value),
            0,
        ).getDate();
        [...daySelect.options].forEach((option) => {
            option.hidden = Boolean(option.value) && Number(option.value) > lastDay;
        });
        if (Number(daySelect.value) > lastDay) daySelect.value = "";
    };
    yearSelect?.addEventListener("change", updatePeriodSelects);
    monthSelect?.addEventListener("change", updatePeriodSelects);
    updatePeriodSelects();

    periodForm?.addEventListener("submit", (event) => {
        if (!yearSelect?.value) {
            event.preventDefault();
            yearSelect?.focus();
        }
    });

    const editor = document.querySelector("#profile-editor");
    const openButton = document.querySelector("#open-profile-editor");
    const closeButton = editor?.querySelector(".profile-editor__close");
    if (editor && openButton) {
        const openEditor = () => {
            editor.hidden = false;
            editor.querySelector("input")?.focus();
        };
        const closeEditor = () => {
            editor.hidden = true;
            openButton.focus();
        };

        openButton.addEventListener("click", openEditor);
        closeButton?.addEventListener("click", closeEditor);
        editor.addEventListener("click", (event) => {
            if (event.target === editor) closeEditor();
        });
        document.addEventListener("keydown", (event) => {
            if (event.key === "Escape" && !editor.hidden) closeEditor();
        });
    }

    const slider = document.querySelector("#attendance-slider");
    const track = slider?.querySelector(".attendance-track");
    const pages = [...(slider?.querySelectorAll(".attendance-page") || [])];
    const previousButton = slider?.querySelector(".attendance-arrow--prev");
    const nextButton = slider?.querySelector(".attendance-arrow--next");
    const dots = [...document.querySelectorAll(".attendance-dot")];
    if (!slider || !track || !pages.length) return;

    let currentPage = Number.parseInt(slider.dataset.currentPage || "0", 10);
    let touchStartX = null;

    const showPage = (pageIndex) => {
        currentPage = Math.max(0, Math.min(pageIndex, pages.length - 1));
        track.style.transform = `translateX(-${currentPage * 100}%)`;
        pages.forEach((page, index) => {
            page.setAttribute("aria-hidden", String(index !== currentPage));
        });
        dots.forEach((dot, index) => {
            const isActive = index === currentPage;
            dot.classList.toggle("attendance-dot--active", isActive);
            dot.setAttribute("aria-selected", String(isActive));
        });
        previousButton.disabled = currentPage === 0;
        nextButton.disabled = currentPage === pages.length - 1;
    };

    previousButton?.addEventListener("click", () => showPage(currentPage - 1));
    nextButton?.addEventListener("click", () => showPage(currentPage + 1));
    dots.forEach((dot, index) => dot.addEventListener("click", () => showPage(index)));

    slider.addEventListener("touchstart", (event) => {
        touchStartX = event.changedTouches[0].clientX;
    }, { passive: true });
    slider.addEventListener("touchend", (event) => {
        if (touchStartX === null) return;
        const distance = event.changedTouches[0].clientX - touchStartX;
        if (Math.abs(distance) > 45) {
            showPage(currentPage + (distance < 0 ? 1 : -1));
        }
        touchStartX = null;
    }, { passive: true });

    showPage(currentPage);
})();
