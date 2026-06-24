from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from typing import Optional

from ..database import get_db
from ..models.watchlist import Watchlist

router = APIRouter(prefix="/watchlist", tags=["watchlist"])


class WatchlistRequest:
    def __init__(self, symbol: str, name: str):
        self.symbol = symbol
        self.name = name


class WatchlistResponse:
    def __init__(self, id: str, symbol: str, name: str, added_at: datetime):
        self.id = id
        self.symbol = symbol
        self.name = name
        self.added_at = added_at

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "symbol": self.symbol,
            "name": self.name,
            "added_at": self.added_at.isoformat()
        }


@router.post("/", response_model=dict)
async def add_watchlist(
    symbol: str,
    name: str,
    session: AsyncSession = Depends(get_db)
) -> dict:
    """관심 종목 추가 (최대 50개)"""
    # 현재 관심 종목 개수 확인
    stmt = select(Watchlist)
    result = await session.execute(stmt)
    count = len(result.scalars().all())

    if count >= 50:
        raise HTTPException(status_code=400, detail="관심 종목 최대 개수(50)에 도달했습니다")

    # 중복 확인
    stmt = select(Watchlist).where(Watchlist.symbol == symbol)
    result = await session.execute(stmt)
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(status_code=400, detail="이미 추가된 종목입니다")

    # 새 종목 추가
    watchlist = Watchlist(symbol=symbol, name=name)
    session.add(watchlist)
    await session.commit()
    await session.refresh(watchlist)

    return {
        "id": str(watchlist.id),
        "symbol": watchlist.symbol,
        "name": watchlist.name,
        "added_at": watchlist.added_at.isoformat()
    }


@router.get("/", response_model=dict)
async def get_watchlist(
    session: AsyncSession = Depends(get_db)
) -> dict:
    """전체 관심 종목 목록 조회"""
    stmt = select(Watchlist).order_by(Watchlist.added_at.desc())
    result = await session.execute(stmt)
    watchlist = result.scalars().all()

    return {
        "total": len(watchlist),
        "items": [
            {
                "id": str(item.id),
                "symbol": item.symbol,
                "name": item.name,
                "added_at": item.added_at.isoformat()
            }
            for item in watchlist
        ]
    }


@router.delete("/{symbol}", response_model=dict)
async def remove_watchlist(
    symbol: str,
    session: AsyncSession = Depends(get_db)
) -> dict:
    """관심 종목 제거"""
    stmt = select(Watchlist).where(Watchlist.symbol == symbol)
    result = await session.execute(stmt)
    watchlist = result.scalar_one_or_none()

    if not watchlist:
        raise HTTPException(status_code=404, detail="종목을 찾을 수 없습니다")

    await session.delete(watchlist)
    await session.commit()

    return {"message": f"{symbol}이 제거되었습니다"}
