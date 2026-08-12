#!/bin/sh
set -e

echo "[entrypoint] 마이그레이션 실행"
python manage.py migrate --noinput

# collectstatic은 컨테이너가 뜰 때마다 실행한다.
# staticfiles는 named volume이라 이미지가 새로 배포돼도 볼륨은 그대로 남는다.
# 즉 빌드 시점에만 모으면 새 정적 파일이 서버에 반영되지 않는다.
echo "[entrypoint] 정적 파일 수집"
python manage.py collectstatic --noinput --clear

# 소셜 로그인은 allauth의 SocialApp/Site 레코드가 DB에 있어야 동작한다.
# 이 커맨드는 환경변수를 읽어 해당 레코드를 만들어준다.
# 키가 비어 있으면 CommandError로 죽는데, 그 때문에 앱 전체가 못 뜨면
# 로그를 보기 어려우므로 경고만 남기고 부팅은 계속한다.
echo "[entrypoint] 소셜 로그인 설정"
if ! python manage.py setup_social_login; then
    echo "[entrypoint] 경고: 소셜 로그인 설정 실패. 소셜 로그인이 동작하지 않는다."
    echo "[entrypoint] EC2의 .env에 GOOGLE_CLIENT_ID/SECRET 등이 채워져 있는지 확인할 것."
fi

echo "[entrypoint] 애플리케이션 시작"
exec "$@"
