document.addEventListener("DOMContentLoaded", () => {
    // ========================================================
    // 1. 플레이어 요소 가져옴.
    // ========================================================

    const audio = document.querySelector("#bgm-audio");

    const playButton = document.querySelector(
        "#bgm-play-button",
    );

    const restartButton = document.querySelector(
        "#bgm-restart-button",
    );

    const muteButton = document.querySelector(
        "#bgm-mute-button",
    );

    const volumeSlider = document.querySelector(
        "#bgm-volume",
    );

    const progressBar = document.querySelector(
        "#bgm-progress",
    );

    const currentTimeText = document.querySelector(
        "#bgm-current-time",
    );

    const durationText = document.querySelector(
        "#bgm-duration",
    );

    const errorMessage = document.querySelector(
        "#bgm-error",
    );


    // 음악이 없는 기록에서는 플레이어 로직 실행하지 않음.
    if (!audio) {
        return;
    }


    // ========================================================
    // 2. 시간 표시 함수
    // ========================================================

    function formatTime(seconds) {
        // 음원 정보를 아직 불러오지 못한 경우 0:00 반환함.
        if (!Number.isFinite(seconds)) {
            return "0:00";
        }

        const minutes = Math.floor(
            seconds / 60,
        );

        const remainingSeconds = Math.floor(
            seconds % 60,
        );

        return (
            `${minutes}:`
            + `${remainingSeconds}`.padStart(
                2,
                "0",
            )
        );
    }


    // ========================================================
    // 3. 재생 버튼 상태 변경 함수
    // ========================================================

    function updatePlayButton() {
        if (!playButton) {
            return;
        }

        // 음악이 멈춘 상태
        if (audio.paused) {
            playButton.textContent = "▶";
            playButton.setAttribute(
                "aria-label",
                "음악 재생",
            );

            return;
        }

        // 음악이 재생 중인 상태
        playButton.textContent = "❚❚";
        playButton.setAttribute(
            "aria-label",
            "음악 일시정지",
        );
    }


    // ========================================================
    // 4. 음소거 버튼 상태 변경 함수
    // ========================================================

    function updateMuteButton() {
        if (!muteButton) {
            return;
        }

        // 음소거 상태이거나 음량이 0인 경우
        if (audio.muted || audio.volume === 0) {
            muteButton.textContent = "🔇";

            muteButton.setAttribute(
                "aria-label",
                "음소거 해제",
            );

            return;
        }

        muteButton.textContent = "🔊";

        muteButton.setAttribute(
            "aria-label",
            "음소거",
        );
    }


    // ========================================================
    // 5. 초기 음량 설정
    // ========================================================

    if (volumeSlider) {
        audio.volume = Number(
            volumeSlider.value,
        );
    }


    // ========================================================
    // 6. 재생 / 일시정지
    // ========================================================

    if (playButton) {
        playButton.addEventListener(
            "click",
            async () => {
                if (audio.paused) {
                    try {
                        await audio.play();
                    } catch (error) {
                        console.error(
                            "BGM 재생 중 오류 발생:",
                            error,
                        );

                        if (errorMessage) {
                            errorMessage.hidden = false;
                        }
                    }

                    return;
                }

                audio.pause();
            },
        );
    }


    // ========================================================
    // 7. 처음부터 다시 듣기
    // ========================================================

    if (restartButton) {
        restartButton.addEventListener(
            "click",
            async () => {
                // 재생 위치를 처음으로 이동함.
                audio.currentTime = 0;

                try {
                    // 처음으로 이동한 뒤 바로 재생함.
                    await audio.play();
                } catch (error) {
                    console.error(
                        "BGM 다시 듣기 중 오류 발생:",
                        error,
                    );
                }
            },
        );
    }


    // ========================================================
    // 8. 음량 조절
    // ========================================================

    if (volumeSlider) {
        volumeSlider.addEventListener(
            "input",
            () => {
                const volume = Number(
                    volumeSlider.value,
                );

                audio.volume = volume;

                // 음량을 직접 올리면 음소거 해제함.
                if (volume > 0) {
                    audio.muted = false;
                }

                updateMuteButton();
            },
        );
    }


    // ========================================================
    // 9. 음소거 / 음소거 해제
    // ========================================================

    if (muteButton) {
        muteButton.addEventListener(
            "click",
            () => {
                audio.muted = !audio.muted;

                updateMuteButton();
            },
        );
    }


    // ========================================================
    // 10. 음원 전체 길이 표시
    // ========================================================

    audio.addEventListener(
        "loadedmetadata",
        () => {
            if (durationText) {
                durationText.textContent = formatTime(
                    audio.duration,
                );
            }

            if (progressBar) {
                progressBar.max = audio.duration;
            }
        },
    );


    // ========================================================
    // 11. 재생 중 진행바와 현재 시간 갱신
    // ========================================================

    audio.addEventListener(
        "timeupdate",
        () => {
            if (currentTimeText) {
                currentTimeText.textContent = formatTime(
                    audio.currentTime,
                );
            }

            if (progressBar) {
                progressBar.value = audio.currentTime;
            }
        },
    );


    // ========================================================
    // 12. 진행바 직접 이동
    // ========================================================

    if (progressBar) {
        progressBar.addEventListener(
            "input",
            () => {
                audio.currentTime = Number(
                    progressBar.value,
                );
            },
        );
    }


    // ========================================================
    // 13. 재생 상태에 맞춰 버튼 변경
    // ========================================================

    audio.addEventListener(
        "play",
        updatePlayButton,
    );

    audio.addEventListener(
        "pause",
        updatePlayButton,
    );


    // ========================================================
    // 14. 음악이 끝났을 때 초기화
    // ========================================================

    audio.addEventListener(
        "ended",
        () => {
            audio.currentTime = 0;

            if (progressBar) {
                progressBar.value = 0;
            }

            if (currentTimeText) {
                currentTimeText.textContent = "0:00";
            }

            updatePlayButton();
        },
    );


    // ========================================================
    // 15. 음원 로딩 실패 처리
    // ========================================================

    audio.addEventListener(
        "error",
        () => {
            audio.pause();

            if (errorMessage) {
                errorMessage.hidden = false;
            }

            if (playButton) {
                playButton.disabled = true;
            }

            if (restartButton) {
                restartButton.disabled = true;
            }

            console.error(
                "BGM 음원 파일을 불러오지 못했습니다.",
                audio.error,
            );
        },
    );


    // ========================================================
    // 16. Listen 모달이 닫히면 음악 일시정지
    // ========================================================

    const listenModal = document.querySelector(
        "#listen-modal",
    );

    if (listenModal) {
        const listenCloseButtons = listenModal.querySelectorAll(
            "[data-modal-close]",
        );

        listenCloseButtons.forEach(
            (button) => {
                button.addEventListener(
                    "click",
                    () => {
                        audio.pause();
                    },
                );
            },
        );
    }


    // ========================================================
    // 17. Photo / Read로 이동하면 음악 일시정지
    // ========================================================

    const otherModalButtons = document.querySelectorAll(
        '[data-modal-open="photo-modal"], '
        + '[data-modal-open="read-modal"]',
    );

    otherModalButtons.forEach(
        (button) => {
            button.addEventListener(
                "click",
                () => {
                    audio.pause();
                },
            );
        },
    );


    // ========================================================
    // 18. 페이지를 떠날 때 음악 종료 및 초기화
    // ========================================================

    window.addEventListener(
        "pagehide",
        () => {
            audio.pause();
            audio.currentTime = 0;
        },
    );


    // ========================================================
    // 19. 초기 버튼 상태 설정
    // ========================================================

    updatePlayButton();
    updateMuteButton();
});