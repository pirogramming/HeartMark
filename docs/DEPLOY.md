# 배포 가이드 (staging)

`staging` 브랜치에 push하면 GitHub Actions가 이미지를 빌드해 Docker Hub에 올리고,
EC2에 접속해 새 이미지로 교체한다.

구성은 컨테이너 두 개다.

- `web` — Django + gunicorn (외부에 포트를 열지 않음)
- `nginx` — 80 포트를 받아 `web`으로 프록시하고, 정적 파일/미디어는 직접 서빙

DB는 SQLite이고, `db_data` / `media_data` / `static_data` 세 개의 named volume에
데이터가 보관되어 재배포해도 남는다.

---

## 1. GitHub Secrets 등록

리포지토리 Settings → Secrets and variables → Actions 에서 4개를 등록한다.

| 이름 | 값 |
|---|---|
| `DOCKER_USERNAME` | Docker Hub 사용자명 |
| `DOCKER_PASSWORD` | Docker Hub Access Token (계정 비밀번호 말고 토큰 권장) |
| `EC2_HOST` | EC2 퍼블릭 IP 또는 도메인 |
| `EC2_KEY` | `.pem` 키 파일의 **전체 내용** |

`EC2_KEY`는 파일 경로가 아니라 내용을 통째로 붙여넣어야 한다.
`-----BEGIN ... PRIVATE KEY-----` 줄과 마지막 `-----END ...-----` 줄까지 포함해야 하고,
줄바꿈도 그대로 유지해야 한다.

## 2. EC2 준비 (최초 1회)

Docker와 Compose 플러그인을 설치한다.

```bash
sudo apt-get update
sudo apt-get install -y docker.io docker-compose-plugin
sudo usermod -aG docker ubuntu
# 그룹 반영을 위해 재접속
exit
```

배포 디렉토리를 만든다. 워크플로우가 이 경로에 파일을 넣는다.

```bash
mkdir -p ~/heartmark
```

## 3. EC2에 `.env` 만들기 (최초 1회)

시크릿은 GitHub에 넣지 않고 서버에서 직접 관리한다.
워크플로우는 이 파일을 덮어쓰지 않으므로 한 번 만들어두면 계속 재사용된다.

```bash
nano ~/heartmark/.env
```

`.env.example`을 참고해 아래 값들을 채운다.

```
DJANGO_SECRET_KEY=<아래 명령으로 생성한 값>
DJANGO_ALLOWED_HOSTS=<EC2 퍼블릭 IP 또는 도메인>
DJANGO_CSRF_TRUSTED_ORIGINS=http://<EC2 퍼블릭 IP 또는 도메인>

SITE_DOMAIN=<EC2 퍼블릭 IP 또는 도메인>
SITE_NAME=HeartMark Staging
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
NAVER_CLIENT_ID=...
NAVER_CLIENT_SECRET=...
KAKAO_CLIENT_ID=...
KAKAO_CLIENT_SECRET=...
KAKAO_REST_KEY=...
KAKAO_JS_KEY=...
```

`DJANGO_SECRET_KEY`는 아래로 만든다.

```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

Django의 `get_random_secret_key()`를 써도 되지만 `#`, `$`, `'` 같은 문자가 섞일 수 있다.
이 `.env`는 docker compose가 변수 치환에도 사용하기 때문에 그런 문자가 들어가면
값이 잘리거나 경고가 난다. 영숫자와 `-_`만 나오는 위 방식이 안전하다.

### `.env` 작성 시 주의

- `=` 앞뒤에 공백을 넣지 않는다 (`KEY=value`, `KEY = value` 아님)
- 값을 따옴표로 감싸지 않는다 — 따옴표까지 값에 포함될 수 있다
- `export`를 붙이지 않는다
- 값 안에 `$`가 있으면 `$$`로 이스케이프한다

