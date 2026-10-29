from math import isfinite
from statistics import mean, pstdev


DEFAULT_WEIGHTS = {
    "evidence": 0.35,
    "blackbox": 0.25,
    "judge": 0.25,
    "whitebox": 0.15,
}


def validate_score(name: str, score: float) -> None:
    if isinstance(score, bool) or not isinstance(score, (int, float)):
        raise ValueError(f"{name} must be a numeric score from 0 to 100.")
    if not isfinite(float(score)) or not 0 <= score <= 100:
        raise ValueError(f"{name} must be a finite number between 0 and 100.")


def calculate_truth_score(
    evidence_score=None,
    blackbox_score=None,
    judge_score=None,
    whitebox_score=None,
) -> dict:
    supplied = {
        "evidence": evidence_score,
        "blackbox": blackbox_score,
        "judge": judge_score,
        "whitebox": whitebox_score,
    }

    scores = {}
    weights = {}
    for name, score in supplied.items():
        # None means unavailable; do not silently convert it to 0.
        if score is None:
            continue
        validate_score(f"{name}_score", score)
        scores[name] = float(score)
        weights[name] = DEFAULT_WEIGHTS[name]

    if not scores:
        return {
            "truth_score": None,
            "hallucination_probability": None,
            "confidence_score": None,
            "risk_level": "UNKNOWN",
            "component_scores": {},
            "weights": {},
            "modules_used": [],
            "warning": "No valid verification scores were available.",
        }

    total_weight = sum(weights.values())
    normalized_weights = {
        name: weight / total_weight for name, weight in weights.items()
    }
    truth_score = sum(scores[name] * normalized_weights[name] for name in scores)
    hallucination_probability = 100.0 - truth_score

    if hallucination_probability < 20:
        risk_level = "LOW"
    elif hallucination_probability <= 60:
        risk_level = "MEDIUM"
    else:
        risk_level = "HIGH"

    score_values = list(scores.values())
    if len(score_values) == 1:
        # Preserve the existing app contract; this is a proxy, not calibrated confidence.
        confidence_score = score_values[0]
        confidence_note = "Only one verification module produced a score; confidence is a proxy."
    else:
        average_score = mean(score_values)
        disagreement = pstdev(score_values)
        confidence_score = max(0.0, min(100.0, average_score - disagreement))
        confidence_note = None

    result = {
        "truth_score": round(truth_score, 2),
        "hallucination_probability": round(hallucination_probability, 2),
        "confidence_score": round(confidence_score, 2),
        "risk_level": risk_level,
        "component_scores": {name: round(score, 2) for name, score in scores.items()},
        "weights": {name: round(weight, 4) for name, weight in normalized_weights.items()},
        "modules_used": list(scores.keys()),
    }
    if confidence_note:
        result["confidence_note"] = confidence_note
    if len(scores) < len(DEFAULT_WEIGHTS):
        result["warning"] = "Truth Score uses only the available modules; interpret it cautiously."
    return result
