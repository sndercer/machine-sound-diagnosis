# streamlit_app.py - 기계 소리 진단 웹 UI (수정된 버전)
import streamlit as st
import librosa
import soundfile as sf
import numpy as np
import matplotlib.pyplot as plt
import io
from sklearn.metrics.pairwise import cosine_similarity
from datetime import datetime
import time

# 페이지 설정
st.set_page_config(
    page_title="🔧 기계 소리 진단 시스템",
    page_icon="🔧",
    layout="wide"
)

# 설정 변수
THRESH_DB = -35
COSINE_THRESH = 0.8
COSINE_THRESH_LOW = 0.6

@st.cache_data
def calculate_rms_dbfs(audio):
    """RMS(dBFS) 계산"""
    rms = np.sqrt(np.mean(audio**2))
    if rms == 0:
        return -np.inf
    return 20 * np.log10(rms)

@st.cache_data
def extract_features(audio, sr):
    """오디오 특징 추출"""
    mel_spec = librosa.feature.melspectrogram(y=audio, sr=sr, n_mels=32)
    mel_features = np.mean(mel_spec, axis=1)
    
    mfcc = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=8)
    mfcc_features = np.mean(mfcc, axis=1)
    
    spectral_centroids = librosa.feature.spectral_centroid(y=audio, sr=sr)
    spectral_rolloff = librosa.feature.spectral_rolloff(y=audio, sr=sr)
    zero_crossing_rate = librosa.feature.zero_crossing_rate(audio)
    
    features = np.concatenate([
        mel_features,
        mfcc_features,
        [np.mean(spectral_centroids)],
        [np.mean(spectral_rolloff)],
        [np.mean(zero_crossing_rate)]
    ])
    
    return features

def load_baseline_features(baseline_files):
    """베이스라인 특징 로드"""
    if not baseline_files:
        return None, 0
    
    start_time = time.time()
    all_features = []
    
    for uploaded_file in baseline_files:
        try:
            audio_data = uploaded_file.getvalue()
            audio, sr = librosa.load(io.BytesIO(audio_data), sr=16000, mono=True)
            features = extract_features(audio, sr)
            all_features.append(features)
        except Exception as e:
            st.error(f"베이스라인 파일 {uploaded_file.name} 처리 오류: {e}")
    
    processing_time = (time.time() - start_time) * 1000
    
    if all_features:
        return np.mean(all_features, axis=0), processing_time
    return None, processing_time

def judge_status(rms, similarity=None, thresh_db=-35):
    """상태 판정"""
    rms_ok = rms <= thresh_db
    
    if similarity is None:
        return "정상" if rms_ok else "고장"
    
    cos_ok = similarity >= COSINE_THRESH
    cos_mid = similarity >= COSINE_THRESH_LOW
    
    if rms_ok and cos_ok:
        return "정상"
    elif rms_ok and cos_mid:
        return "재측정"
    elif cos_ok and not rms_ok:
        return "재측정"
    else:
        return "고장"

