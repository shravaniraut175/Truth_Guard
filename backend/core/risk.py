def make_risk_decision(
    truth_score: float,
    hallucination_probability: float,
    confidence_score: float,
) -> dict:

    # High hallucination probability → regenerate
    if hallucination_probability > 60:
        decision = "REGENERATE"
        reason = "High hallucination risk detected."

    # Medium risk or low confidence → review
    elif hallucination_probability >= 20 or confidence_score < 60:
        decision = "REVIEW"
        reason = "The response has moderate risk or insufficient confidence."

    # Low risk + good confidence → accept
    else:
        decision = "ACCEPT"
        reason = "The response has low hallucination risk and sufficient confidence."

    return {
        "decision": decision,
        "reason": reason,
        "truth_score": round(truth_score, 2),
        "hallucination_probability": round(hallucination_probability, 2),
        "confidence_score": round(confidence_score, 2),
    }