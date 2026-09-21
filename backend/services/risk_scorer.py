import re
import os
import logging

logger = logging.getLogger(__name__)

# High-risk signal words — expand this list as needed
HIGH_RISK_KEYWORDS = [
    "fine", "penalty", "sanction", "criminal", "imprisonment", "prohibit",
    "mandatory", "must", "shall", "required", "obligation", "breach",
    "violation", "infringement", "liability", "enforcement", "immediate",
    "ban", "suspend", "revoke", "terminate", "injunction",
]

MEDIUM_RISK_KEYWORDS = [
    "audit", "review", "assess", "report", "disclose", "notify", "implement",
    "establish", "maintain", "ensure", "comply", "compliance", "document",
    "record", "monitor", "inspect", "certify", "approve", "deadline",
]

LOW_RISK_KEYWORDS = [
    "recommend", "should", "consider", "encourage", "may", "optional",
    "guideline", "best practice", "suggest", "advise", "guidance",
]

def _rule_based_score(text: str) -> int:
    """Fast heuristic scoring. No model needed."""
    text_lower = text.lower()
    words = re.findall(r'\b\w+\b', text_lower)
    word_count = max(len(words), 1)

    high_hits = sum(1 for w in HIGH_RISK_KEYWORDS if w in text_lower)
    medium_hits = sum(1 for w in MEDIUM_RISK_KEYWORDS if w in text_lower)
    low_hits = sum(1 for w in LOW_RISK_KEYWORDS if w in text_lower)

    # Density-based scoring (hits per 100 words)
    high_density = (high_hits / word_count) * 100
    medium_density = (medium_hits / word_count) * 100

    # Check for fine amounts (strong HIGH signal)
    fine_pattern = re.search(
        r'(€|£|\$|usd|eur)\s*[\d,]+\s*(million|billion|thousand)?|'
        r'[\d,]+\s*%(.*?)(annual|revenue|turnover)',
        text_lower
    )
    has_fine_amount = bool(fine_pattern)

    # Scoring logic
    if has_fine_amount or high_density > 2.0:
        base = 75
    elif high_hits >= 3 or medium_density > 3.0:
        base = 50
    elif medium_hits >= 2:
        base = 35
    else:
        base = 15

    # Modifiers
    score = base
    score += min(high_hits * 3, 20)
    score += min(medium_hits * 1, 10)
    score -= min(low_hits * 2, 10)
    score += 10 if has_fine_amount else 0

    return max(0, min(100, score))


def _load_ml_model():
    """Load trained sklearn model if it exists."""
    # Updated to point to our custom trained model from Phase 3
    model_path = "/home/perseuskyogre/Projects/CodeWizards/backend/ml/risk_scorer_v1.joblib"
    if os.path.exists(model_path):
        import joblib
        logger.info(f"✅ Loading custom ML Risk Scorer from {model_path}")
        return joblib.load(model_path)
    return None

_ml_model = None
_ml_model_checked = False

def score_regulation(text: str) -> int:
    """
    Primary entry point.
    Uses ML model if available, falls back to rule-based.
    """
    global _ml_model, _ml_model_checked

    if not _ml_model_checked:
        _ml_model = _load_ml_model()
        _ml_model_checked = True

    if _ml_model is not None:
        try:
            proba = _ml_model.predict_proba([text])[0]   # [low, medium, high]
            # Convert probability to 0-100 score
            score = int(proba[1] * 40 + proba[2] * 80)
            return max(0, min(100, score))
        except Exception as e:
            logger.warning(f"ML model failed, using rule-based: {e}")

    return _rule_based_score(text)


def score_to_level(score: int) -> str:
    if score >= 70:
        return "HIGH"
    elif score >= 40:
        return "MEDIUM"
    return "LOW"


class RiskScorer:
    def predict(self, text: str) -> int:
        return score_regulation(text)

    def to_level(self, score: int) -> str:
        return score_to_level(score)

risk_scorer = RiskScorer()
