
from backend.core.generator import generate_response
from backend.core.claim_extractor import extract_claims
from backend.core.evidence import verify_claim
from backend.core.judge import judge_claim
from backend.core.fusion import calculate_truth_score
from backend.core.risk import make_risk_decision


def run_truthguard(question: str) -> dict:
    """Run TruthGuard and return structured results for the UI."""

    if not question or not question.strip():
        raise ValueError("Please enter a question.")

    question = question.strip()

    # Step 1: Generate response
    original_response = generate_response(question)

    # Step 2: Extract claims
    extraction_result = extract_claims(original_response)
    claims = extraction_result.claims

    results = {
        "question": question,
        "original_response": original_response,
        "claims": [],
        "evidence_average": None,
        "judge_average": None,
        "fusion": None,
        "risk": None,
        "errors": [],
    }

    if not claims:
        results["errors"].append(
            "No claims were extracted from the generated response."
        )
        return results

    evidence_scores = []
    judge_scores = []

    # Steps 3 and 4: Verify every claim
    for claim in claims:
        evidence_result = None
        judge_result = None

        try:
            evidence_result = verify_claim(claim.text)

            if evidence_result.get("score") is not None:
                evidence_scores.append(
                    float(evidence_result["score"])
                )

        except Exception as exc:
            results["errors"].append(
                f"Evidence verification failed for claim "
                f"{claim.id}: {exc}"
            )

        try:
            judge_result = judge_claim(
                claim=claim.text,
                response=original_response,
                evidence=evidence_result,
            )

            if judge_result.get("score") is not None:
                judge_scores.append(
                    float(judge_result["score"])
                )

        except Exception as exc:
            results["errors"].append(
                f"LLM judge failed for claim {claim.id}: {exc}"
            )

        results["claims"].append({
            "id": claim.id,
            "text": claim.text,
            "type": claim.type,
            "evidence": evidence_result,
            "judge": judge_result,
        })

    # Step 5: Average available scores
    evidence_average = (
        sum(evidence_scores) / len(evidence_scores)
        if evidence_scores else None
    )

    judge_average = (
        sum(judge_scores) / len(judge_scores)
        if judge_scores else None
    )

    results["evidence_average"] = evidence_average
    results["judge_average"] = judge_average

    # Do not silently replace missing scores with zero.
    if evidence_average is None or judge_average is None:
        results["errors"].append(
            "Fusion was skipped because one or more required "
            "average scores are unavailable."
        )
        return results

    
    # Step 6: Score fusion using all available scores.
    # Missing scores remain None; they are never replaced with zero.
    try:
        fusion_result = calculate_truth_score(
            evidence_score=evidence_average,
            judge_score=judge_average,
        )

        results["fusion"] = fusion_result

        if fusion_result["truth_score"] is None:
            results["errors"].append(
                "Truth Score unavailable: no verification module "
                "produced a valid score."
            )
            return results

        # Step 7: Risk decision
        risk_result = make_risk_decision(
            truth_score=fusion_result["truth_score"],
            hallucination_probability=(
                fusion_result["hallucination_probability"]
            ),
            confidence_score=fusion_result["confidence_score"],
        )

        results["risk"] = risk_result

        # Explain when the result uses incomplete verification.
        if evidence_average is None:
            results["errors"].append(
                "Evidence verification was unavailable. "
                "The Truth Score uses the remaining valid modules."
            )

        if judge_average is None:
            results["errors"].append(
                "Judge verification was unavailable. "
                "The Truth Score uses the remaining valid modules."
            )

    except Exception as exc:
        results["errors"].append(
            f"Score fusion or risk calculation failed: {exc}"
        )

    return results

