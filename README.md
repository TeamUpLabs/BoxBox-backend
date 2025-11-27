# BoxBox API

F1 관련 데이터를 제공하는 FastAPI 기반 백엔드 애플리케이션입니다.

## 📋 개요

이 프로젝트는 F1(Formula 1) 관련 정보를 제공하는 REST API 서버입니다. 드라이버, 팀, 서킷, 세션, 경기 결과, 뉴스 등 다양한 F1 데이터에 접근할 수 있습니다.

## 🚀 주요 기능

- **드라이버 정보**: F1 드라이버들의 상세 정보 제공
- **팀 정보**: F1 팀 및 컨스트럭터 정보 제공
- **서킷 정보**: F1 경기가 열리는 서킷 정보 제공
- **세션 정보**: 연습, 예선, 본경기 등 세션별 정보 제공
- **경기 결과**: 각 그랜드프릭스의 경기 결과 제공
- **뉴스**: F1 관련 최신 뉴스 제공

## 🛠️ 기술 스택

- **Python 3.x**
- **FastAPI**: 웹 프레임워크
- **Supabase**: 데이터베이스 및 백엔드 서비스
- **SQLAlchemy**: ORM
- **Pydantic**: 데이터 유효성 검증
- **Uvicorn**: ASGI 서버

## 📦 설치 및 실행

### 1. 저장소 클론

```bash
git clone <repository-url>
cd f1app
```

### 2. 가상환경 생성 및 활성화

```bash
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# 또는
.venv\Scripts\activate  # Windows
```

### 3. 의존성 설치

```bash
pip install -r requirements.txt
```

### 4. 환경 변수 설정

`.env` 파일을 생성하고 다음 변수들을 설정하세요:

```env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
SUPABASE_DB_URL=your_supabase_db_url
```

### 5. 서버 실행

```bash
python main.py
```

서버는 `http://localhost:8000`에서 실행됩니다.

## 📚 API 문서

서버 실행 후 다음 URL에서 API 문서를 확인할 수 있습니다:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 🏗️ 프로젝트 구조

```
f1app/
├── main.py                 # 애플리케이션 진입점
├── requirements.txt        # Python 의존성
├── .env                    # 환경 변수 파일
├── src/
│   ├── core/
│   │   └── config.py       # 설정 관리
│   └── v2/
│       ├── crawler/        # 데이터 크롤러
│       ├── dto/           # 데이터 전송 객체
│       ├── models/        # 데이터베이스 모델
│       ├── repositories/   # 데이터 접근 계층
│       ├── router/        # API 라우터
│       └── utils/         # 유틸리티 함수
├── data/                   # 정적 데이터 파일
│   ├── F1Drivers.json     # 드라이버 데이터
│   └── F1Teams.json       # 팀 데이터
└── cache/                  # 캐시 디렉토리
```

## 🔗 API 엔드포인트

### 기본 엔드포인트

- `GET /` - API 기본 정보
- `GET /health` - 헬스 체크

### v2 API 엔드포인트

- `GET /v2/drivers` - 드라이버 정보
- `GET /v2/teams` - 팀 정보
- `GET /v2/circuits` - 서킷 정보
- `GET /v2/sessions` - 세션 정보
- `GET /v2/results` - 경기 결과
- `GET /v2/news` - 뉴스 정보

## 🌐 CORS 설정

개발 환경에서는 모든 출처를 허용하도록 설정되어 있습니다. 프로덕션 환경에서는 보안을 위해 구체적인 도메인으로 제한하는 것을 권장합니다.

## 📝 라이선스

이 프로젝트의 라이선스 정보를 여기에 추가하세요.

## 🤝 기여

기여를 원하시면 다음 단계를 따르세요:

1. 이 저장소를 포크합니다
2. 기능 브랜치를 생성합니다 (`git checkout -b feature/AmazingFeature`)
3. 변경사항을 커밋합니다 (`git commit -m 'Add some AmazingFeature'`)
4. 브랜치에 푸시합니다 (`git push origin feature/AmazingFeature`)
5. Pull Request를 생성합니다

## 📞 문의

질문이나 문제가 있을 경우 이슈를 생성해주세요.