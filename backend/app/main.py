from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .config import settings
from .database import engine, Base
from .api import watchlist, analysis

# DB 초기화
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✓ Database tables created")
    yield
    # Shutdown
    await engine.dispose()
    print("✓ Database connection closed")


# FastAPI 앱 생성
app = FastAPI(
    title="AI Stock Intelligence Platform",
    description="AI 주식 분석 어시스턴트 - Phase 1",
    version="0.1.0",
    lifespan=lifespan
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(watchlist.router)
app.include_router(analysis.router)


@app.get("/", tags=["health"])
async def root():
    """헬스 체크"""
    return {
        "message": "AI Stock Intelligence Platform - Phase 1",
        "status": "running",
        "version": "0.1.0"
    }


@app.get("/health", tags=["health"])
async def health():
    """헬스 체크"""
    return {
        "status": "healthy",
        "database": "connected",
        "api_version": "0.1.0"
    }
