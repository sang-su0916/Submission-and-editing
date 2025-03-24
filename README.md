# 학원 문제 관리 시스템 - README

이 프로젝트는 영어, 수학학원 선생님과 학생들을 대상으로 기존 학원의 문제를 데이터로 활용하여 문제 출제 및 첨삭이 가능한 웹 애플리케이션입니다.

## 주요 기능

### 1. 문제 데이터베이스 시스템
- 영어, 수학 과목의 문제 데이터 관리
- 문제 카테고리 및 난이도 분류 시스템
- 문제 검색 및 필터링 기능

### 2. 문제 출제 기능
- 기존 문제 기반 새 문제 생성 (유의어 대체, 문장 구조 변경, 난이도 조정)
- 문제 유형별 템플릿 생성
- 직접 문제 작성 기능

### 3. 첨삭 시스템
- 학생 답안 입력 인터페이스
- 답안 평가 및 첨삭 기능
- 첨삭 결과 시각화 및 피드백 제공
- 첨삭 이력 관리

### 4. 사용자 인증
- 역할별 접근 권한 (관리자, 선생님, 학생)
- 사용자 관리 기능

## 설치 및 실행 방법

### 필요 라이브러리
```
streamlit
pandas
numpy
matplotlib
seaborn
nltk
scikit-learn
```

### 설치
```bash
pip install -r requirements.txt
```

### 실행
```bash
streamlit run app.py
```

## 기본 계정 정보
- 관리자: admin / admin123
- 선생님: teacher / teacher123
- 학생: student / student123

## 프로젝트 구조
```
streamlit_academy_app/
├── app.py                  # 메인 애플리케이션 파일
├── pages/                  # 페이지 모듈
│   ├── problem_generation.py  # 문제 출제 페이지
│   ├── feedback_system.py     # 첨삭 시스템 페이지
│   ├── feedback_analytics.py  # 첨삭 결과 분석 페이지
│   └── admin.py               # 관리자 페이지
├── models/                 # 데이터 모델 및 알고리즘
│   ├── data_models.py         # 데이터 모델 클래스
│   └── problem_generator.py   # 문제 생성 알고리즘
├── utils/                  # 유틸리티 함수
│   ├── auth.py                # 인증 관련 유틸리티
│   └── common.py              # 공통 유틸리티 함수
└── data/                   # 데이터 파일
    ├── problems.json          # 문제 데이터
    ├── feedback_data.json     # 첨삭 데이터
    └── users.json             # 사용자 데이터
```

## 개발자 정보
이 프로젝트는 깃허브와 스트림릿을 활용하여 개발되었습니다.
