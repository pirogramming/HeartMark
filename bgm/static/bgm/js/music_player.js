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


    // ========================================================
    // 2. 필수 요소 확인
    // ========================================================

    // Listen 버튼이 없는 페이지에서는
    // BGM 기능 실행하지 않음.
    if (!toggleButton) {
        return;
    }


    // 동일 버튼에 이벤트가
    // 여러 번 등록되는 현상 방지함.
    if (
        toggleButton.dataset.bgmInitialized
        === "true"
    ) {
        return;
    }


    // audio 요소가 없으면
    // BGM 기능 실행하지 않음.
    if (!audio) {
        console.error(
            "BGM audio 요소를 찾을 수 없음.",
        );

        toggleButton.disabled = true;

        return;
    }


    // 등록된 음원이 하나도 없으면
    // Listen 버튼 비활성화함.
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


    // 정상적으로 초기화된 버튼임을 저장함.
    toggleButton.dataset.bgmInitialized = "true";


    // 음원이 존재하므로
    // Listen 버튼 활성화함.
    toggleButton.disabled = false;


    // 직전에 재생한 음악 위치 저장함.
    //
    // 처음에는 재생한 음악이 없으므로 -1 사용함.
    let previousMusicIndex = -1;


    // ========================================================
    // 3. Listen 버튼 상태 변경
    // ========================================================

    function updateButtonState(isPlaying) {

        // 재생 중이면
        // 일반 헤드셋 아이콘 표시함.
        if (iconOn) {
            iconOn.hidden = !isPlaying;
        }


        // 정지 상태이면
        // 사선 헤드셋 아이콘 표시함.
        if (iconOff) {
            iconOff.hidden = isPlaying;
        }


        // 재생 상태 전용 CSS 적용함.
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
    // 4. 오류 문구 숨김
    // ========================================================

    function hideErrorMessage() {

        if (!errorMessage) {
            return;
        }

        errorMessage.hidden = true;
    }


    // ========================================================
    // 5. 오류 문구 표시
    // ========================================================

    function showErrorMessage() {

        if (!errorMessage) {
            return;
        }

        errorMessage.hidden = false;
    }


    // ========================================================
    // 6. 랜덤 음악 선택
    // ========================================================

    function getRandomMusicIndex() {

        // 음악이 한 곡뿐이면
        // 무조건 첫 번째 곡 사용함.
        if (musicItems.length === 1) {
            return 0;
        }


        let randomIndex;


        // 직전에 재생한 음악과
        // 다른 곡이 나올 때까지 다시 선택함.
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
    // 7. 랜덤 BGM 재생
    // ========================================================

    async function playRandomMusic() {

        // 랜덤 음악 위치 선택함.
        const randomIndex = (
            getRandomMusicIndex()
        );


        // 선택된 음악 데이터 가져옴.
        const selectedMusic = (
            musicItems[randomIndex]
        );


        // data-src에 저장된
        // 실제 static 음원 주소 가져옴.
        const musicSrc = (
            selectedMusic.dataset.src
        );


        // 음원 경로가 없다면
        // 재생하지 않음.
        if (!musicSrc) {

            console.error(
                "선택된 BGM의 파일 경로가 없음.",
            );

            showErrorMessage();

            updateButtonState(false);

            return;
        }


        // 현재 선택된 음악 위치 저장함.
        previousMusicIndex = randomIndex;


        // 이전 음악이 재생 중이라면 정지함.
        audio.pause();


        // 새로운 음원 파일 지정함.
        audio.src = musicSrc;


        // 브라우저가 새로운 파일을
        // 다시 읽도록 함.
        audio.load();


        // 처음부터 재생하도록 위치 초기화함.
        audio.currentTime = 0;


        // 이전 오류 문구 숨김.
        hideErrorMessage();


        try {

            // 사용자가 Listen 버튼을 직접 눌렀기 때문에
            // 일반적인 브라우저 자동재생 정책에 걸리지 않음.
            await audio.play();


            // 재생 상태 UI 적용함.
            updateButtonState(true);


        } catch (error) {

            console.error(
                "BGM 재생 실패:",
                error,
            );


            // 재생 실패 시 정지 상태로 복구함.
            updateButtonState(false);


            // 오류 안내 표시함.
            showErrorMessage();
        }
    }


    // ========================================================
    // 8. Listen 버튼 클릭
    // ========================================================

    toggleButton.addEventListener(
        "click",
        async () => {

            // ==================================================
            // 현재 음악이 재생 중인 경우
            // ==================================================

            if (!audio.paused) {

                // 음악 정지함.
                audio.pause();


                // 다음 재생 시 처음부터 시작하도록 초기화함.
                audio.currentTime = 0;


                // 정지 상태 아이콘으로 변경함.
                updateButtonState(false);

                return;
            }


            // ==================================================
            // 현재 음악이 정지된 경우
            // ==================================================

            // 새로운 랜덤 음악을 선택하여 재생함.
            await playRandomMusic();
        },
    );


    // ========================================================
    // 9. 음악이 끝난 경우
    // ========================================================

    audio.addEventListener(
        "ended",
        () => {

            // 재생 위치 처음으로 돌림.
            audio.currentTime = 0;


            // 정지 상태 아이콘 표시함.
            updateButtonState(false);
        },
    );


    // ========================================================
    // 10. 음원 파일 로딩 실패
    // ========================================================

    audio.addEventListener(
        "error",
        () => {

            // 정지 상태로 변경함.
            updateButtonState(false);


            // 오류 문구 표시함.
            showErrorMessage();


            console.error(
                "BGM 음원 파일을 불러오지 못함.",
                audio.error,
                audio.currentSrc,
            );
        },
    );


    // ========================================================
    // 11. 페이지를 떠날 때 음악 종료
    // ========================================================

    window.addEventListener(
        "pagehide",
        () => {

            // 음악 정지함.
            audio.pause();


            // 재생 위치 초기화함.
            audio.currentTime = 0;
        },
    );


    // ========================================================
    // 12. 초기 상태
    // ========================================================

    hideErrorMessage();

    updateButtonState(false);
}


// ============================================================
// 페이지 로드 상태에 맞춰 초기화
// ============================================================
//
// HTML 생성 전:
// DOMContentLoaded 이후 실행함.
//
// HTML 생성 후:
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