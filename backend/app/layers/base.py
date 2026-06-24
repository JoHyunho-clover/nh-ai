from dataclasses import dataclass


@dataclass
class LayerResult:
    """각 분석 레이어의 결과"""
    layer_name: str
    score: float         # 0~100
    signal: str          # BUY | SELL | HOLD
    confidence: float    # 0~1
    rationale: str

    def to_dict(self) -> dict:
        return {
            "layer_name": self.layer_name,
            "score": round(self.score, 2),
            "signal": self.signal,
            "confidence": round(self.confidence, 4),
            "rationale": self.rationale
        }
