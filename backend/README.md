# Backend: AI Stock Intelligence Platform - Phase 1

FastAPI 기반 주식 분석 엔진

## 설정

### 1. 환경변수 설정
```bash
cp .env.example .env
```

기본값:
```
DATABASE_URL=postgresql+asyncpg://nhaiuser:nhaipass@localhost:5432/nhai_db
REDIS_URL=redis://localhost:6379/0
```

### 2. PostgreSQL + Redis 시작
```bash
docker-compose up -d
```

### 3. Python 패키지 설치
```bash
pip install -r requirements.txt
```

### 4. 초기 데이터 수집 (선택)
```bash
python init_data.py
```
- 삼성전자(005930.KS), SK하이닉스(000660.KS), 현대차(005380.KS)의 10년 OHLCV 데이터 수집
- Watchlist에 자동 추가

## 실행

### FastAPI 서버 시작
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 접속
- API: http://localhost:8000
- Docs: http://localhost:8000/docs

## API 엔드포인트

### Watchlist
- `POST /watchlist` — 관심 종목 추가
  ```bash
  curl -X POST "http://localhost:8000/watchlist?symbol=005930.KS&name=삼성전자"
  ```
- `GET /watchlist` — 전체 관심 종목 목록
- `DELETE /watchlist/{symbol}` — 종목 제거

### Analysis
- `GET /analysis/{symbol}` — 상세 분석 리포트
  ```bash
  curl "http://localhost:8000/analysis/005930.KS"
  ```
  응답:
  ```json
  {
    "symbol": "005930.KS",
    "current_price": 82000,
    "timestamp": "2024-06-24T16:30:00",
    "short_term": {
      "signal": "BUY",
      "score": 88,
      "confidence": 0.92,
      "buy_prices": [80360, 77900, 75440],
      "sell_prices": [86100, 90200, 94300]
    },
    "long_term": {
      "signal": "BUY",
      "score": 88,
      "confidence": 0.92,
      "target_price": 98400
    },
    "layers": [
      {
        "layer_name": "Market Regime",
        "score": 85,
        "signal": "BUY",
        "confidence": 0.85,
        "rationale": "..."
      },
      ...
    ],
    "total_score": 85,
    "signal": "BUY",
    "confidence": 0.82,
    "warning": false,
    "warning_message": null,
    "rationale": [...]
  }
  ```

## 디렉토리 구조

```
backend/
├── app/
│   ├── main.py              # FastAPI 진입점
│   ├── config.py            # 설정
│   ├── database.py          # SQLAlchemy 설정
│   ├── models/
│   │   ├── stock.py         # StockPrice 모델
│   │   └── watchlist.py     # Watchlist 모델
│   ├── api/
│   │   ├── watchlist.py     # Watchlist 엔드포인트
│   │   └── analysis.py      # Analysis 엔드포인트
│   ├── services/
│   │   └── data_collector.py  # yfinance 데이터 수집
│   ├── layers/
│   │   ├── base.py          # LayerResult 클래스
│   │   ├── layer1_market_regime.py
│   │   ├── layer2_smart_money.py
│   │   ├── layer3_market_structure.py
│   │   ├── layer4_volume_profile.py
│   │   └── layer5_technical.py
│   └── engine/
│       └── scorer.py        # 점수 통합 엔진
├── init_data.py             # 초기 데이터 수집 스크립트
├── requirements.txt
├── docker-compose.yml
├── .env.example
└── README.md
```

## Phase 1 완성 기준

✓ yfinance 데이터 수집 (10년 OHLCV)
✓ PostgreSQL 스키마 (StockPrice, Watchlist)
✓ Layer 1~5 분석 엔진
✓ 점수 통합 엔진 (11개 레이어)
✓ FastAPI 기본 엔드포인트
- Layer 6~11은 Phase 2에서 추가
- 자기개선 루프는 Phase 4에서 추가

## 다음 단계

Phase 2: Layer 6~11 + Claude API 통합
