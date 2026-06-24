"""
Phase 1 초기 데이터 수집 스크립트
삼성전자, SK하이닉스, 현대차 10년 OHLCV 데이터 수집
"""
import asyncio
from app.database import AsyncSessionLocal, engine, Base
from app.services import initialize_watchlist_data
from app.models import Watchlist, StockPrice


async def main():
    # DB 테이블 생성
    print("Creating database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✓ Database tables created")

    # 관심 종목 초기 데이터 수집
    symbols = ["005930.KS", "000660.KS", "005380.KS"]
    names = ["삼성전자", "SK하이닉스", "현대차"]

    print("\nFetching OHLCV data from yfinance...")
    results = await initialize_watchlist_data(symbols, names)

    # Watchlist에 추가
    print("\nAdding to watchlist...")
    async with AsyncSessionLocal() as session:
        for symbol, name in zip(symbols, names):
            existing = await session.execute(
                f"SELECT * FROM watchlist WHERE symbol = '{symbol}'"
            )
            if not existing:
                watchlist = Watchlist(symbol=symbol, name=name)
                session.add(watchlist)
        await session.commit()

    print("\n✓ Phase 1 초기 데이터 수집 완료!")
    print(f"\nResults:")
    for symbol, result in results.items():
        print(f"  {symbol}: {result}")


if __name__ == "__main__":
    asyncio.run(main())
