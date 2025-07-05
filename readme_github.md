# 🔧 기계 소리 진단 시스템

압축기, 모터, 베어링 등의 기계 소리를 AI로 분석하여 정상/재측정/고장 상태를 실시간 진단하는 웹 애플리케이션입니다.

![Demo](https://img.shields.io/badge/Demo-Streamlit-red)
![Python](https://img.shields.io/badge/Python-3.8+-blue)
![License](https://img.shields.io/badge/License-MIT-green)

## ✨ 주요 기능

- 🎵 **드래그-앤-드롭** WAV 파일 업로드
- 📊 **RMS 레벨 분석** (dBFS 기반 음량 측정)
- 🧠 **AI 유사도 분석** (코사인 거리 기반)
- 🎚️ **실시간 임계치 조정** 슬라이더
- 📈 **게이지 차트** 시각화
- ⏱️ **성능 모니터링** (밀리초 단위)
- 🛡️ **포괄적 오류 처리**
- 🌊 **파형 분석**

## 🎯 3단계 판정 시스템

- 🟢 **정상**: 기계가 정상 작동 중
- 🟡 **재측정**: 추가 점검 또는 재측정 필요
- 🔴 **고장**: 즉시 수리 필요

## 🚀 빠른 시작

### 1. 저장소 클론
```bash
git clone https://github.com/your-username/machine-sound-diagnosis.git
cd machine-sound-diagnosis
```

### 2. 의존성 설치
```bash
pip install -r requirements.txt
```

### 3. 웹 애플리케이션 실행
```bash
streamlit run streamlit_app.py
```

### 4. 브라우저에서 접속
자동으로 `http://localhost:8501`이 열립니다.

## 📁 프로젝트 구조

```
machine-sound-diagnosis/
├── streamlit_app.py          # 메인 웹 애플리케이션
├── audio_converter.py        # CLI 버전 (고급 분석)
├── quickcold.py             # 압축된 버전 (50줄)
├── requirements.txt         # 의존성 목록
├── test_samples/           # 테스트용 샘플 파일
│   ├── normal_compressor.wav    # 정상 압축기 소리
│   ├── normal_motor.wav         # 정상 모터 소리
│   ├── normal_bearing.wav       # 정상 베어링 소리
│   └── faulty_machine.wav       # 고장 기계 소리
├── reports/                # PDF 리포트 저장 폴더
├── results/                # CSV 결과 저장 폴더
└── README.md               # 이 파일
```

## 🎵 테스트 샘플 사용법

### 웹 UI에서 테스트:
1. **베이스라인 설정**: `test_samples/normal_*.wav` 3개 파일을 사이드바에 업로드
2. **테스트 파일**: `test_samples/faulty_machine.wav` 파일을 메인 영역에 업로드
3. **결과 확인**: 실시간으로 분석 결과와 시각화 확인

### CLI에서 테스트:
```bash
# 단일 파일 분석
python audio_converter.py test_samples/normal_compressor.wav

# 베이스라인 포함 분석
python audio_converter.py --baseline test_samples/normal_*.wav test_samples/faulty_machine.wav

# 여러 파일 배치 분석
python audio_converter.py test_samples/*.wav
```

## ⚙️ 설정 및 커스터마이징

### 주요 매개변수:
```python
# streamlit_app.py 또는 audio_converter.py에서 수정
THRESH_DB = -35              # RMS 임계치 (dBFS)
COSINE_THRESH = 0.8          # 유사도 높은 기준
COSINE_THRESH_LOW = 0.6      # 유사도 낮은 기준
```

### 웹 UI 슬라이더:
- **범위**: -60 ~ -10 dBFS
- **권장값**: 
  - 엄격한 기준: -40 이하
  - 일반 기준: -35 ~ -30
  - 관대한 기준: -25 이상

## 📊 분석 알고리즘

### RMS (Root Mean Square) 분석:
- 오디오 신호의 평균 음량 레벨 측정
- dBFS 단위로 표현 (0에 가까울수록 큰 소리)
- 임계치 기반 정상/고장 판별

### 코사인 유사도 분석:
- MEL Spectrogram, MFCC 등 음향 특징 추출
- 정상 베이스라인과의 패턴 유사성 측정
- 0~1 값 (1에 가까울수록 유사)

## 🛠️ 요구사항

### Python 버전:
- Python 3.8 이상

### 주요 라이브러리:
- `streamlit`: 웹 UI 프레임워크
- `librosa`: 오디오 신호 처리
- `scikit-learn`: 코사인 유사도 계산
- `matplotlib`: 시각화
- `numpy`: 수치 계산

전체 목록은 `requirements.txt` 참조

## 🎯 사용 사례

### 산업 현장:
- 압축기 상태 모니터링
- 모터 베어링 점검
- 펌프 이상 감지
- 기어박스 진단

### 특징:
- **실시간 분석**: 몇 초 내 즉시 결과
- **현장 친화적**: 드래그-앤-드롭 간편 사용
- **정확한 진단**: AI 기반 다중 알고리즘
- **성능 모니터링**: 처리 시간 실시간 표시

## 🚨 지원 파일 형식

### ✅ 지원:
- **형식**: WAV (.wav)
- **최대 크기**: 100MB
- **최소 길이**: 0.1초
- **권장 설정**: 16kHz, 16bit, 모노/스테레오

### ❌ 지원하지 않음:
- MP3, M4A, FLAC 등 (WAV로 변환 필요)

## 🆘 문제 해결

### 일반적인 문제:

**Q: "지원하지 않는 파일 형식" 오류가 나요**
- A: WAV 파일만 지원합니다. Audacity로 변환하세요.

**Q: "파일이 너무 큽니다" 오류가 나요**
- A: 100MB 이하로 파일 크기를 줄이세요.

**Q: 분석 결과가 이상해요**
- A: 임계치 슬라이더를 조정해보세요. 기계마다 적절한 기준이 다릅니다.

**Q: 베이스라인 설정은 어떻게 하나요?**
- A: 정상 상태의 동일 기계 소리 3개 이상을 사이드바에 업로드하세요.

## 📝 라이센스

MIT License - 자유롭게 사용, 수정, 배포 가능

## 🤝 기여하기

1. Fork 생성
2. 기능 브랜치 생성 (`git checkout -b feature/amazing-feature`)
3. 변경사항 커밋 (`git commit -m 'Add amazing feature'`)
4. 브랜치에 Push (`git push origin feature/amazing-feature`)
5. Pull Request 생성

## 📞 지원

- **이슈**: GitHub Issues 탭에서 버그 리포트 또는 기능 요청
- **이메일**: support@example.com
- **문서**: 이 README 파일

## 🎬 데모 영상

[![데모 영상](https://img.youtube.com/vi/YOUR_VIDEO_ID/0.jpg)](https://www.youtube.com/watch?v=YOUR_VIDEO_ID)

---

**⭐ 이 프로젝트가 도움이 되셨다면 Star를 눌러주세요!**