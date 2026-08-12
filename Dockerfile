FROM python:3.11-slim

# Python 로그가 버퍼링 없이 바로 docker logs에 찍히도록 함.
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Pillow(이미지 처리)와 cryptography 빌드에 필요한 시스템 패키지.
# 설치 후 apt 캐시를 지워 이미지 용량을 줄인다.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libjpeg-dev \
        zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# requirements를 먼저 복사해서 의존성 레이어를 캐시한다.
# 코드만 바뀐 경우 이 레이어는 재사용되어 빌드가 빨라진다.
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY . .

# SQLite 파일과 업로드 미디어가 저장될 디렉토리.
# compose에서 named volume을 여기에 마운트해 재배포 시에도 데이터가 유지된다.
RUN mkdir -p /app/data /app/media /app/staticfiles

RUN chmod +x /app/docker/entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/app/docker/entrypoint.sh"]
CMD ["gunicorn", "config.wsgi:application", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "3", \
     "--timeout", "60", \
     "--access-logfile", "-", \
     "--error-logfile", "-"]
