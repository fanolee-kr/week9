# 식당 메뉴 OCR 프로그램 (Gemini API 활용)

이 프로그램은 식당 정보 이미지와 요일별 메뉴 이미지를 합쳐서 Google의 Gemini API를 통해 OCR(광학 문자 인식)을 수행합니다.

## 필요 조건

- Python 3.6 이상
- Google Gemini API 키
- 필요한 Python 패키지 (requirements.txt 참조)

## 설치 방법

1. 필요한 패키지 설치:
   ```
   pip install -r requirements.txt
   ```

2. Google Gemini API 키 설정:
   - [Google AI Studio](https://makersuite.google.com/app/apikey)에서 API 키 생성
   - 프로젝트 루트에 `.env` 파일을 생성하고 다음과 같이 API 키 설정:
     ```
     GOOGLE_API_KEY=your_api_key_here
     ```

## 사용 방법

1. 이미지 파일을 `./output` 디렉토리에 다음과 같이 저장:
   - `0.png`: 식당 정보
   - `1.png`: 월요일 메뉴
   - `2.png`: 화요일 메뉴
   - `3.png`: 수요일 메뉴
   - `4.png`: 목요일 메뉴
   - `5.png`: 금요일 메뉴

2. 스크립트 실행:
   ```
   python menu_ocr.py
   ```

3. 기본적으로 월요일 메뉴만 처리합니다. 다른 요일도 처리하려면 코드 하단의 주석을 해제하세요.

## 결과

- 합친 이미지는 `./output/combined_[요일번호].png`로 저장됩니다.
- OCR 결과는 `./output/menu_[요일번호].md` 파일로 저장됩니다.
- OCR 결과는 마크다운 형식으로 콘솔에도 출력됩니다.

## 특징

- Google의 Gemini AI 모델을 사용하여 고품질의 OCR 결과를 얻습니다.
- 메뉴 항목, 칼로리 정보 등을 구조화된 형식으로 추출합니다.
- 결과를 직원들에게 공유하기 좋은 포맷으로 제공합니다.

## 문제 해결

OCR 결과가 정확하지 않은 경우:
- 이미지 품질 확인
- 프롬프트 조정 (코드 내 ocr_with_gemini 함수에서 수정 가능)
- 이미지 전처리 (대비 조정, 해상도 개선 등) 