document.addEventListener("DOMContentLoaded", () => {
    // BGM 재생을 담당하는 audio 요소 가져옴.
    const audio = document.querySelector("#bgm-audio");

    // 재생·일시정지 버튼 가져옴.
    const playButton = document.querySelector("#bgm-play-button");

    // 현재 기록에 연결된 음악이 없으면 실행 중단함.
    if (!audio || !playButton) {
        return;
    }


    // ========================================================
    // 1. 재생 / 일시정지
    // ========================================================

    playButton.addEventListener("click", async () => {
        // 현재 음악이 멈춰 있다면 재생함.
        if (audio.paused) {
            try {
                await audio.play();
            } catch (error) {
                console.error(
                    "BGM 재생 중 오류가 발생했습니다.",
                    error,
                );
            }

            return;
        }

        // 이미 음악이 재생 중이라면 일시정지함.
        audio.pause();
    });


    // ========================================================
    // 2. 재생 상태에 따라 버튼 문구 변경
    // ========================================================

    audio.addEventListener("play", () => {
        playButton.textContent = "일시정지";
    });

    audio.addEventListener("pause", () => {
        playButton.textContent = "재생";
    });


    // ========================================================
    // 3. 음악이 끝나면 처음 상태로 되돌림
    // ========================================================

    audio.addEventListener("ended", () => {
        // 재생 위치 처음으로 이동함.
        audio.currentTime = 0;

        // 버튼 문구 초기화함.
        playButton.textContent = "재생";
    });


    // ========================================================
    // 4. 음원 로딩 실패 처리
    // ========================================================

    audio.addEventListener("error", () => {
        // 오류 발생 시 재생 버튼 비활성화함.
        playButton.disabled = true;

        // 사용자에게 음원 오류 안내함.
        playButton.textContent = "음악을 불러올 수 없습니다.";

        console.error(
            "BGM 음원 파일을 불러오지 못했습니다.",
            audio.error,
        );
    });
});