def create_gauge_chart(rms, similarity=None, status="정상", thresh_db=-35):
    """게이지 차트 생성"""
    if similarity is not None:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
    else:
        fig, ax1 = plt.subplots(1, 1, figsize=(5, 4))
    
    # RMS 게이지
    rms_normalized = max(0, min(100, (rms + 60) / 60 * 100))
    
    colors = {"정상": "green", "재측정": "orange", "고장": "red"}
    color = colors.get(status, "gray")
    
    bars1 = ax1.barh(['RMS Level'], [rms_normalized], color=color, height=0.3)
    
    thresh_normalized = max(0, min(100, (thresh_db + 60) / 60 * 100))
    ax1.axvline(x=thresh_normalized, color='red', linestyle='--', linewidth=2, 
               label=f'임계치 ({thresh_db} dBFS)')
    
    ax1.set_xlim(0, 100)
    ax1.set_xlabel('RMS Level (%)')
    ax1.set_title(f'RMS: {rms:.1f} dBFS')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    if rms_normalized < 90:
        ax1.text(rms_normalized + 2, 0, f'{rms:.1f}', va='center', fontweight='bold')
    
    # 유사도 게이지
    if similarity is not None:
        similarity_percent = similarity * 100
        
        if similarity >= COSINE_THRESH:
            color2 = 'green'
        elif similarity >= COSINE_THRESH_LOW:
            color2 = 'orange'
        else:
            color2 = 'red'
        
        bars2 = ax2.barh(['Similarity'], [similarity_percent], color=color2, height=0.3)
        
        ax2.axvline(x=COSINE_THRESH * 100, color='green', linestyle='--', linewidth=2)
        ax2.axvline(x=COSINE_THRESH_LOW * 100, color='orange', linestyle='--', linewidth=2)
        
        ax2.set_xlim(0, 100)
        ax2.set_xlabel('Similarity (%)')
        ax2.set_title(f'Similarity: {similarity:.3f}')
        ax2.grid(True, alpha=0.3)
        
        if similarity_percent < 90:
            ax2.text(similarity_percent + 2, 0, f'{similarity:.3f}', va='center', fontweight='bold')
    
    plt.tight_layout()
    return fig

def create_waveform_plot(audio, sr, status):
    """파형 플롯 생성"""
    fig, ax = plt.subplots(1, 1, figsize=(10, 4))
    
    time = np.linspace(0, len(audio)/sr, len(audio))
    ax.plot(time, audio)
    ax.set_title(f"Waveform - {status}")
    ax.set_xlabel('Time (seconds)')
    ax.set_ylabel('Amplitude')
    ax.grid(True)
    
    plt.tight_layout()
    return fig

def analyze_audio_file(uploaded_file, baseline_features, thresh_db):
    """안전한 오디오 분석"""
    try:
        # 파일 크기 체크
        if uploaded_file.size > 100 * 1024 * 1024:  # 100MB
            return None, f"파일이 너무 큽니다 (최대 100MB, 현재: {uploaded_file.size/1024/1024:.1f}MB)"
        
        # 전체 처리 시간 측정
        total_start = time.time()
        
        # 오디오 로드
        audio_data = uploaded_file.getvalue()
        load_start = time.time()
        audio, sr = librosa.load(io.BytesIO(audio_data), sr=16000, mono=True)
        load_time = (time.time() - load_start) * 1000
        
        if len(audio) == 0:
            return None, "오디오 데이터가 비어있습니다."
        
        # RMS 계산
        rms_start = time.time()
        rms = calculate_rms_dbfs(audio)
        rms_time = (time.time() - rms_start) * 1000
        
        # 유사도 계산
        similarity = None
        similarity_time = 0
        
        if baseline_features is not None:
            sim_start = time.time()
            try:
                features = extract_features(audio, sr)
                similarity = cosine_similarity([baseline_features], [features])[0][0]
                similarity_time = (time.time() - sim_start) * 1000
            except:
                similarity = None
        
        # 상태 판정
        status = judge_status(rms, similarity, thresh_db)
        
        total_time = (time.time() - total_start) * 1000
        
        return {
            'audio': audio,
            'sr': sr,
            'rms': rms,
            'similarity': similarity,
            'status': status,
            'load_time': load_time,
            'rms_time': rms_time,
            'similarity_time': similarity_time,
            'total_time': total_time
        }, None
        
    except Exception as e:
        return None, f"분석 오류: {str(e)}"