`DJANGO_CSRF_TRUSTED_ORIGINS`는 `http://`를 반드시 붙여야 한다.
빠뜨리면 로그인/글쓰기 같은 POST 요청이 403으로 막힌다.

## 4. 보안 그룹

EC2 보안 그룹 인바운드에서 아래를 연다.

- `80/tcp` — 서비스 접속
- `22/tcp` — GitHub Actions의 SSH 배포 (가능하면 소스 IP를 제한)

## 5. 소셜 로그인 콘솔 설정

각 provider 콘솔에서 staging 도메인의 redirect URI를 등록한다.
이걸 안 하면 로그인 시 redirect_uri_mismatch가 난다.

```
http://<EC2 주소>/accounts/google/login/callback/
http://<EC2 주소>/accounts/naver/login/callback/
http://<EC2 주소>/accounts/kakao/login/callback/
```

카카오맵을 쓰는 화면 때문에 카카오 콘솔의 **플랫폼 > Web 사이트 도메인**에도
`http://<EC2 주소>`를 추가해야 한다.

## 6. 배포

`staging` 브랜치에 push하면 자동으로 돈다.
수동 실행은 Actions 탭 → Deploy to EC2 → Run workflow.

---

## 컨테이너가 부팅할 때 하는 일

`docker/entrypoint.sh`가 gunicorn을 띄우기 전에 아래를 순서대로 실행한다.

1. `migrate` — 스키마 반영. BGM 시드 데이터도 여기서 들어간다.
2. `collectstatic` — 정적 파일을 볼륨에 모은다. 볼륨은 이미지가 바뀌어도
   유지되기 때문에, 빌드 시점이 아니라 부팅할 때마다 새로 모아야 반영된다.
3. `setup_social_login` — allauth의 `Site`/`SocialApp` 레코드를 `.env` 값으로 만든다.
   이 단계가 실패해도 원인을 로그에서 보려고 부팅은 계속한다.
   대신 소셜 로그인은 동작하지 않으니 로그를 확인할 것.

## 문제가 생겼을 때

```bash
cd ~/heartmark

# 상태 확인
docker compose -f docker-compose.prod.yml ps

# 로그 (부팅 과정이 여기 다 찍힌다)
docker compose -f docker-compose.prod.yml logs -f web
docker compose -f docker-compose.prod.yml logs -f nginx

# 재시작
docker compose -f docker-compose.prod.yml restart
```

증상별로 볼 곳은 다음과 같다.

- **400 Bad Request** — `.env`의 `DJANGO_ALLOWED_HOSTS`에 접속 중인 주소가 없다.
- **403 CSRF verification failed** — `DJANGO_CSRF_TRUSTED_ORIGINS`가 비었거나 `http://`가 빠졌다.
- **CSS가 깨짐** — `collectstatic`이 실패했는지 `logs web`에서 확인.
- **소셜 로그인 실패** — `logs web`의 `[entrypoint] 소셜 로그인 설정` 부분과
  provider 콘솔의 redirect URI를 확인.

## 데이터 백업

SQLite 파일 하나만 챙기면 된다.

WAL 모드라 파일을 그냥 복사하면 커밋되지 않은 내용이 빠질 수 있다.
SQLite의 백업 API를 쓰면 실행 중에도 안전한 사본이 나온다.

```bash
docker compose -f docker-compose.prod.yml exec -T web python -c "
import sqlite3
src = sqlite3.connect('/app/data/db.sqlite3')
dst = sqlite3.connect('/app/data/backup.sqlite3')
src.backup(dst)
dst.close(); src.close()
print('백업 완료')
"
docker compose -f docker-compose.prod.yml cp web:/app/data/backup.sqlite3 ./backup.sqlite3
```

업로드된 사진은 `media_data` 볼륨에 있다.

```bash
docker run --rm -v heartmark_media_data:/media -v $(pwd):/backup alpine \
  tar czf /backup/media-backup.tar.gz -C /media .
```
