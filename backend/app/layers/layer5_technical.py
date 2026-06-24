import pandas as pd
import pandas_ta as ta
from .base import LayerResult


def analyze_technical(df: pd.DataFrame) -> LayerResult:
    """
    Layer 5: Technical Indicators (기술적 지표)

    RSI, MACD, EMA20/50/200을 활용한 기술적 분석
    """
    if df.empty or len(df) < 50:
        return LayerResult(
            layer_name="Technical Indicators",
            score=50,
            signal="HOLD",
            confidence=0.3,
            rationale="충분한 데이터 부재"
        )

    df = df.copy()

    # 지표 계산
    # RSI (14)
    rsi = ta.rsi(df['Close'], length=14)
    current_rsi = rsi.iloc[-1] if not rsi.empty else 50

    # MACD
    macd_result = ta.macd(df['Close'], fast=12, slow=26, signal=9)
    if macd_result is not None and not macd_result.empty:
        macd = macd_result.iloc[:, 0]  # MACD line
        macd_signal = macd_result.iloc[:, 1]  # Signal line
        current_macd = macd.iloc[-1] if not macd.empty else 0
        current_signal = macd_signal.iloc[-1] if not macd_signal.empty else 0
        macd_histogram = current_macd - current_signal
    else:
        macd_histogram = 0

    # EMA (20, 50, 200)
    ema20 = ta.ema(df['Close'], length=20)
    ema50 = ta.ema(df['Close'], length=50)
    ema200 = ta.ema(df['Close'], length=200)

    current_price = df['Close'].iloc[-1]
    current_ema20 = ema20.iloc[-1] if not ema20.empty else current_price
    current_ema50 = ema50.iloc[-1] if not ema50.empty else current_price
    current_ema200 = ema200.iloc[-1] if not ema200.empty else current_price

    # 점수 계산
    score = 50
    signal = "HOLD"
    confidence = 0.6
    rationale_list = []

    # RSI 신호
    if current_rsi > 70:
        score -= 15
        signal = "SELL"
        rationale_list.append(f"RSI({current_rsi:.1f}) > 70 (과매수)")
    elif current_rsi < 30:
        score += 15
        signal = "BUY"
        rationale_list.append(f"RSI({current_rsi:.1f}) < 30 (과매도)")
    else:
        rationale_list.append(f"RSI({current_rsi:.1f}) (중립)")

    # MACD 신호
    if macd_histogram > 0:
        score += 10
        rationale_list.append("MACD 양수 (상승 추세)")
    else:
        score -= 10
        rationale_list.append("MACD 음수 (하락 추세)")

    # 이동평균 정렬 (20 > 50 > 200 → 강세)
    if current_ema20 > current_ema50 > current_ema200:
        score += 15
        signal = "BUY"
        rationale_list.append("EMA 정렬 (20 > 50 > 200)")
        confidence = 0.8
    elif current_ema20 < current_ema50 < current_ema200:
        score -= 15
        signal = "SELL"
        rationale_list.append("EMA 역정렬 (20 < 50 < 200)")
        confidence = 0.8
    else:
        rationale_list.append("EMA 혼합 신호")

    # 현재가가 EMA20 위에 있으면 단기 강세
    if current_price > current_ema20:
        score += 5
        rationale_list.append(f"현재가 > EMA20 (단기 강세)")
    else:
        score -= 5
        rationale_list.append(f"현재가 < EMA20 (단기 약세)")

    score = max(0, min(100, score))

    return LayerResult(
        layer_name="Technical Indicators",
        score=score,
        signal=signal,
        confidence=confidence,
        rationale=", ".join(rationale_list)
    )
