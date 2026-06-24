from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from datetime import datetime
import pandas as pd

from ..database import get_db
from ..models.stock import StockPrice
from ..layers import (
    analyze_market_regime,
    analyze_smart_money,
    analyze_market_structure,
    analyze_volume_profile,
    analyze_technical,
    LayerResult
)
from ..engine import calculate_score

router = APIRouter(prefix="/analysis", tags=["analysis"])


async def get_ohlcv_dataframe(
    session: AsyncSession,
    symbol: str,
    timeframe: str = "1D",
    limit: int = 250
) -> pd.DataFrame:
    """심볼과 타임프레임으로 OHLCV 데이터 조회"""
    stmt = select(StockPrice).where(
        and_(
            StockPrice.symbol == symbol,
            StockPrice.timeframe == timeframe
        )
    ).order_by(StockPrice.date.asc()).limit(limit)

    result = await session.execute(stmt)
    records = result.scalars().all()

    if not records:
        return pd.DataFrame()

    data = [
        {
            "Date": record.date,
            "Open": record.open,
            "High": record.high,
            "Low": record.low,
            "Close": record.close,
            "Volume": record.volume
        }
        for record in records
    ]

    df = pd.DataFrame(data)
    df.set_index("Date", inplace=True)
    return df


@router.get("/{symbol}", response_model=dict)
async def get_analysis(
    symbol: str,
    session: AsyncSession = Depends(get_db)
) -> dict:
    """
    특정 종목의 상세 분석 리포트

    Returns:
        {
            "symbol": "005930.KS",
            "name": "삼성전자",
            "current_price": 82000,
            "timestamp": "2024-06-24T16:30:00",
            "short_term": {...},
            "long_term": {...},
            "layers": [...],
            "total_score": 85,
            "signal": "BUY",
            "confidence": 0.82,
            "warning": False,
            "warning_message": None,
            "rationale": [...]
        }
    """

    # 일봉 데이터 조회
    df_daily = await get_ohlcv_dataframe(session, symbol, "1D", 250)
    if df_daily.empty:
        raise HTTPException(status_code=404, detail="데이터를 찾을 수 없습니다")

    # 주봉 데이터 조회 (선택사항)
    df_weekly = await get_ohlcv_dataframe(session, symbol, "1W", 260)

    current_price = float(df_daily['Close'].iloc[-1])
    current_date = df_daily.index[-1]

    # Layer 분석 실행
    layer_results: list[LayerResult] = [
        analyze_market_regime(df_daily),
        analyze_smart_money(df_daily),
        analyze_market_structure(df_weekly if not df_weekly.empty else df_daily),
        analyze_volume_profile(df_daily),
        analyze_technical(df_daily)
    ]

    # 가중치 통합
    score_result = calculate_score(layer_results)

    # 근거 리스트 생성
    rationale = [layer["rationale"] for layer in score_result["layers"]]

    return {
        "symbol": symbol,
        "current_price": round(current_price, 2),
        "timestamp": current_date.isoformat(),
        "short_term": {
            "signal": score_result["signal"],
            "score": score_result["total_score"],
            "confidence": score_result["confidence"],
            "buy_prices": [
                round(current_price * 0.98, 0),
                round(current_price * 0.95, 0),
                round(current_price * 0.92, 0)
            ],
            "sell_prices": [
                round(current_price * 1.05, 0),
                round(current_price * 1.10, 0),
                round(current_price * 1.15, 0)
            ]
        },
        "long_term": {
            "signal": score_result["signal"],
            "score": score_result["total_score"],
            "confidence": score_result["confidence"],
            "target_price": round(current_price * 1.20, 0)
        },
        "scenarios": {
            "up": 0.62 if score_result["signal"] == "BUY" else 0.35,
            "sideways": 0.25,
            "down": 0.13 if score_result["signal"] == "BUY" else 0.40
        },
        "layers": score_result["layers"],
        "total_score": score_result["total_score"],
        "signal": score_result["signal"],
        "confidence": score_result["confidence"],
        "warning": score_result["warning"],
        "warning_message": score_result["warning_message"],
        "rationale": rationale
    }
