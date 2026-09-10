from backend.core.generator import generate_response
from backend.core.query_analyzer import analyze_query
from backend.core.router import get_verification_plan
from backend.core.fusion import calculate_truth_score
from backend.core.risk import make_risk_decision


def _average(values):
    if not values:
        raise ValueError("Cannot calculate an average from an empty list.")
    return sum(values) / len(values)


def _overall_fusion(evidence_scores, blackbox_score=None, judge_scores=None,
                    whitebox_scores=None):
    return calculate_truth_score(
        evidence_score=_average(evidence_scores) if evidence_scores else None,
        blackbox_score=blackbox_score,
        judge_score=_average(judge_scores) if judge_scores else None,
        whitebox_score=_average(whitebox_scores) if whitebox_scores else None,
    )


def run_truthguard(question: str) -> dict:
    if not question or not question.strip():
        raise ValueError("Question cannot be empty.")

    question = question.strip()

    # 1. Analyze question and select adaptive verification route.
    query_analysis = analyze_query(question)
    complexity_level = query_analysis["level"]
    verification_plan = get_verification_plan(complexity_level)

    # 2. Initial answer.
    original_response = generate_response(question)
    modules_used = ["Initial Response"]

    claim_results = []
    regeneration_result = None
    final_verification_result = None
    final_response = original_response

    # ==========================================================
    # LOW: Initial Response -> Quick Evidence -> Light Judge
    # ==========================================================
    if complexity_level == "LOW":
        from backend.core.evidence import verify_claim
        from backend.core.judge import judge_claim

        evidence_result = None
        judge_result = None

        if verification_plan["evidence"]:
            evidence_result = verify_claim(original_response)
            modules_used.append("Quick Evidence Check")

        if verification_plan["judge"]:
            judge_result = judge_claim(
                original_response,
                original_response,
            )
            modules_used.append("Lightweight LLM Judge")

        fusion_result = calculate_truth_score(
            evidence_score=evidence_result["score"] if evidence_result else None,
            judge_score=judge_result["score"] if judge_result else None,
        )

        component_results = {
            "evidence": evidence_result,
            "judge": judge_result,
        }

    # ==========================================================
    # MEDIUM / HIGH:
    # Claim Extraction -> Evidence + Black-Box + Judge
    # HIGH additionally -> White-Box
    # ==========================================================
    else:
        # Claim extraction is required for MEDIUM and HIGH.
        from backend.core.claim_extractor import extract_claims

        extraction_result = extract_claims(original_response)
        claims = extraction_result.claims
        modules_used.append("Claim Extraction")

        if not claims:
            raise RuntimeError("No claims were available for verification.")

        # IMPORTANT: Black-Box runs ONCE for the whole question.
        # It must NOT be placed inside the claim loop.
        blackbox_result = None
        if verification_plan["blackbox"]:
            from backend.core.blackbox import blackbox_score

            blackbox_result = blackbox_score(question)
            modules_used.append("Black-Box UQ")

        evidence_scores = []
        judge_scores = []
        whitebox_scores = []

        # Qwen is imported ONLY when HIGH verification requires it.
        if verification_plan["whitebox"]:
            from backend.core.whitebox import calculate_whitebox_score

        from backend.core.evidence import verify_claim
        from backend.core.judge import judge_claim

        for claim in claims:
            claim_text = claim.text

            current = {
                "claim": {
                    "id": claim.id,
                    "text": claim.text,
                    "type": claim.type,
                }
            }

            # Claim-level Evidence.
            if verification_plan["evidence"]:
                evidence = verify_claim(claim_text)
                current["evidence"] = evidence
                evidence_scores.append(evidence["score"])

            # Claim-level Judge.
            if verification_plan["judge"]:
                judge = judge_claim(
                    claim_text,
                    original_response,
                )
                current["judge"] = judge
                judge_scores.append(judge["score"])

            # HIGH ONLY: claim-level White-Box UQ.
            if verification_plan["whitebox"]:
                whitebox = calculate_whitebox_score(claim_text)
                current["whitebox"] = whitebox
                whitebox_scores.append(whitebox["whitebox_score"])

            # Per-claim fusion excludes Black-Box because Black-Box
            # is a single response-level score.
            current["fusion"] = calculate_truth_score(
                evidence_score=(
                    current["evidence"]["score"]
                    if "evidence" in current else None
                ),
                judge_score=(
                    current["judge"]["score"]
                    if "judge" in current else None
                ),
                whitebox_score=(
                    current["whitebox"]["whitebox_score"]
                    if "whitebox" in current else None
                ),
            )

            claim_results.append(current)

        if verification_plan["evidence"]:
            modules_used.append("Evidence Verification")
        if verification_plan["judge"]:
            modules_used.append("LLM Judge")
        if verification_plan["whitebox"]:
            modules_used.append("White-Box UQ")

        # Correct overall fusion:
        # Evidence 35%, Black-Box 25%, Judge 25%, White-Box 15%.
        # Claim-level scores are averaged first; Black-Box is used once.
        fusion_result = _overall_fusion(
            evidence_scores=evidence_scores,
            blackbox_score=(
                blackbox_result["consistency_score"]
                if blackbox_result else None
            ),
            judge_scores=judge_scores,
            whitebox_scores=whitebox_scores,
        )

        component_results = {
            "blackbox": blackbox_result,
            "evidence_average": (
                round(_average(evidence_scores), 2)
                if evidence_scores else None
            ),
            "judge_average": (
                round(_average(judge_scores), 2)
                if judge_scores else None
            ),
            "whitebox_average": (
                round(_average(whitebox_scores), 2)
                if whitebox_scores else None
            ),
        }

    # ==========================================================
    # Risk Decision
    # ==========================================================
    risk_result = make_risk_decision(
        truth_score=fusion_result["truth_score"],
        hallucination_probability=fusion_result["hallucination_probability"],
        confidence_score=fusion_result["confidence_score"],
    )

    # ==========================================================
    # Regenerate only when risk is HIGH.
    # Then perform final verification.
    # ==========================================================
    if risk_result["decision"] == "REGENERATE":
        from backend.core.regenerator import regenerate_response

        context_parts = []

        if complexity_level == "LOW":
            evidence = component_results.get("evidence")
            judge = component_results.get("judge")

            if evidence:
                context_parts.append(
                    f"Evidence score: {evidence['score']}\n"
                    f"Verdict: {evidence['verdict']}\n"
                    f"Explanation: {evidence['explanation']}"
                )

            if judge:
                context_parts.append(
                    f"Judge score: {judge['score']}\n"
                    f"Verdict: {judge.get('verdict', '')}\n"
                    f"Explanation: {judge.get('explanation', '')}"
                )
        else:
            for item in claim_results:
                parts = [f"Claim: {item['claim']['text']}"]

                if "evidence" in item:
                    parts.extend([
                        f"Evidence score: {item['evidence']['score']}",
                        f"Verdict: {item['evidence']['verdict']}",
                        f"Explanation: {item['evidence']['explanation']}",
                    ])

                if "judge" in item:
                    parts.append(
                        f"Judge score: {item['judge']['score']}"
                    )

                if "whitebox" in item:
                    parts.append(
                        f"White-Box score: "
                        f"{item['whitebox']['whitebox_score']}"
                    )

                context_parts.append("\n".join(parts))

        regenerated_response = regenerate_response(
            question=question,
            original_response=original_response,
            verification_context="\n\n".join(context_parts),
        )

        regeneration_result = {
            "original_response": original_response,
            "regenerated_response": regenerated_response,
        }

        from backend.core.final_verifier import final_verify

        final_verification_result = final_verify(
            question=question,
            response=regenerated_response,
        )
        final_response = regenerated_response

    return {
        "question": question,
        "query_analysis": query_analysis,
        "verification_plan": verification_plan,
        "modules_used": modules_used,
        "original_response": original_response,
        "claims": claim_results,
        "overall_scores": {
            "truth_score": fusion_result["truth_score"],
            "hallucination_probability": fusion_result[
                "hallucination_probability"
            ],
            "confidence_score": fusion_result["confidence_score"],
            "risk_level": fusion_result["risk_level"],
            "component_scores": fusion_result["component_scores"],
            "weights": fusion_result["weights"],
            "modules_used": fusion_result["modules_used"],
        },
        "component_results": component_results,
        "risk_decision": risk_result,
        "regeneration": regeneration_result,
        "final_verification": final_verification_result,
        "final_response": final_response,
    }
