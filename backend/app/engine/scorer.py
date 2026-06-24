from typing import dict, list
from ..layers.base import LayerResult


DEFAULT_WEIGHTS = {
    "Layer 1: Market Regime": 0.15,
    "Layer 2: Smart Money": 0.15,
    "Layer 3: Market Structure": 0.15,
    "Layer 4: Volume Profile": 0.15,
    "Layer 5: Technical Indicators": 0.10,
    # Phase 2에서 추가
    "Layer 6: Candlestick Analysis": 0.10,
    "Layer 7: Chart Pattern Recognition": 0.05,
    "Layer 8: Sector Rotation": 0.05,
    "Layer 9: Fundamental Analysis": 0.05,
    "Layer 10: News Sentiment": 0.03,
    "Layer 11: Macro & Global": 0.02,
}


def calculate_score(
    layer_results: list[LayerResult],
    weights: dict = None
) -> dict:
    """
    11개 레이어의 점수를 가중치에 따라 종합하여 최종 점수 계산

    Args:
        layer_results: [LayerResult, ...] 리스트
        weights: {"Layer 1: ...": 0.15, ...} 딕셔너리 (기본값: DEFAULT_WEIGHTS)

    Returns:
        {
            "total_score": 85,
            "signal": "BUY",
            "confidence": 0.82,
            "buy_prices": [80000, 78000, 75000],  # Phase 2에서 추가
            "sell_prices": [88000, 92000, 98000],  # Phase 2에서 추가
            "layers": [...]
        }
    """
    if weights is None:
        weights = DEFAULT_WEIGHTS

    if not layer_results:
        return {
            "total_score": 50,
            "signal": "HOLD",
            "confidence": 0.0,
            "layers": []
        }

    # 점수와 신뢰도 가중치 계산
    total_weighted_score = 0
    total_confidence = 0
    total_weight = 0

    layer_details = []

    for result in layer_results:
        # 레이어 이름 매핑
        weight = weights.get(result.layer_name, 0)
        if weight == 0:
            continue

        total_weighted_score += result.score * weight
        total_confidence += result.confidence * weight
        total_weight += weight

        layer_details.append({
            "layer_name": result.layer_name,
            "score": round(result.score, 2),
            "signal": result.signal,
            "confidence": round(result.confidence, 4),
            "rationale": result.rationale,
            "weight": weight
        })

    # 최종 점수 정규화
    total_score = total_weighted_score / total_weight if total_weight > 0 else 50
    total_score = max(0, min(100, total_score))

    # 신뢰도
    avg_confidence = total_confidence / total_weight if total_weight > 0 else 0.5
    avg_confidence = max(0, min(1, avg_confidence))

    # 통합 신호 결정 (최종 점수 기반)
    if total_score >= 70:
        signal = "BUY"
    elif total_score <= 30:
        signal = "SELL"
    else:
        signal = "HOLD"

    # 60% 이하 신뢰도 경고
    warning = avg_confidence < 0.6

    return {
        "total_score": round(total_score, 2),
        "signal": signal,
        "confidence": round(avg_confidence, 4),
        "warning": warning,
        "warning_message": "신뢰도 60% 이하 - 참고용으로만 사용하세요" if warning else None,
        "layers": layer_details
    }
