# 기계 소리 진단 시스템 Dockerfile
FROM python:3.11-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 의존성 설치 (librosa 및 오디오 처리용)
RUN apt-get update && apt-get install -y \
    libsndfile1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 먼저 복사 및 설치 (Docker 캐시 활용)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY streamlit_app.py .
COPY audio_converter.py .
# COPY quickcold.py .          ← 이 줄 삭제 또는 주석

# 테스트 샘플 디렉토리 생성 (선택사항)
RUN mkdir -p test_samples reports results

# 테스트 샘플 파일 복사 (있는 경우)
# COPY test_samples/ ./test_samples/    ← 이 줄 삭제 또는 주석

# Streamlit 포트 노출
EXPOSE 8501

# 헬스체크 추가
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Streamlit 앱 실행
CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.enableCORS=false", "--server.enableXsrfProtection=false"]