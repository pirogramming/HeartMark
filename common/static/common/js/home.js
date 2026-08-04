(function () {
    const page = document.querySelector(".home-page");
    if (!page || page.dataset.showTutorial !== "true") {
        return;
    }

    const imageBase = "/static/accounts/images/";
    const DEBUG_SHOW_ALL_IMAGES = false;
    const steps = [
        {
            target: '[data-tutorial-target="record-write"]',
            title: "기록작성",
            text: "오늘 머문 장소와 마음을 남기는 곳이에요.",
            image: "tutorial-record-write.png",
            imageWidth: 120,
            imageHeight: 46,
            imageOffsetX: 0,
            imageOffsetY: -20,
            cardOffsetY: 38,
        },
        {
            target: '[data-tutorial-target="record-list"]',
            title: "기록보기",
            text: "남겨둔 마음자국들을 한곳에서 다시 볼 수 있어요.",
            image: "tutorial-record-list.png",
            imageWidth: 120,
            imageHeight: 46,
            imageOffsetX: 0,
            imageOffsetY: -20,
            cardOffsetY: 38,
        },
        {
            target: '[data-tutorial-target="calendar"]',
            title: "달력",
            text: "날짜별로 쌓인 기록과 마음의 흐름을 확인해요.",
            image: "tutorial-calendar.png",
            imageWidth: 120,
            imageHeight: 46,
            imageOffsetX: 0,
            imageOffsetY: -20,
            cardOffsetY: 38,
        },
        {
            target: '[data-tutorial-target="mypage"]',
            title: "마이페이지",
            text: "프로필과 캐릭터 설정을 관리할 수 있어요.",
            image: "tutorial-mypage.png",
            imageWidth: 120,
            imageHeight: 46,
            imageOffsetX: 0,
            imageOffsetY: -20,
            cardOffsetY: 38,
        },
        {
            target: '[data-tutorial-target="auth"]',
            title: "로그아웃",
            text: "사용을 마친 뒤에는 여기에서 계정을 안전하게 나갈 수 있어요.",
            image: "tutorial-logout.png",
            imageWidth: 120,
            imageHeight: 46,
            imageOffsetX: 0,
            imageOffsetY: -20,
            cardOffsetY: 38,
        },
        {
            target: '[data-tutorial-target="quick-start"]',
            title: "빠른 기록",
            text: "검정 원을 누르면 기록을 빠르게 시작할 수 있게 연결돼요.",
            cardWidth: 480,
            cardOffsetX: 0,
            cardOffsetY: 60,
            cardLarge: true,
            shape: "circle",
            highlightPadding: 22,
            highlightOffsetY: -44,
            liveTarget: true,
        },
        {
            target: '[data-tutorial-target="speech-actions"]',
            title: "오늘의 질문",
            text: "로그인할 때마다 새로운 질문으로 오늘의 마음을 꺼내볼 수 있어요.",
            cardWidth: 430,
            cardPlacement: "right",
            cardOffsetX: 34,
            cardOffsetY: -8,
            cardLarge: true,
            spotlightClass: "tutorial-spotlight--speech",
        },
        {
            target: '[data-tutorial-target="selected-character"]',
            title: "나의 캐릭터",
            text: "캐릭터 선택에서 고른 친구가 메인 화면에 함께 나타나요.",
            cardWidth: 360,
            cardPlacement: "right",
            cardOffsetX: 40,
            cardOffsetY: 20,
            cardLarge: true,
            shape: "circle",
        },
    ];

    let index = 0;
    const overlay = document.createElement("div");
    const highlight = document.createElement("div");
    const spotlight = document.createElement("div");
    const card = document.createElement("button");
    let activeLiveTarget = null;
    let isFinishing = false;

    overlay.className = "tutorial-overlay";
    highlight.className = "tutorial-highlight";
    spotlight.className = "tutorial-spotlight";
    card.className = "tutorial-card";
    card.type = "button";
    card.setAttribute("aria-label", "다음 튜토리얼 보기");

    document.body.append(overlay, highlight, spotlight, card);
    document.body.style.overflow = "hidden";

    function getCookie(name) {
        return document.cookie
            .split("; ")
            .find((row) => row.startsWith(name + "="))
            ?.split("=")[1];
    }

    function clamp(value, min, max) {
        return Math.min(Math.max(value, min), max);
    }

    function resetLiveTarget() {
        if (!activeLiveTarget) {
            return;
        }

        activeLiveTarget.classList.remove("tutorial-live-target");
        activeLiveTarget = null;
    }

    function placeCard(rect, step) {
        const margin = 18;
        const cardWidth = Math.min(step.cardWidth || 360, window.innerWidth - 32);
        const estimatedHeight = 142;
        const cardOffsetX = step.cardOffsetX || 0;
        const cardOffsetY = step.cardOffsetY || 0;
        let left = rect.left + rect.width / 2 - cardWidth / 2 + cardOffsetX;
        let top = rect.bottom + 18 + cardOffsetY;

        if (step.cardPlacement === "right") {
            left = rect.right + cardOffsetX;
            top = rect.top + rect.height / 2 - estimatedHeight / 2 + cardOffsetY;

            if (left + cardWidth > window.innerWidth - margin) {
                left = rect.left + rect.width / 2 - cardWidth / 2;
                top = rect.bottom + 26 + cardOffsetY;
            }
        }

        if (top + estimatedHeight > window.innerHeight - margin) {
            top = rect.top - estimatedHeight - 18 + cardOffsetY;
        }

        if (top < margin) {
            top = margin;
        }

        card.style.left = clamp(left, margin, window.innerWidth - cardWidth - margin) + "px";
        card.style.top = top + "px";
    }

    function renderSpotlight(step, target, rect) {
        spotlight.innerHTML = "";

        if (step.liveTarget) {
            return;
        }

        if (step.image) {
            const image = document.createElement("img");
            image.className = "tutorial-spotlight-image";
            image.src = imageBase + step.image;
            image.alt = step.title;
            spotlight.appendChild(image);
            return;
        }

        const clone = target.cloneNode(true);
        clone.removeAttribute("id");
        clone.removeAttribute("href");
        clone.removeAttribute("data-tutorial-target");
        clone.style.margin = "0";
        clone.style.transform = "none";
        clone.style.pointerEvents = "none";
        clone.style.width = rect.width + "px";
        clone.style.height = rect.height + "px";
        if (step.spotlightClass) {
            clone.classList.add(step.spotlightClass);
        }
        spotlight.appendChild(clone);
    }

    function getImagePlacement(step, rect) {
        const imageWidth = step.imageWidth || 120;
        const imageHeight = step.imageHeight || 46;
        const imageOffsetX = step.imageOffsetX || 0;
        const imageOffsetY = step.imageOffsetY || 0;

        return {
            left: rect.left + rect.width / 2 - imageWidth / 2 + imageOffsetX,
            top: rect.top + imageOffsetY,
            width: imageWidth,
            height: imageHeight,
        };
    }

    function showAllImageGuides() {
        overlay.classList.add("is-active");
        highlight.remove();
        spotlight.remove();
        card.remove();

        steps
            .filter((step) => step.image)
            .forEach((step) => {
                const target = document.querySelector(step.target);
                if (!target) {
                    return;
                }

                const rect = target.getBoundingClientRect();
                const placement = getImagePlacement(step, rect);
                const guide = document.createElement("div");
                const image = document.createElement("img");

                guide.className = "tutorial-spotlight tutorial-debug-guide has-image";
                guide.style.left = placement.left + "px";
                guide.style.top = placement.top + "px";
                guide.style.width = placement.width + "px";
                guide.style.height = placement.height + "px";

                image.className = "tutorial-spotlight-image";
                image.src = imageBase + step.image;
                image.alt = step.title;
                guide.appendChild(image);
                document.body.appendChild(guide);
            });
    }

    function showStep() {
        resetLiveTarget();
        const step = steps[index];
        const target = document.querySelector(step.target);

        if (!target) {
            nextStep();
            return;
        }

        target.scrollIntoView({ behavior: "smooth", block: "center", inline: "center" });

        window.setTimeout(() => {
            const rect = target.getBoundingClientRect();
            const padding = step.highlightPadding || (step.shape === "circle" ? 12 : 10);

            if (step.liveTarget) {
                activeLiveTarget = target;
                target.classList.add("tutorial-live-target");
            }

            highlight.classList.toggle("is-circle", step.shape === "circle");
            highlight.classList.toggle("is-hidden", Boolean(step.image));
            highlight.style.left = rect.left - padding + "px";
            highlight.style.top = rect.top - padding + (step.highlightOffsetY || 0) + "px";
            highlight.style.width = rect.width + padding * 2 + "px";
            highlight.style.height = rect.height + padding * 2 + "px";

            if (step.image) {
                const placement = getImagePlacement(step, rect);
                spotlight.style.left = placement.left + "px";
                spotlight.style.top = placement.top + "px";
                spotlight.style.width = placement.width + "px";
                spotlight.style.height = placement.height + "px";
            } else {
                spotlight.style.left = rect.left + "px";
                spotlight.style.top = rect.top + "px";
                spotlight.style.width = rect.width + "px";
                spotlight.style.height = rect.height + "px";
            }

            spotlight.classList.toggle("has-image", Boolean(step.image));
            spotlight.classList.toggle("is-circle-image", step.imageShape === "circle");
            spotlight.classList.toggle("no-image-border", step.imageBorder === false);
            spotlight.classList.toggle("is-speech", step.spotlightClass === "tutorial-spotlight--speech");
            spotlight.classList.toggle("is-hidden", Boolean(step.liveTarget));
            renderSpotlight(step, target, rect);

            card.innerHTML = `
                <strong>${step.title}</strong>
                <p>${step.text}</p>
                <span>${index + 1} / ${steps.length} · 클릭해서 계속</span>
            `;
            card.classList.toggle("is-large", Boolean(step.cardLarge));
            card.style.setProperty("--tutorial-card-width", (step.cardWidth || 360) + "px");
            placeCard(rect, step);
            overlay.classList.add("is-active");
        }, 260);
    }

    function finishTutorial() {
        if (isFinishing) {
            return;
        }

        isFinishing = true;
        resetLiveTarget();
        highlight.remove();
        spotlight.remove();
        card.remove();

        const finale = document.createElement("div");
        finale.className = "tutorial-finale";
        finale.innerHTML = `
            <strong>이제 기록을 시작해보아요</strong>
            <p>오늘의 마음이 머문 순간을 천천히 남겨봐요.</p>
        `;
        document.body.appendChild(finale);
        window.setTimeout(() => finale.classList.add("is-active"), 20);
        window.setTimeout(() => {
            document.body.style.overflow = "";
            const hero = document.querySelector(".home-hero");
            if (hero) {
                hero.scrollIntoView({ behavior: "smooth", block: "start" });
            } else {
                window.scrollTo({ top: 0, behavior: "smooth" });
            }
        }, 3000);

        fetch(page.dataset.tutorialCompleteUrl, {
            method: "POST",
            headers: {
                "X-CSRFToken": decodeURIComponent(getCookie("csrftoken") || ""),
                "X-Requested-With": "XMLHttpRequest",
            },
        }).catch(() => {});

        window.setTimeout(() => {
            overlay.remove();
            finale.remove();
            document.body.style.overflow = "";
        }, 3900);
    }

    function nextStep() {
        if (isFinishing) {
            return;
        }

        index += 1;
        if (index >= steps.length) {
            finishTutorial();
            return;
        }
        showStep();
    }

    overlay.addEventListener("click", nextStep);
    card.addEventListener("click", nextStep);
    window.addEventListener("resize", showStep);

    if (DEBUG_SHOW_ALL_IMAGES) {
        showAllImageGuides();
        return;
    }

    showStep();
})();
