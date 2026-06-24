import pandas as pd
from .base import LayerResult


def analyze_market_structure(df: pd.DataFrame, timeframe: str = "1W") -> LayerResult:
    """
    Layer 3: Market Structure (지지·저항 분석)

    주봉/월봉을 기반으로 주요 지지·저항 레벨을 계산하고
    현재가가 어느 위치에 있는지 판단
    """
    if df.empty or len(df) < 13:  # 최소 13주 필요
        return LayerResult(
            layer_name="Market Structure",
            score=50,
            signal="HOLD",
            confidence=0.3,
            rationale="충분한 데이터 부재"
        )

    df = df.copy()

    # 최근 52주(1년) 고점/저점
    recent_52 = df.tail(52) if len(df) >= 52 else df
    year_high = recent_52['High'].max()
    year_low = recent_52['Low'].min()

    # 최근 13주(3개월) 고점/저점
    recent_13 = df.tail(13)
    q_high = recent_13['High'].max()
    q_low = recent_13['Low'].min()

    current_price = df['Close'].iloc[-1]

    # 지지/저항 레벨 정의
    resistance = year_high
    support = year_low
    mid_point = (resistance + support) / 2

    # 점수 계산: 현재가가 어느 위치에 있는가?
    price_ratio = (current_price - support) / (resistance - support) if resistance != support else 0.5
    price_ratio = max(0, min(1, price_ratio))  # 0~1 범위

    # 0.5 이상이면 저항 방향으로, 0.5 이하면 지지 방향으로 해석
    if price_ratio >= 0.65:
        # 고점 근처
        score = 70 + price_ratio * 20
        score = min(100, score)
        signal = "SELL"  # 매도 주의
        confidence = 0.75
        rationale = f"52주 고점({resistance:.0f}) 근처, 익절 기회"
    elif price_ratio >= 0.50:
        # 중점에서 저항 사이
        score = 65
        signal = "HOLD"
        confidence = 0.6
        rationale = f"중장기 저항 구간({mid_point:.0f}~{resistance:.0f})"
    elif price_ratio > 0.35:
        # 중점에서 지지 사이
        score = 60
        signal = "HOLD"
        confidence = 0.6
        rationale = f"중장기 지지 구간({support:.0f}~{mid_point:.0f})"
    else:
        # 저점 근처
        score = 30 + (1 - price_ratio) * 20
        score = max(0, score)
        signal = "BUY"  # 매수 기회
        confidence = 0.75
        rationale = f"52주 저점({support:.0f}) 근처, 매수 기회"

    return LayerResult(
        layer_name="Market Structure",
        score=score,
        signal=signal,
        confidence=confidence,
        rationale=rationale
    )
