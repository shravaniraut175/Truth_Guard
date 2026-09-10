from statistics import mean, pstdev


DEFAULT_WEIGHTS = {
    "evidence": 0.35,
    "blackbox": 0.25,
    "judge": 0.25,
    "whitebox": 0.15,
}


def validate_score(name: str, score: float):

    if not 0 <= score <= 100:
        raise ValueError(
            f"{name} must be between 0 and 100."
        )


def calculate_truth_score(
    evidence_score=None,
    blackbox_score=None,
    judge_score=None,
    whitebox_score=None,
) -> dict:

    scores = {}
    weights = {}

    if evidence_score is not None:
        validate_score("evidence_score", evidence_score)
        scores["evidence"] = evidence_score
        weights["evidence"] = DEFAULT_WEIGHTS["evidence"]

    if blackbox_score is not None:
        validate_score("blackbox_score", blackbox_score)
        scores["blackbox"] = blackbox_score
        weights["blackbox"] = DEFAULT_WEIGHTS["blackbox"]

    if judge_score is not None:
        validate_score("judge_score", judge_score)
        scores["judge"] = judge_score
        weights["judge"] = DEFAULT_WEIGHTS["judge"]

    if whitebox_score is not None:
        validate_score("whitebox_score", whitebox_score)
        scores["whitebox"] = whitebox_score
        weights["whitebox"] = DEFAULT_WEIGHTS["whitebox"]

    if not scores:
        raise ValueError(
            "At least one verification score is required."
        )

    # Normalize weights because some modules may be skipped.
    total_weight = sum(weights.values())

    normalized_weights = {
        name: weight / total_weight
        for name, weight in weights.items()
    }

    truth_score = sum(
        scores[name] * normalized_weights[name]
        for name in scores
    )

    hallucination_probability = 100 - truth_score

    if hallucination_probability < 20:
        risk_level = "LOW"

    elif hallucination_probability <= 60:
        risk_level = "MEDIUM"

    else:
        risk_level = "HIGH"

    score_values = list(scores.values())

    if len(score_values) == 1:
        confidence_score = score_values[0]

    else:
        average_score = mean(score_values)
        disagreement = pstdev(score_values)

        confidence_score = max(
            0,
            min(100, average_score - disagreement)
        )

    return {
        "truth_score": round(truth_score, 2),

        "hallucination_probability": round(
            hallucination_probability,
            2
        ),

        "confidence_score": round(
            confidence_score,
            2
        ),

        "risk_level": risk_level,

        "component_scores": {
            name: round(score, 2)
            for name, score in scores.items()
        },

        "weights": {
            name: round(weight, 4)
            for name, weight in normalized_weights.items()
        },

        "modules_used": list(scores.keys()),
    }