// 날짜 자동 생성
// 8/3 대면 회의: record-list PR 머지 후에 JS의 임시 날짜 생성 코드 제거 예정
// 이후 views.py의 Python calendar 모듈 방식으로 수정

document.addEventListener("DOMContentLoaded", () => {
    const calendarGrid = document.querySelector("#emotion-calendar-grid");
    const calendarTitle = document.querySelector("#calendar-title");
    const previousButton = document.querySelector("#previous-month-button");
    const nextButton = document.querySelector("#next-month-button");

    if (!calendarGrid || !calendarTitle || !previousButton || !nextButton) {
        return;
    }

    let currentYear = Number(calendarGrid.dataset.year);
    let currentMonth = Number(calendarGrid.dataset.month);

    const sampleEmotions = {
        2: "emotion-01.svg",
        6: "emotion-01.svg",
        9: "emotion-01.svg",
        12: "emotion-01.svg",
        18: "emotion-01.svg",
        23: "emotion-01.svg",
        29: "emotion-01.svg",
    };

    function isToday(year, month, date) {
        const today = new Date();

        return (
            today.getFullYear() === year &&
            today.getMonth() + 1 === month &&
            today.getDate() === date
        );
    }

    function createDayCell({
        year,
        month,
        date,
        isOutside,
    }) {
        const dayCell = document.createElement("article");
        dayCell.className = "calendar-day";

        if (isOutside) {
            dayCell.classList.add("calendar-day--outside");
        }

        if (!isOutside && isToday(year, month, date)) {
            dayCell.classList.add("calendar-day--today");
        }

        const dayNumber = document.createElement("time");
        dayNumber.className = "calendar-day-number";
        dayNumber.textContent = date;

        const formattedMonth = String(month).padStart(2, "0");
        const formattedDate = String(date).padStart(2, "0");

        dayNumber.dateTime =
            `${year}-${formattedMonth}-${formattedDate}`;

        dayCell.appendChild(dayNumber);

        if (!isOutside && sampleEmotions[date]) {
            const emotionImage = document.createElement("img");
            emotionImage.className = "calendar-emotion";
            emotionImage.src =
                `/static/diary/images/${sampleEmotions[date]}`;
            emotionImage.alt = "감정";

            dayCell.appendChild(emotionImage);
        }

        return dayCell;
    }

    function renderCalendar() {
        calendarGrid.innerHTML = "";
        calendarTitle.textContent = `${currentYear}년 ${currentMonth}월`;

        const firstDay = new Date(
            currentYear,
            currentMonth - 1,
            1
        );

        const lastDay = new Date(
            currentYear,
            currentMonth,
            0
        );

        const previousMonthLastDay = new Date(
            currentYear,
            currentMonth - 1,
            0
        );

        const firstWeekday = firstDay.getDay();
        const lastDate = lastDay.getDate();
        const previousMonthLastDate =
            previousMonthLastDay.getDate();

        const totalCells = 35;

        for (let index = 0; index < totalCells; index += 1) {
            let cellYear = currentYear;
            let cellMonth = currentMonth;
            let cellDate;
            let isOutside = false;

            if (index < firstWeekday) {
                cellDate =
                    previousMonthLastDate -
                    firstWeekday +
                    index +
                    1;

                cellMonth = currentMonth - 1;
                isOutside = true;

                if (cellMonth === 0) {
                    cellMonth = 12;
                    cellYear -= 1;
                }
            } else if (index >= firstWeekday + lastDate) {
                cellDate =
                    index -
                    firstWeekday -
                    lastDate +
                    1;

                cellMonth = currentMonth + 1;
                isOutside = true;

                if (cellMonth === 13) {
                    cellMonth = 1;
                    cellYear += 1;
                }
            } else {
                cellDate = index - firstWeekday + 1;
            }

            const dayCell = createDayCell({
                year: cellYear,
                month: cellMonth,
                date: cellDate,
                isOutside,
            });

            calendarGrid.appendChild(dayCell);
        }
    }

    previousButton.addEventListener("click", () => {
        currentMonth -= 1;

        if (currentMonth === 0) {
            currentMonth = 12;
            currentYear -= 1;
        }

        renderCalendar();
    });

    nextButton.addEventListener("click", () => {
        currentMonth += 1;

        if (currentMonth === 13) {
            currentMonth = 1;
            currentYear += 1;
        }

        renderCalendar();
    });

    renderCalendar();
});