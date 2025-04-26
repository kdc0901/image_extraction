# Image Extraction Project

이 프로젝트는 이미지 추출 및 처리에 관한 작업을 수행하는 Python 기반 프로젝트입니다.

## 프로젝트 구조

```
image_extraction/
├── src/                    # 소스 코드
│   ├── utils/             # 유틸리티 함수들
│   ├── models/            # 이미지 처리 모델
│   ├── preprocessing/     # 전처리 관련 코드
│   └── postprocessing/    # 후처리 관련 코드
├── output/                # 결과물 저장
│   ├── raw/              # 원본 이미지
│   ├── processed/        # 처리된 이미지
│   └── final/            # 최종 결과물
├── tests/                 # 테스트 코드
│   ├── unit/             # 단위 테스트
│   ├── integration/      # 통합 테스트
│   └── data/             # 테스트용 데이터
├── docs/                  # 문서
└── scripts/               # 스크립트 파일
```

## 설치 방법

1. Python 3.8 이상이 설치되어 있어야 합니다.
2. 필요한 패키지를 설치합니다:
   ```bash
   pip install -r requirements.txt
   ```

## 사용 방법

1. 프로젝트를 클론합니다:
   ```bash
   git clone [repository-url]
   cd image_extraction
   ```

2. 필요한 패키지를 설치합니다:
   ```bash
   pip install -r requirements.txt
   ```

3. 메인 스크립트를 실행합니다:
   ```bash
   python src/main.py
   ```

## 개발 환경

- Python 3.8+
- 주요 의존성 패키지:
  - OpenCV
  - NumPy
  - Pillow
  - Matplotlib

## 테스트

테스트를 실행하려면:
```bash
python -m pytest tests/
```

## 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 