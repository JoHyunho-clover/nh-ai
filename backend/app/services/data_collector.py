import yfinance as yf
import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from datetime import datetime, timedelta
from typing import Optional

from ..models.stock import StockPrice
from ..database import AsyncSessionLocal


async def fetch_ohlcv(
    symbol: str,
    period: str = "10y",
    interval: str = "1d"
) -> Optional[pd.DataFrame]:
    """
    yfinance로 OHLCV 데이터 수집
    symbol: e.g., "005930.KS" (삼성전자)
    period: "10y", "5y", "1mo" 등
    interval: "1d" (일봉), "1wk" (주봉), "1mo" (월봉)
    """
    try:
        data = yf.download(
            symbol,
            period=period,
            interval=interval,
            progress=False
        )
        if data.empty:
            return None
        return data
    except Exception as e:
        print(f"Error fetching {symbol}: {e}")
        return None


async def upsert_prices(
    session: AsyncSession,
    symbol: str,
    df: pd.DataFrame,
    timeframe: str = "1D"
) -> int:
    """
    DataFrame의 OHLCV 데이터를 DB에 저장/업데이트
    timeframe: "1D", "1W", "1M"
    """
    inserted_count = 0

    for date, row in df.iterrows():
        # date를 파이썬 date 객체로 변환
        if hasattr(date, 'date'):
            date_obj = date.date()
        else:
            date_obj = pd.Timestamp(date).date()

        # 이미 존재하는지 확인
        stmt = select(StockPrice).where(
            and_(
                StockPrice.symbol == symbol,
                StockPrice.timeframe == timeframe,
                StockPrice.date == date_obj
            )
        )
        existing = await session.execute(stmt)
        existing_record = existing.scalar_one_or_none()

        if existing_record is None:
            # 새로운 레코드 추가
            new_price = StockPrice(
                symbol=symbol,
                timeframe=timeframe,
                date=date_obj,
                open=float(row['Open']),
                high=float(row['High']),
                low=float(row['Low']),
                close=float(row['Close']),
                volume=int(row['Volume'])
            )
            session.add(new_price)
            inserted_count += 1

    await session.commit()
    return inserted_count


async def initialize_watchlist_data(
    symbols: list[str],
    names: list[str]
) -> dict:
    """
    관심 종목 초기 데이터 수집 (일봉/주봉/월봉)
    """
    results = {}
    async with AsyncSessionLocal() as session:
        for symbol, name in zip(symbols, names):
            print(f"Fetching {symbol} ({name})...")

            # 일봉 (5년)
            daily_df = await fetch_ohlcv(symbol, period="5y", interval="1d")
            if daily_df is not None:
                daily_count = await upsert_prices(session, symbol, daily_df, "1D")
                print(f"  → Daily: {daily_count} records")

            # 주봉 (10년)
            weekly_df = await fetch_ohlcv(symbol, period="10y", interval="1wk")
            if weekly_df is not None:
                weekly_count = await upsert_prices(session, symbol, weekly_df, "1W")
                print(f"  → Weekly: {weekly_count} records")

            # 월봉 (10년)
            monthly_df = await fetch_ohlcv(symbol, period="10y", interval="1mo")
            if monthly_df is not None:
                monthly_count = await upsert_prices(session, symbol, monthly_df, "1M")
                print(f"  → Monthly: {monthly_count} records")

            results[symbol] = {"name": name, "status": "completed"}

    return results
