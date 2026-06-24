import pandas as pd
from .base import LayerResult


def analyze_smart_money(df: pd.DataFrame) -> LayerResult:
    """
    Layer 2: Smart Money (수급 분석)

    MVP에서는 거래량과 가격 변화를 기반으로 수급 강도 분석
    - 상승 시 거래량 증가 → 매수 수급 강함
    - 하락 시 거래량 감소 → 매도 수급 약함
    - 역학관계 분석
    """
    if df.empty or len(df) < 20:
        return LayerResult(
            layer_name="Smart Money",
            score=50,
            signal="HOLD",
            confidence=0.3,
            rationale="충분한 데이터 부재"
        )

    df = df.copy()

    # 최근 20일 데이터 분석
    recent_20 = df.tail(20)
    price_change = recent_20['Close'].iloc[-1] - recent_20['Close'].iloc[0]
    avg_volume_20 = recent_20['Volume'].mean()
    current_volume = recent_20['Volume'].iloc[-1]
    volume_ratio = current_volume / avg_volume_20 if avg_volume_20 > 0 else 1

    # 최근 5일 데이터 분석
    recent_5 = df.tail(5)
    price_5 = recent_5['Close'].iloc[-1] - recent_5['Close'].iloc[0]
    avg_volume_5 = recent_5['Volume'].mean()
    current_volume_5 = recent_5['Volume'].iloc[-1]
    volume_ratio_5 = current_volume_5 / avg_volume_5 if avg_volume_5 > 0 else 1

    # 점수 계산
    score = 50
    signal = "HOLD"
    confidence = 0.6
    rationale_list = []

    # 상승 추세 + 거래량 증가 → 매수 수급 강함
    if price_change > 0 and volume_ratio > 1.2:
        score = 80
        signal = "BUY"
        confidence = 0.8
        rationale_list.append("상승 추세 + 거래량 증가 (매수 수급 강함)")

    # 최근 5일 급등락 + 거래량 폭증
    elif price_5 > 0 and volume_ratio_5 > 1.5:
        score = 75
        signal = "BUY"
        confidence = 0.75
        rationale_list.append("최근 급등 + 거래량 폭증")

    # 하락 추세 + 거래량 감소 → 약세
    elif price_change < 0 and volume_ratio < 0.8:
        score = 30
        signal = "SELL"
        confidence = 0.75
        rationale_list.append("하락 추세 + 거래량 감소 (약세 신호)")

    # 상승했지만 거래량 저조 → 약한 신호
    elif price_change > 0 and volume_ratio < 1.0:
        score = 55
        signal = "HOLD"
        confidence = 0.6
        rationale_list.append("상승하나 거래량 저조 (약한 신호)")

    else:
        rationale_list.append("안정적인 거래량 + 혼합 신호")

    rationale = ", ".join(rationale_list) if rationale_list else "중립"

    return LayerResult(
        layer_name="Smart Money",
        score=score,
        signal=signal,
        confidence=confidence,
        rationale=rationale
    )
