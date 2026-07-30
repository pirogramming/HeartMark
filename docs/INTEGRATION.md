# 통합 규칙

## 작업 경계

| 담당자 | 수정하는 기본 경로 | 메인 화면 전달 파일 |
|---|---|---|
| A | `accounts/` | `accounts/partials/user_menu.html` |
| B | `locations/` | `locations/partials/map_tab.html` |
| C | `records/` | `records/partials/record_modal.html` |
| D | `diary/` | `diary/partials/diary_tab.html` |

각 담당자는 원칙적으로 자신의 앱 폴더 안에서만 작업합니다.

## 공용 파일

다음 파일은 통합 담당자 한 명만 수정합니다.

- `config/settings.py`
- `config/urls.py`
- `templates/base.html`
- `templates/includes/`
- `common/`
- `requirements.txt`

새 앱 등록, 외부 라이브러리 추가, 공통 레이아웃 변경이 필요하면 담당자가 공용
파일을 직접 수정하지 않고 PR 설명에 필요한 변경을 기록합니다. 통합 담당자가
해당 변경을 한 번에 반영합니다.

## 앱 내부 규칙

- 템플릿: `<app>/templates/<app>/`
- CSS: `<app>/static/<app>/css/`
- JavaScript: `<app>/static/<app>/js/`
- URL name: `<app>:<name>`
- 앱 내부 partial: `<app>/templates/<app>/partials/`

정적 파일과 템플릿 경로에 앱 이름을 한 번 더 넣어 Django 파일명 충돌을
방지합니다.

## 모델 간 참조

- A가 사용자 모델 규격을 먼저 공유합니다.
- B는 장소 모델과 좌표 필드 규격을 공유합니다.
- C는 A와 B의 모델을 참조해 기록 모델을 정의하고 생성·상세·수정·삭제를
  모두 담당합니다.
- D는 별도 기록 모델이나 상세 화면을 만들지 않고 C의 기록 모델을 캘린더와
  목록에서 조회합니다.
- D의 목록에서 기록을 선택하면 C가 만든 `records` 상세 URL로 이동합니다.
- 다른 앱의 모델을 임의로 수정하지 않습니다.

## 기록 기능 경계

| 기능 | 담당 앱 |
|---|---|
| 기록 작성 | `records` (C) |
| 기록 상세 | `records` (C) |
| 기록 수정 | `records` (C) |
| 기록 삭제 | `records` (C) |
| 월별 캘린더 조회 | `diary` (D) |
| 다이어리 목록 조회 | `diary` (D) |

`diary`는 기록 상세 템플릿을 별도로 만들지 않습니다. 상세·수정·삭제 화면은
항상 `records`의 URL과 템플릿을 사용합니다.

## 권장 브랜치

- `feature/accounts-*`
- `feature/locations-*`
- `feature/records-*`
- `feature/diary-*`
- `integration/*`

한 PR에는 한 담당 앱의 변경만 포함하는 것을 원칙으로 합니다.
