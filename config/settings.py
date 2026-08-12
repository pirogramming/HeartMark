import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# 프로젝트 루트의 .env 파일을 읽어서 os.environ에 등록한다.
# .env는 .gitignore에 포함되어 있어 git에 올라가지 않으므로,
# API 키 같은 민감한 값은 코드에 직접 쓰지 않고 이 방식으로 불러온다.
load_dotenv(BASE_DIR / ".env")

def load_local_env():
    env_path = BASE_DIR / ".env"
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


load_local_env()

# 배포 환경에서는 아래 값들을 모두 환경변수로 주입한다.
# 기본값은 로컬 개발 기준이라, .env 없이도 로컬 실행은 그대로 동작한다.
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "development-only")

# 서버용 compose 파일에 DJANGO_DEBUG=False가 박혀 있으므로
# 누가 .env를 빠뜨려도 프로덕션에서 DEBUG가 켜지지 않는다.
DEBUG = os.environ.get("DJANGO_DEBUG", "True").lower() not in ("false", "0", "no")

# "1.2.3.4,example.com" 형태의 콤마 구분 문자열을 받는다.
ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get("DJANGO_ALLOWED_HOSTS", "").split(",")
    if host.strip()
]

# nginx 뒤에 있을 때 POST 요청의 CSRF origin 검사를 통과시키기 위한 값.
# "http://1.2.3.4" 처럼 스킴을 반드시 포함해야 한다.
CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.environ.get("DJANGO_CSRF_TRUSTED_ORIGINS", "").split(",")
    if origin.strip()
]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    "allauth.socialaccount.providers.kakao",
    "allauth.socialaccount.providers.naver",
    "common",
    "accounts",
    "mypage",
    "locations",
    "records",
    "diary",
    "social_hub",
    "friendships",
    "record_sharing",
    "bgm",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "locations.context_processors.location_verification",
            ],
        },
    }
]
WSGI_APPLICATION = "config.wsgi.application"

# 컨테이너에서는 DB 파일을 /app/data 아래에 둔다.
# BASE_DIR(=/app)에 볼륨을 마운트하면 코드가 덮여버리므로 경로를 분리했다.
DB_PATH = os.environ.get("DJANGO_DB_PATH") or (BASE_DIR / "db.sqlite3")

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": DB_PATH,
        "OPTIONS": {
            # WAL 모드는 읽기와 쓰기가 서로를 막지 않게 해준다.
            # gunicorn 워커가 여러 개인 환경에서 "database is locked"를 크게 줄여준다.
            "init_command": "PRAGMA journal_mode=WAL; PRAGMA synchronous=NORMAL;",
            # 잠금이 걸렸을 때 바로 실패하지 않고 최대 20초까지 기다린다.
            "timeout": 20,
            # 쓰기 트랜잭션의 잠금을 시작 시점에 잡아 갱신 충돌을 방지한다.
            "transaction_mode": "IMMEDIATE",
        },
    }
}

LANGUAGE_CODE = "ko-kr"
TIME_ZONE = "Asia/Seoul"
USE_I18N = True
USE_TZ = True
STATIC_URL = "static/"

# collectstatic이 각 앱의 static/을 모아두는 위치. nginx가 이 디렉토리를 서빙한다.
STATIC_ROOT = os.environ.get("DJANGO_STATIC_ROOT") or (BASE_DIR / "staticfiles")

# 프로젝트 루트의 static/은 현재 존재하지 않는다.
# 없는 경로를 그대로 두면 collectstatic이 W004 경고를 내므로 있을 때만 넣는다.
STATICFILES_DIRS = [BASE_DIR / "static"] if (BASE_DIR / "static").exists() else []

MEDIA_URL = "media/"
MEDIA_ROOT = os.environ.get("DJANGO_MEDIA_ROOT") or (BASE_DIR / "media")

LOGIN_URL = "/accounts/login/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# 카카오맵 API 키 (locations 앱: 위치 선택/지도 화면에서 사용)
# - KAKAO_JS_KEY: 브라우저에서 카카오맵 JS SDK를 로드할 때 쓰는 키.
#   공개돼도 큰 문제는 없지만(카카오 콘솔에 등록된 도메인에서만 동작),
#   그래도 값 자체는 .env에서 관리한다.
# - KAKAO_REST_KEY: 서버(Django)에서 좌표→주소 변환(coord2address), 주소 검색 등
#   REST API를 호출할 때 쓰는 키. 절대 클라이언트(JS, 템플릿)로 내려보내면 안 되고,
#   반드시 뷰(views.py)에서 서버 사이드로만 사용해야 한다.
# 두 값 모두 .env 파일에 정의되어 있어야 하며, .env는 git에 커밋되지 않는다.
KAKAO_JS_KEY = os.environ.get("KAKAO_JS_KEY")
KAKAO_REST_KEY = os.environ.get("KAKAO_REST_KEY")
SITE_ID = 1

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

LOGIN_REDIRECT_URL = "/accounts/login/redirect/"
LOGOUT_REDIRECT_URL = "/"

ACCOUNT_EMAIL_VERIFICATION = "none"
SOCIALACCOUNT_AUTO_SIGNUP = True
SOCIALACCOUNT_LOGIN_ON_GET = True
SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "SCOPE": ["profile", "email"],
        "AUTH_PARAMS": {"access_type": "online"},
    }
}

