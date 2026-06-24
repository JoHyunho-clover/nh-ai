import pandas as pd
from .base import LayerResult


def analyze_market_regime(df: pd.DataFrame) -> LayerResult:
    """
    Layer 1: Market Regime (강세/약세/횡보 판정)

    200일 이동평균 기준으로 시장 체제 판정
    - 현재가 > MA200 + 상승 추세 → 강세 (BUY)
    - 현재가 < MA200 + 하락 추세 → 약세 (SELL)
    - 그 외 → 횡보 (HOLD)
    """
    if df.empty or len(df) < 200:
        return LayerResult(
            layer_name="Market Regime",
            score=50,
            signal="HOLD",
            confidence=0.3,
            rationale="충분한 데이터 부재"
        )

    df = df.copy()
    current_price = df['Close'].iloc[-1]

    # 200일 MA
    ma200 = df['Close'].rolling(window=200).mean().iloc[-1]

    # 20일 MA (단기 추세)
    ma20 = df['Close'].rolling(window=20).mean().iloc[-1]

    # 현재가가 20일 MA보다 높으면 상승 추세
    is_uptrend = current_price > ma20

    # 현재가가 200일 MA보다 높으면 장기 강세
    is_above_ma200 = current_price > ma200

    if is_above_ma200 and is_uptrend:
        # 강세장
        score = 85 + (current_price - ma200) / ma200 * 10  # MA200 이탈 정도 반영
        score = min(100, score)
        rationale = f"현재가({current_price:.0f}) > MA200({ma200:.0f}), 상승 추세 확인"
        signal = "BUY"
        confidence = 0.85
    elif not is_above_ma200 and not is_uptrend:
        # 약세장
        score = 20 + (ma200 - current_price) / ma200 * 10
        score = max(0, score)
        rationale = f"현재가({current_price:.0f}) < MA200({ma200:.0f}), 하락 추세 확인"
        signal = "SELL"
        confidence = 0.85
    else:
        # 횡보
        score = 50
        rationale = "강세/약세 혼재 → 횡보장"
        signal = "HOLD"
        confidence = 0.6

    return LayerResult(
        layer_name="Market Regime",
        score=score,
        signal=signal,
        confidence=confidence,
        rationale=rationale
    )
