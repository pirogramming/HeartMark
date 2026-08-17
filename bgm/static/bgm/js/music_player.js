// ============================================================
// 랜덤 BGM 재생
// ============================================================

function initializeBgmPlayer() {
    // ========================================================
    // 1. 필요한 요소 가져옴.
    // ========================================================

    const toggleButton = document.querySelector(
        "#bgm-toggle-button",
    );

    const audio = document.querySelector(
        "#bgm-audio",
    );

    const musicItems = Array.from(
        document.querySelectorAll(
            ".bgm-music-data",
        ),
    );

    const iconOff = document.querySelector(
        "#bgm-icon-off",
    );

    const iconOn = document.querySelector(
        "#bgm-icon-on",
    );

    const errorMessage = document.querySelector(
        "#bgm-error",
    );


    // Listen 버튼이 없는 페이지에서는 실행하지 않음.
    if (!toggleButton) {
        return;
    }


    // 같은 버튼에 이벤트가 중복 등록되는 현상 방지함.
    if (
        toggleButton.dataset.bgmInitialized
        === "true"
    ) {
        return;
    }


    // audio 요소가 없으면 실행 중단함.
    if (!audio) {
        console.error(
            "BGM audio 요소를 찾을 수 없음.",
        );

        return;
    }


    // 등록된 BGM 데이터가 없으면 버튼 비활성화함.
    if (musicItems.length === 0) {
        toggleButton.disabled = true;

        toggleButton.setAttribute(
            "aria-label",
            "재생 가능한 BGM 없음",
        );

        console.error(
            "재생 가능한 BGM 데이터가 없음.",
        );

        return;
    }


    // 정상적으로 초기화됨을 저장함.
    toggleButton.dataset.bgmInitialized = "true";

    // BGM이 존재하므로 버튼 활성화함.
    toggleButton.disabled = false;


    // 직전에 재생한 음악 위치 저장함.
    let previousMusicIndex = -1;


    // ========================================================
    // 2. Listen 버튼 상태 변경
    // ========================================================

    function updateButtonState(isPlaying) {
        // 재생 중 아이콘 표시 여부 변경함.
        if (iconOn) {
            iconOn.hidden = !isPlaying;
        }

        // 정지 상태 아이콘 표시 여부 변경함.
        if (iconOff) {
            iconOff.hidden = isPlaying;
        }

        // 재생 중 스타일 적용함.
        toggleButton.classList.toggle(
            "is-playing",
            isPlaying,
        );

        // 접근성 상태 변경함.
        toggleButton.setAttribute(
            "aria-pressed",
            String(isPlaying),
        );

        toggleButton.setAttribute(
            "aria-label",
            isPlaying
                ? "BGM 정지"
                : "BGM 재생",
        );
    }


    // ========================================================
    // 3. 랜덤 음악 선택
    // ========================================================

    function getRandomMusicIndex() {
        // 음악이 한 곡뿐이면 첫 번째 곡 반환함.
        if (musicItems.length === 1) {
            return 0;
        }

        let randomIndex;


        // 직전에 나온 곡과 다른 곡 선택함.
        do {
            randomIndex = Math.floor(
                Math.random()
                * musicItems.length,
            );

        } while (
            randomIndex
            === previousMusicIndex
        );


        return randomIndex;
    }


    // ========================================================
    // 4. 랜덤 BGM 재생
    // ========================================================

    async function playRandomMusic() {
        // 랜덤 음악 위치 선택함.
        const randomIndex = getRandomMusicIndex();

        // 선택된 음악 데이터 가져옴.
        const selectedMusic = musicItems[
            randomIndex
        ];

        // HTML의 data-src 값 가져옴.
        const musicSrc = selectedMusic.dataset.src;


        // 음원 주소가 없으면 재생하지 않음.
        if (!musicSrc) {
            console.error(
                "선택된 BGM의 파일 경로가 없음.",
            );

            return;
        }


        // 직전 음악 위치 저장함.
        previousMusicIndex = randomIndex;


        // 기존 음악 정지함.
        audio.pause();


        // 새로운 음원 주소 설정함.
        audio.src = musicSrc;


        // 새 음원 로드함.
        audio.load();


        // 처음부터 재생함.
        audio.currentTime = 0;


        // 이전 오류 문구 숨김.
        if (errorMessage) {
            errorMessage.hidden = true;
        }


        try {
            // 음악 재생함.
            await audio.play();

            // 재생 중 상태로 변경함.
            updateButtonState(true);

        } catch (error) {
            console.error(
                "BGM 재생 실패:",
                error,
            );

            updateButtonState(false);

            if (errorMessage) {
                errorMessage.hidden = false;
            }
        }
    }


    // ========================================================
    // 5. Listen 버튼 클릭
    // ========================================================

    toggleButton.addEventListener(
        "click",
        async () => {
            // 현재 BGM 재생 중인 경우 정지함.
            if (!audio.paused) {
                audio.pause();

                // 다음 클릭 시 새로운 랜덤 곡을
                // 처음부터 재생하기 위해 초기화함.
                audio.currentTime = 0;

                updateButtonState(false);

                return;
            }


            // 정지 상태에서 클릭하면
            // 새로운 랜덤 BGM 재생함.
            await playRandomMusic();
        },
    );


    // ========================================================
    // 6. 음악이 끝난 경우
    // ========================================================

    audio.addEventListener(
        "ended",
        () => {
            // 재생 위치 초기화함.
            audio.currentTime = 0;

            // 정지 아이콘으로 변경함.
            updateButtonState(false);
        },
    );


    // ========================================================
    // 7. 음원 로딩 실패
    // ========================================================

    audio.addEventListener(
        "error",
        () => {
            updateButtonState(false);

            if (errorMessage) {
                errorMessage.hidden = false;
            }

            console.error(
                "BGM 음원 파일을 불러오지 못함.",
                audio.error,
            );
        },
    );


    // ========================================================
    // 8. 페이지를 떠날 때 음악 종료
    // ========================================================

    window.addEventListener(
        "pagehide",
        () => {
            audio.pause();

            audio.currentTime = 0;
        },
    );


    // ========================================================
    // 9. 초기 버튼 상태
    // ========================================================

    updateButtonState(false);
}


// ============================================================
// 페이지 로드 상태에 맞춰 초기화
// ============================================================
//
// DOM 생성 전:
// DOMContentLoaded 이후 실행함.
//
// DOM 생성 후:
// 바로 실행함.
// ============================================================

if (document.readyState === "loading") {
    document.addEventListener(
        "DOMContentLoaded",
        initializeBgmPlayer,
    );

} else {
    initializeBgmPlayer();
}