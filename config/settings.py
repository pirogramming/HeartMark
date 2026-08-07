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

SECRET_KEY = "development-only"
DEBUG = True
ALLOWED_HOSTS = []

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
    "friendships",
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

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

LANGUAGE_CODE = "ko-kr"
TIME_ZONE = "Asia/Seoul"
USE_I18N = True
USE_TZ = True
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

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

