// 공통 담당자만 수정: 전체 페이지 공통 동작

(function () {
    var toggle = document.querySelector(".nav-toggle");
    var nav = document.getElementById("site-nav");

    if (!toggle || !nav) return;

    function closeNav() {
        nav.classList.remove("is-open");
        toggle.setAttribute("aria-expanded", "false");
    }

    toggle.addEventListener("click", function () {
        var isOpen = nav.classList.toggle("is-open");
        toggle.setAttribute("aria-expanded", isOpen ? "true" : "false");
    });

    document.addEventListener("click", function (event) {
        if (!nav.classList.contains("is-open")) return;
        if (nav.contains(event.target) || toggle.contains(event.target)) return;
        closeNav();
    });

    window.addEventListener("resize", function () {
        if (window.innerWidth > 767) closeNav();
    });
})();

