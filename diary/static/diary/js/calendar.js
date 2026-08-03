// ============================================================
// 감정 캘린더
// ============================================================
//
// diary/views.py의 emotion_calendar view에서 전달한
// 날짜별 대표 감정 데이터를 이용해 캘린더를 생성합니다.
//
// 같은 날짜에 기록이 여러 개 있다면
// views.py에서 가장 최근 기록의 대표 감정을 전달합니다.
//

document.addEventListener("DOMContentLoaded", () => {
    // 날짜 칸들이 들어갈 요소입니다.
    const calendarGrid = document.querySelector(
        "#emotion-calendar-grid"
    );

    // 현재 연도와 월을 표시하는 제목입니다.
    const calendarTitle = document.querySelector(
        "#calendar-title"
    );

    // 이전 달 버튼입니다.
    const previousButton = document.querySelector(
        "#previous-month-button"
    );

    // 다음 달 버튼입니다.
    const nextButton = document.querySelector(
        "#next-month-button"
    );

    // Django의 json_script로 출력한 감정 데이터 요소입니다.
    const emotionDataElement = document.querySelector(
        "#calendar-emotions-data"
    );

    // 필요한 요소가 하나라도 없다면
    // JavaScript 실행을 중단합니다.
    if (
        !calendarGrid ||
        !calendarTitle ||
        !previousButton ||
        !nextButton ||
        !emotionDataElement
    ) {
        return;
    }

    // calendar.html의 data-year와 data-month 값을 읽습니다.
    let currentYear = Number(
        calendarGrid.dataset.year
    );

    let currentMonth = Number(
        calendarGrid.dataset.month
    );

    // Django에서 전달한 JSON 문자열을
    // JavaScript 객체로 변환합니다.
    //
    // 결과 예:
    // {
    //     "2026-08-03": {
    //         number: 7,
    //         name: "짝사랑",
    //         image_name: "emotion-07.png",
    //         record_id: 2
    //     }
    // }
    const calendarEmotions = JSON.parse(
        emotionDataElement.textContent
    );

    /**
     * 연도, 월, 일을 YYYY-MM-DD 형태로 변환합니다.
     *
     * 예:
     * 2026, 8, 3
     * → "2026-08-03"
     */
    function makeDateKey(year, month, date) {
        const formattedMonth = String(month).padStart(
            2,
            "0"
        );

        const formattedDate = String(date).padStart(
            2,
            "0"
        );

        return `${year}-${formattedMonth}-${formattedDate}`;
    }

    /**
     * 해당 날짜가 오늘인지 확인합니다.
     */
    function isToday(year, month, date) {
        const today = new Date();

        return (
            today.getFullYear() === year &&
            today.getMonth() + 1 === month &&
            today.getDate() === date
        );
    }

    /**
     * 캘린더의 날짜 칸 하나를 생성합니다.
     */
    function createDayCell({
        year,
        month,
        date,
        isOutside,
    }) {
        // 날짜 칸의 바깥 요소입니다.
        const dayCell = document.createElement(
            "article"
        );

        dayCell.className = "calendar-day";

        // 이전 달 또는 다음 달 날짜라면
        // 흐리게 표시하는 클래스를 추가합니다.
        if (isOutside) {
            dayCell.classList.add(
                "calendar-day--outside"
            );
        }

        // 현재 달의 오늘 날짜라면
        // 오늘 표시용 클래스를 추가합니다.
        if (
            !isOutside &&
            isToday(year, month, date)
        ) {
            dayCell.classList.add(
                "calendar-day--today"
            );
        }

        // 날짜 숫자 요소를 생성합니다.
        const dayNumber = document.createElement(
            "time"
        );

        dayNumber.className =
            "calendar-day-number";

        dayNumber.textContent = date;

        // 날짜를 YYYY-MM-DD 형태로 만듭니다.
        const dateKey = makeDateKey(
            year,
            month,
            date
        );

        dayNumber.dateTime = dateKey;

        dayCell.appendChild(dayNumber);

        // 현재 날짜에 저장된 대표 감정 정보를 찾습니다.
        const emotionData =
            calendarEmotions[dateKey];

        // 현재 달 날짜이고 실제 감정 기록이 있을 때만
        // 감정 이미지를 표시합니다.
        if (!isOutside && emotionData) {
            const emotionImage =
                document.createElement("img");

            emotionImage.className =
                "calendar-emotion";

            // 실제 감정 이미지가 저장된 경로입니다.
            //
            // records.css에서도 사용하는 이미지:
            // records/static/records/images/emotions/
            emotionImage.src =
                `/static/records/images/emotions/${emotionData.image_name}`;

            // 스크린리더가 이미지 의미를 알 수 있게 합니다.
            emotionImage.alt =
                emotionData.name;

            // 마우스를 이미지 위에 올리면
            // 감정 이름이 브라우저 기본 툴팁으로 표시됩니다.
            emotionImage.title =
                emotionData.name;

            dayCell.appendChild(
                emotionImage
            );

            // 날짜 칸에도 감정 이름을 넣습니다.
            //
            // 이미지가 아닌 칸의 빈 부분에 커서를 올려도
            // 감정 이름을 확인할 수 있습니다.
            dayCell.title =
                emotionData.name;

            // 해당 기록의 ID를 HTML 데이터 속성에 저장합니다.
            // 추후 클릭해서 상세 페이지로 이동할 때 사용할 수 있습니다.
            dayCell.dataset.recordId =
                emotionData.record_id;
        }

        return dayCell;
    }

    /**
     * 현재 선택된 연도와 월에 맞춰
     * 캘린더 전체를 다시 그립니다.
     */
    function renderCalendar() {
        // 기존 날짜 칸들을 모두 제거합니다.
        calendarGrid.innerHTML = "";

        // 제목의 연도와 월을 변경합니다.
        calendarTitle.textContent =
            `${currentYear}년 ${currentMonth}월`;

        // 현재 달 1일의 요일을 구합니다.
        //
        // 0: 일요일
        // 1: 월요일
        // ...
        // 6: 토요일
        const firstDay = new Date(
            currentYear,
            currentMonth - 1,
            1
        );

        // 현재 달의 마지막 날짜를 구합니다.
        const lastDay = new Date(
            currentYear,
            currentMonth,
            0
        );

        // 이전 달의 마지막 날짜를 구합니다.
        const previousMonthLastDay = new Date(
            currentYear,
            currentMonth - 1,
            0
        );

        const firstWeekday =
            firstDay.getDay();

        const lastDate =
            lastDay.getDate();

        const previousMonthLastDate =
            previousMonthLastDay.getDate();

        // 해당 달을 표시하는 데 필요한 주의 수를 계산합니다.
        //
        // 예:
        // 첫 요일 위치 + 현재 달 날짜 수가 35 이하이면 5주,
        // 35를 넘으면 6주를 표시합니다.
        const requiredCellCount =
            firstWeekday + lastDate;

        const totalCells =
            requiredCellCount > 35
                ? 42
                : 35;

        for (
            let index = 0;
            index < totalCells;
            index += 1
        ) {
            let cellYear = currentYear;
            let cellMonth = currentMonth;
            let cellDate;
            let isOutside = false;

            // 현재 달 1일보다 앞에 있는
            // 이전 달 날짜를 계산합니다.
            if (index < firstWeekday) {
                cellDate =
                    previousMonthLastDate -
                    firstWeekday +
                    index +
                    1;

                cellMonth =
                    currentMonth - 1;

                isOutside = true;

                if (cellMonth === 0) {
                    cellMonth = 12;
                    cellYear -= 1;
                }

            // 현재 달의 마지막 날짜 이후에 있는
            // 다음 달 날짜를 계산합니다.
            } else if (
                index >=
                firstWeekday + lastDate
            ) {
                cellDate =
                    index -
                    firstWeekday -
                    lastDate +
                    1;

                cellMonth =
                    currentMonth + 1;

                isOutside = true;

                if (cellMonth === 13) {
                    cellMonth = 1;
                    cellYear += 1;
                }

            // 현재 달의 날짜입니다.
            } else {
                cellDate =
                    index -
                    firstWeekday +
                    1;
            }

            const dayCell =
                createDayCell({
                    year: cellYear,
                    month: cellMonth,
                    date: cellDate,
                    isOutside,
                });

            calendarGrid.appendChild(
                dayCell
            );
        }
    }

    // 이전 달 버튼을 눌렀을 때
    previousButton.addEventListener(
        "click",
        () => {
            currentMonth -= 1;

            // 1월에서 이전 달을 누르면
            // 전년도 12월로 이동합니다.
            if (currentMonth === 0) {
                currentMonth = 12;
                currentYear -= 1;
            }

            renderCalendar();
        }
    );

    // 다음 달 버튼을 눌렀을 때
    nextButton.addEventListener(
        "click",
        () => {
            currentMonth += 1;

            // 12월에서 다음 달을 누르면
            // 다음 연도 1월로 이동합니다.
            if (currentMonth === 13) {
                currentMonth = 1;
                currentYear += 1;
            }

            renderCalendar();
        }
    );

    // 페이지가 처음 열렸을 때
    // 현재 달의 캘린더를 생성합니다.
    renderCalendar();
});