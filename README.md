# HeartMark

사진, 감정, 장소를 함께 기록해 나만의 감정 지도를 만드는 위치 기반 기록 서비스입니다.

현재 저장소에는 팀 개발을 위한 Django 기본 구조만 구성되어 있습니다.

## 기술 스택

- Backend: Django
- Frontend: HTML, CSS, JavaScript
- Database: SQLite (개발 환경)
- Map: Kakao Maps 또는 Google Maps 연동 예정

## 실행 방법

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

서버 실행 후 `http://127.0.0.1:8000/`으로 접속합니다.

## 프로젝트 구조

```text
HeartMark/
├── config/                    # Django 프로젝트 설정
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── common/                    # 통합 담당자: 공통 메인 및 공유 기능
├── accounts/                  # A: 회원, 인증, 캐릭터, 온보딩
│   └── templates/accounts/
├── locations/                 # B: 지도 및 장소 탐색
│   └── templates/locations/
├── records/                   # C: 기록 작성, 상세, 수정, 삭제
│   └── templates/records/
├── diary/                     # D: 다이어리 목록 및 캘린더 조회
│   └── templates/diary/
│
├── templates/
│   ├── base.html              # 전체 페이지 공통 레이아웃
│   └── includes/
│       ├── header.html
│       └── bottom_nav.html
│
├── manage.py
└── requirements.txt
```

각 앱의 정적 파일은 충돌 방지를 위해
`<app>/static/<app>/css/`, `<app>/static/<app>/js/`에 둡니다.

## 역할 분담

### A — 홍연우: 회원/인증 & 캐릭터·온보딩

- 담당 앱: `accounts`
- 담당 화면: 로그인, 회원가입, 캐릭터 선택, 온보딩
- 주요 모델 예정: `User`, `Character`
- 협업: B, C, D 파트에서 공통으로 사용할 인증 구조 공유

### B — 신은아: 지도 & 장소 탐색

- 담당 앱: `locations`
- 담당 화면: 메인 지도, 장소 검색, 장소 선택
- 주요 모델 예정: `Place`
- 협업: C가 저장한 장소 좌표와 감정 정보를 지도 핀으로 표시

### C — 서영은: 기록 작성 & 상세·수정·삭제

- 담당 앱: `records`
- 담당 화면: 기록 작성 모달, 기록 상세, 기록 수정, 기록 삭제
- 주요 모델 예정: `Record`
- UI 방향: 회색 오버레이 위에 기록 작성 팝업 표시
- 협업: B의 장소 선택 결과를 전달받아 기록에 저장
- 협업: D의 캘린더와 목록에서 기록을 선택하면 C의 상세 화면으로 이동

### D — 한지수: 다이어리 & 캘린더 조회

- 담당 앱: `diary`
- 담당 화면: 캘린더, 다이어리 목록
- 협업: C가 정의한 `Record` 모델과 JSON 응답 형식을 기준으로 조회하고,
  기록 선택 시 `records` 앱의 상세 페이지로 연결

## 공통 개발 규칙

- 공통 레이아웃은 `templates/base.html`을 상속합니다.
- 각 담당자는 원칙적으로 자기 앱 폴더 안의 파일만 수정합니다.
- 메인 화면 조각은 각 앱의 `templates/<app>/partials/`에 작성합니다.
- 공용 파일은 지정된 통합 담당자 한 명만 수정합니다.
- CSS와 JavaScript는 각 앱의 `static/<app>/` 아래에 작성합니다.
- 앱별 URL에는 `app_name`을 사용합니다.
- 모델 구조와 API 응답 형식은 구현 전에 팀 전체가 먼저 합의합니다.
- 비밀키와 외부 API 키는 Git에 올리지 않습니다.

자세한 충돌 방지 및 통합 규칙은
[`docs/INTEGRATION.md`](docs/INTEGRATION.md)를 확인합니다.

## 템플릿 사용 예시

```django
{% extends "base.html" %}
{% load static %}

{% block title %}페이지 제목 | HeartMark{% endblock %}

{% block extra_css %}
<link rel="stylesheet" href="{% static 'accounts/css/accounts.css' %}">
{% endblock %}

{% block content %}
<!-- 담당 화면 작성 -->
{% endblock %}

{% block extra_js %}
<script src="{% static 'accounts/js/accounts.js' %}"></script>
{% endblock %}
```

## 현재 상태

- [x] Django 프로젝트 기본 구조
- [x] 기능 도메인별 앱 분리
- [x] 공통 `base.html` 및 include 구조
- [x] 파트별 HTML, CSS, JavaScript 파일 분리
- [ ] DB 모델 및 ERD 설계
- [ ] 화면 디자인 및 기능 구현
- [ ] API 연동
- [ ] 테스트 및 배포

## 출처
- 서울 자치구 지도: Kurykh, Wikimedia Commons, CC BY-SA 3.0
수정하여 사용함
