document.addEventListener("DOMContentLoaded", () => {
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


    // Listen 버튼이 없으면 실행 중단함.
    if (!toggleButton) {
        return;
    }


    // 등록된 음원이 없으면 버튼 비활성화함.
    if (!audio || musicItems.length === 0) {
        toggleButton.disabled = true;

        toggleButton.setAttribute(
            "aria-label",
            "재생 가능한 BGM 없음",
        );

        return;
    }


    // 직전에 선택된 음악 위치 저장함.
    let previousMusicIndex = -1;


    // ========================================================
    // 2. 아이콘 상태 변경
    // ========================================================

    function updateButtonState(isPlaying) {
        if (iconOn) {
            iconOn.hidden = !isPlaying;
        }

        if (iconOff) {
            iconOff.hidden = isPlaying;
        }

        toggleButton.classList.toggle(
            "is-playing",
            isPlaying,
        );

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
    // 3. 랜덤 음악 위치 선택
    // ========================================================

    function getRandomMusicIndex() {
        // 음악이 한 곡뿐이면 첫 번째 곡 사용함.
        if (musicItems.length === 1) {
            return 0;
        }

        let randomIndex;

        // 직전 음악과 다른 곡이 나올 때까지 다시 선택함.
        do {
            randomIndex = Math.floor(
                Math.random() * musicItems.length,
            );
        } while (
            randomIndex === previousMusicIndex
        );

        return randomIndex;
    }


    // ========================================================
    // 4. 랜덤 음악 선택 후 재생
    // ========================================================

    async function playRandomMusic() {
        // 랜덤 음악 위치 선택함.
        const randomIndex = getRandomMusicIndex();

        const selectedMusic = musicItems[
            randomIndex
        ];

        const musicSrc = selectedMusic.dataset.src;

        // 음원 경로가 없으면 실행 중단함.
        if (!musicSrc) {
            return;
        }

        // 직전 음악 위치 갱신함.
        previousMusicIndex = randomIndex;

        // 이전 음악 정지함.
        audio.pause();

        // 새로운 음원 지정함.
        audio.src = musicSrc;

        // 새로운 음악 처음부터 시작함.
        audio.currentTime = 0;

        // 오류 문구 숨김.
        if (errorMessage) {
            errorMessage.hidden = true;
        }

        try {
            // 음악 재생함.
            await audio.play();

            // 재생 상태 표시함.
            updateButtonState(true);

        } catch (error) {
            console.error(
                "BGM 재생 중 오류 발생:",
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
            // 현재 음악이 재생 중이면 정지함.
            if (!audio.paused) {
                audio.pause();

                // 다시 누르면 새로운 곡을 선택하도록
                // 현재 위치를 처음으로 초기화함.
                audio.currentTime = 0;

                updateButtonState(false);

                return;
            }

            // 멈춰 있는 상태에서 클릭하면
            // 새로운 랜덤 음악 선택 후 재생함.
            await playRandomMusic();
        },
    );


    // ========================================================
    // 6. 음악이 끝난 경우 상태 초기화
    // ========================================================

    audio.addEventListener(
        "ended",
        () => {
            audio.currentTime = 0;

            updateButtonState(false);
        },
    );


    // ========================================================
    // 7. 음원 오류 처리
    // ========================================================

    audio.addEventListener(
        "error",
        () => {
            updateButtonState(false);

            if (errorMessage) {
                errorMessage.hidden = false;
            }

            console.error(
                "BGM 음원 파일을 불러오지 못했습니다.",
                audio.error,
            );
        },
    );


    // ========================================================
    // 8. 페이지 이동 시 음악 종료
    // ========================================================

    window.addEventListener(
        "pagehide",
        () => {
            audio.pause();
            audio.currentTime = 0;
        },
    );


    // ========================================================
    // 9. 초기 상태
    // ========================================================

    updateButtonState(false);
});