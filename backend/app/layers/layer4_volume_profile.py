import pandas as pd
from .base import LayerResult


def analyze_volume_profile(df: pd.DataFrame) -> LayerResult:
    """
    Layer 4: Volume Profile (거래량 프로파일)

    가격 구간별 거래량을 분석하여 주요 거래 가격 영역(POC)을 파악
    현재가가 고거래량 구간에 있으면 강한 지지/저항이 될 가능성
    """
    if df.empty or len(df) < 20:
        return LayerResult(
            layer_name="Volume Profile",
            score=50,
            signal="HOLD",
            confidence=0.3,
            rationale="충분한 데이터 부재"
        )

    df = df.copy()
    recent = df.tail(60)  # 최근 60거래일

    current_price = recent['Close'].iloc[-1]
    current_volume = recent['Volume'].iloc[-1]
    avg_volume = recent['Volume'].mean()

    # 가격대별 거래량 구간 분석
    price_range = recent['High'].max() - recent['Low'].min()
    num_bins = 20
    bin_size = price_range / num_bins if price_range > 0 else 1

    # 각 가격 구간의 평균 거래량 계산
    bins = pd.cut(
        (recent['High'] + recent['Low']) / 2,
        bins=num_bins,
        labels=False
    )
    volume_by_bin = recent.groupby(bins)['Volume'].mean()

    if not volume_by_bin.empty:
        # POC (Point of Control): 가장 높은 거래량 구간
        poc_bin = volume_by_bin.idxmax()
        poc_price = recent['Low'].min() + (poc_bin + 0.5) * bin_size

        # 현재가와 POC의 거리
        distance_to_poc = abs(current_price - poc_price)
        normalized_distance = distance_to_poc / price_range if price_range > 0 else 0

        # 거래량 강도
        volume_strength = min(100, (current_volume / avg_volume) * 50) if avg_volume > 0 else 50
    else:
        poc_price = current_price
        normalized_distance = 0.5
        volume_strength = 50

    # 스코어링
    score = 50
    signal = "HOLD"
    confidence = 0.6

    # POC에 가까우면 지지/저항이 강함
    if normalized_distance < 0.1:
        # POC 근처 → 강한 지지/저항
        score = 70
        if current_volume > avg_volume * 1.2:
            signal = "BUY"
            confidence = 0.75
            rationale = f"POC({poc_price:.0f}) 근처, 높은 거래량 확인"
        else:
            signal = "HOLD"
            confidence = 0.7
            rationale = f"POC({poc_price:.0f}) 근처, 강한 거래량 수준"
    elif normalized_distance < 0.3:
        # POC에서 약간 떨어짐
        score = 55 + volume_strength * 0.2
        rationale = f"POC({poc_price:.0f})에서 약간 이격"
    else:
        # POC에서 멀어짐 → 약한 거래량 영역
        if current_volume > avg_volume * 1.3:
            # 하지만 거래량이 높음
            score = 60
            signal = "BUY"
            confidence = 0.65
            rationale = "POC 이탈 구간, 거래량 증가"
        else:
            score = 40
            signal = "SELL"
            confidence = 0.6
            rationale = f"POC에서 멀어짐, 거래량 약함"

    return LayerResult(
        layer_name="Volume Profile",
        score=score,
        signal=signal,
        confidence=confidence,
        rationale=rationale
    )