# 메인 UI
def main():
    st.title("🔧 기계 소리 진단 시스템")
    st.markdown("압축기, 모터, 베어링 등의 기계 소리를 분석하여 상태를 진단합니다.")
    
    # 사이드바 설정
    st.sidebar.header("⚙️ 설정")
    
    # 임계치 조정 슬라이더
    st.sidebar.subheader("🎚️ 임계치 조정")
    thresh_db = st.sidebar.slider(
        "RMS 임계치 (dBFS)",
        min_value=-60,
        max_value=-10,
        value=-35,
        step=1,
        help="낮을수록 엄격한 기준"
    )
    
    st.sidebar.info(f"현재 기준: {thresh_db} dBFS")
    
    # 베이스라인 파일 업로드
    st.sidebar.subheader("📁 정상 베이스라인 파일")
    baseline_files = st.sidebar.file_uploader(
        "정상 상태 WAV 파일들 (3개 권장)",
        type=['wav'],
        accept_multiple_files=True,
        key="baseline"
    )
    
    # 베이스라인 처리
    baseline_features = None
    baseline_time = 0
    if baseline_files:
        with st.sidebar:
            with st.spinner("베이스라인 로딩 중..."):
                baseline_features, baseline_time = load_baseline_features(baseline_files)
            if baseline_features is not None:
                st.success(f"✅ {len(baseline_files)}개 베이스라인 로드됨")
                st.info(f"⏱️ 처리 시간: {baseline_time:.1f}ms")
    
    # 메인 영역
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🎵 분석할 WAV 파일 업로드")
        
        uploaded_file = st.file_uploader(
            "WAV 파일을 드래그 앤 드롭하거나 클릭하여 업로드하세요",
            type=['wav'],
            key="test_file"
        )
        
        if uploaded_file is not None:
            st.info(f"📁 파일명: {uploaded_file.name}")
            st.info(f"📊 파일 크기: {uploaded_file.size / 1024:.1f} KB")
            
            with st.spinner("분석 중..."):
                result, error = analyze_audio_file(uploaded_file, baseline_features, thresh_db)
            
            if error:
                st.error(f"❌ 오류: {error}")
                st.markdown("""
                ### 🛠️ 문제 해결:
                - WAV 파일만 지원됩니다
                - 최대 파일 크기: 100MB
                - 최소 길이: 0.1초 이상
                """)
            else:
                # 분석 성공
                audio = result['audio']
                sr = result['sr']
                rms = result['rms']
                similarity = result['similarity']
                status = result['status']
                
                # 결과 표시
                st.subheader("📊 분석 결과")
                
                if status == "정상":
                    st.success(f"🟢 **판정: {status}**")
                elif status == "재측정":
                    st.warning(f"🟡 **판정: {status}**")
                else:
                    st.error(f"🔴 **판정: {status}**")
                
                # 상세 정보
                col_info1, col_info2, col_info3 = st.columns(3)
                
                with col_info1:
                    st.metric("RMS (dBFS)", f"{rms:.2f}")
                    st.metric("길이 (초)", f"{len(audio)/sr:.2f}")
                
                with col_info2:
                    if similarity is not None:
                        st.metric("유사도", f"{similarity:.3f}")
                    st.metric("샘플링 레이트", f"{sr} Hz")
                
                with col_info3:
                    st.metric("처리 시간", f"{result['total_time']:.1f} ms")
                    st.metric("현재 임계치", f"{thresh_db} dBFS")
                
                # 게이지 차트
                st.subheader("📈 게이지 차트")
                gauge_fig = create_gauge_chart(rms, similarity, status, thresh_db)
                st.pyplot(gauge_fig)
                
                # 파형 차트
                st.subheader("🌊 파형 분석")
                waveform_fig = create_waveform_plot(audio, sr, status)
                st.pyplot(waveform_fig)
    
    with col2:
        st.subheader("📋 진단 기준")
        
        st.markdown(f"""
        **RMS 임계치:** {thresh_db} dBFS
        
        **판정 기준:**
        - 🟢 **정상**: RMS ≤ {thresh_db} dBFS
        - 🟡 **재측정**: 애매한 경계값
        - 🔴 **고장**: RMS > {thresh_db} dBFS
        
        **유사도 기준** (베이스라인 사용시):
        - 🟢 **정상**: ≥ {COSINE_THRESH}
        - 🟡 **재측정**: {COSINE_THRESH_LOW} ~ {COSINE_THRESH}
        - 🔴 **고장**: < {COSINE_THRESH_LOW}
        """)
        
        if baseline_features is not None:
            st.success("✅ 베이스라인 활성화됨")
        else:
            st.warning("⚠️ 베이스라인 없음")

if __name__ == "__main__":
    main()