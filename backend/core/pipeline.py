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
    original_response = generate_response(question)

    if not isinstance(original_response, str):
        original_response = str(original_response)

    extraction_result = extract_claims(original_response)
    claims = getattr(extraction_result, "claims", None) or []

    results = {
        "question": question,
        "original_response": original_response,
        "final_response": original_response,
        "claims": [],
        "evidence_average": None,
        "judge_average": None,
        "fusion": None,
        "risk": None,
        "component_results": {},
        "final_verification": None,
        "regeneration": None,
        "errors": [],
    }

    if not claims:
        results["errors"].append(
            "No claims were extracted from the generated response."
        )
        return results

    evidence_scores = []
    judge_scores = []

    for claim in claims:
        claim_text = getattr(claim, "text", str(claim))
        claim_id = getattr(claim, "id", len(results["claims"]) + 1)
        claim_type = getattr(claim, "type", "unknown")

        evidence_result = None
        judge_result = None

        # Evidence verification
        try:
            evidence_result = verify_claim(claim_text)

            if not isinstance(evidence_result, dict):
                raise TypeError(
                    "Evidence verifier did not return a dictionary."
                )

            score = evidence_result.get("score")

            if score is not None:
                score = float(score)
                if 0 <= score <= 100:
                    evidence_scores.append(score)
                else:
                    results["errors"].append(
                        f"Evidence score outside 0-100 for claim {claim_id}."
                    )
                    evidence_result["score"] = None

        except Exception as exc:
            evidence_result = {
                "score": None,
                "verdict": "ERROR",
                "explanation": str(exc),
                "sources": [],
            }
            results["errors"].append(
                f"Evidence verification failed for claim {claim_id}: {exc}"
            )

        # LLM judge
        try:
            judge_result = judge_claim(
                claim=claim_text,
                response=original_response,
                evidence=evidence_result,
            )

            if not isinstance(judge_result, dict):
                raise TypeError(
                    "Judge did not return a dictionary."
                )

            score = judge_result.get("score")

            if score is not None:
                score = float(score)
                if 0 <= score <= 100:
                    judge_scores.append(score)
                else:
                    results["errors"].append(
                        f"Judge score outside 0-100 for claim {claim_id}."
                    )
                    judge_result["score"] = None

        except Exception as exc:
            judge_result = {
                "score": None,
                "verdict": "ERROR",
                "explanation": str(exc),
            }
            results["errors"].append(
                f"Judge failed for claim {claim_id}: {exc}"
            )

        results["claims"].append({
            "claim": {
                "id": claim_id,
                "text": claim_text,
                "type": claim_type,
            },
            "evidence": evidence_result,
            "judge": judge_result,
        })

    # Calculate averages using only valid scores.
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
    results["component_results"] = {
        "evidence_average": evidence_average,
        "judge_average": judge_average,
        "claims_extracted": len(claims),
        "evidence_scored_claims": len(evidence_scores),
        "judge_scored_claims": len(judge_scores),
    }

    # Never convert a missing score to zero.
    if evidence_average is None and judge_average is None:
        results["fusion"] = {
            "truth_score": None,
            "hallucination_probability": None,
            "confidence_score": None,
            "risk_level": "UNKNOWN",
            "component_scores": {},
            "weights": {},
        }
        results["risk"] = {
            "decision": "REVIEW",
            "risk_level": "UNKNOWN",
            "reason": "No valid evidence or judge scores were available.",
        }
        results["errors"].append(
            "Fusion unavailable: both verification modules lack valid scores."
        )
        return results

    # Pass the actual values, including None, to fusion.
    # calculate_truth_score must support missing component scores.
    try:
        fusion_result = calculate_truth_score(
            evidence_score=evidence_average,
            judge_score=judge_average,
        )

        results["fusion"] = fusion_result

        # A single available component is not enough to claim full coverage.
        if evidence_average is None or judge_average is None:
            results["errors"].append(
                "Partial analysis: one verification module returned no "
                "valid average score. Interpret the final metrics cautiously."
            )

        if fusion_result.get("truth_score") is not None:
            results["risk"] = make_risk_decision(
                truth_score=fusion_result["truth_score"],
                hallucination_probability=fusion_result.get(
                    "hallucination_probability"
                ),
                confidence_score=fusion_result.get("confidence_score"),
            )
        else:
            results["risk"] = {
                "decision": "REVIEW",
                "risk_level": "UNKNOWN",
                "reason": "Fusion did not produce a valid truth score.",
            }

    except Exception as exc:
        results["fusion"] = {
            "truth_score": None,
            "hallucination_probability": None,
            "confidence_score": None,
            "risk_level": "UNKNOWN",
            "component_scores": {},
            "weights": {},
        }
        results["risk"] = {
            "decision": "REVIEW",
            "risk_level": "UNKNOWN",
            "reason": f"Score fusion failed: {exc}",
        }
        results["errors"].append(
            f"Fusion failed: {exc}. Check backend/core/fusion.py."
        )

    return results


def main():
    """Optional terminal runner, using the same function as the API."""
    question = input("\nEnter a question for TruthGuard: ").strip()

    try:
        result = run_truthguard(question)
    except Exception as exc:
        print(f"\nTruthGuard failed: {exc}")
        return

    print("\n" + "=" * 70)
    print("TRUTHGUARD END-TO-END TEST")
    print("=" * 70)
    print("\nQUESTION:\n", result["question"])
    print("\nORIGINAL RESPONSE:\n", result["original_response"])
    print(f"\nCLAIMS EXTRACTED: {len(result['claims'])}")

    for item in result["claims"]:
        claim = item["claim"]
        print(f"\nClaim {claim['id']}: {claim['text']}")
        print("Evidence:", item["evidence"])
        print("Judge:", item["judge"])

    print("\nEVIDENCE AVERAGE:", result["evidence_average"])
    print("JUDGE AVERAGE:", result["judge_average"])
    print("FUSION:", result["fusion"])
    print("RISK:", result["risk"])
    print("\nTEST COMPLETED")


if __name__ == "__main__":
    main()
