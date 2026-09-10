from backend.core.generator import generate_response
from backend.core.query_analyzer import analyze_query
from backend.core.router import get_verification_plan
from backend.core.fusion import calculate_truth_score
from backend.core.risk import make_risk_decision


def run_truthguard(question: str) -> dict:

    if not question or not question.strip():
        raise ValueError("Question cannot be empty.")

    question = question.strip()

    # ==================================================
    # 1. QUERY ANALYSIS
    # ==================================================

    query_analysis = analyze_query(question)

    complexity_level = query_analysis["level"]

    # ==================================================
    # 2. SELECT VERIFICATION PLAN
    # ==================================================

    verification_plan = get_verification_plan(
        complexity_level
    )

    modules_used = []

    # ==================================================
    # 3. INITIAL RESPONSE
    # ==================================================

    original_response = generate_response(question)

    modules_used.append("Initial Response")

    # ==================================================
    # 4. LOW / MEDIUM / HIGH VERIFICATION
    # ==================================================

    evidence_result = None
    blackbox_result = None
    judge_result = None
    whitebox_result = None
    claim_results = []

    # --------------------------------------------------
    # LOW
    # --------------------------------------------------

    if complexity_level == "LOW":

        # Quick Evidence Check
        if verification_plan["evidence"]:

            from backend.core.evidence import verify_claim

            evidence_result = verify_claim(
                original_response
            )

            modules_used.append(
                "Quick Evidence Check"
            )

        # Lightweight Judge
        if verification_plan["judge"]:

            from backend.core.judge import judge_claim

            judge_result = judge_claim(
                original_response,
                original_response
            )

            modules_used.append(
                "Lightweight LLM Judge"
            )

        fusion_result = calculate_truth_score(
            evidence_score=(
                evidence_result["score"]
                if evidence_result
                else None
            ),

            judge_score=(
                judge_result["score"]
                if judge_result
                else None
            ),
        )

    # --------------------------------------------------
    # MEDIUM / HIGH
    # --------------------------------------------------

    else:

        # Claim Extraction
        if verification_plan["claim_extraction"]:

            from backend.core.claim_extractor import extract_claims

            extraction_result = extract_claims(
                original_response
            )

            claims = extraction_result.claims

            modules_used.append(
                "Claim Extraction"
            )

        else:
            claims = []

        # ----------------------------------------------
        # Analyze each claim
        # ----------------------------------------------

        for claim in claims:

            claim_text = claim.text

            current = {
                "claim": {
                    "id": claim.id,
                    "text": claim.text,
                    "type": claim.type,
                }
            }

            # Evidence
            if verification_plan["evidence"]:

                from backend.core.evidence import verify_claim

                evidence = verify_claim(
                    claim_text
                )

                current["evidence"] = evidence

            # Black-box
            if verification_plan["blackbox"]:

                from backend.core.blackbox import blackbox_score

                blackbox = blackbox_score(
                    question
                )

                current["blackbox"] = blackbox

            # Judge
            if verification_plan["judge"]:

                from backend.core.judge import judge_claim

                judge = judge_claim(
                    claim_text,
                    original_response
                )

                current["judge"] = judge

            # White-box ONLY for HIGH
            if verification_plan["whitebox"]:

                from backend.core.whitebox import calculate_whitebox_score

                whitebox = calculate_whitebox_score(
                    claim_text
                )

                current["whitebox"] = whitebox

            # ------------------------------------------
            # Claim-level fusion
            # ------------------------------------------

            fusion = calculate_truth_score(
                evidence_score=(
                    current["evidence"]["score"]
                    if "evidence" in current
                    else None
                ),

                blackbox_score=(
                    current["blackbox"]["consistency_score"]
                    if "blackbox" in current
                    else None
                ),

                judge_score=(
                    current["judge"]["score"]
                    if "judge" in current
                    else None
                ),

                whitebox_score=(
                    current["whitebox"]["whitebox_score"]
                    if "whitebox" in current
                    else None
                ),
            )

            current["fusion"] = fusion

            claim_results.append(current)

        # ----------------------------------------------
        # Module-level fallback
        # ----------------------------------------------

        if not claim_results:

            raise RuntimeError(
                "No claims were available for verification."
            )

        # ----------------------------------------------
        # Overall scores
        # ----------------------------------------------

        truth_scores = [
            claim["fusion"]["truth_score"]
            for claim in claim_results
        ]

        hallucination_scores = [
            claim["fusion"]["hallucination_probability"]
            for claim in claim_results
        ]

        confidence_scores = [
            claim["fusion"]["confidence_score"]
            for claim in claim_results
        ]

        overall_truth_score = (
            sum(truth_scores)
            / len(truth_scores)
        )

        overall_hallucination_probability = (
            sum(hallucination_scores)
            / len(hallucination_scores)
        )

        overall_confidence_score = (
            sum(confidence_scores)
            / len(confidence_scores)
        )

        fusion_result = {
            "truth_score": round(
                overall_truth_score,
                2
            ),

            "hallucination_probability": round(
                overall_hallucination_probability,
                2
            ),

            "confidence_score": round(
                overall_confidence_score,
                2
            ),

            "risk_level": (
                "LOW"
                if overall_hallucination_probability < 20
                else
                "MEDIUM"
                if overall_hallucination_probability <= 60
                else
                "HIGH"
            ),
        }

    # ==================================================
    # 5. RISK DECISION
    # ==================================================

    risk_result = make_risk_decision(
        truth_score=fusion_result["truth_score"],

        hallucination_probability=(
            fusion_result[
                "hallucination_probability"
            ]
        ),

        confidence_score=(
            fusion_result["confidence_score"]
        ),
    )

    # ==================================================
    # 6. REGENERATION
    # ==================================================

    regeneration_result = None
    final_verification_result = None

    final_response = original_response

    if risk_result["decision"] == "REGENERATE":

        from backend.core.regenerator import regenerate_response

        verification_context = ""

        for claim in claim_results:

            verification_context += (
                f"Claim: "
                f"{claim['claim']['text']}\n"
            )

            if "evidence" in claim:

                verification_context += (
                    f"Evidence score: "
                    f"{claim['evidence']['score']}\n"
                )

                verification_context += (
                    f"Verdict: "
                    f"{claim['evidence']['verdict']}\n"
                )

                verification_context += (
                    f"Explanation: "
                    f"{claim['evidence']['explanation']}\n\n"
                )

        regenerated_response = regenerate_response(
            question=question,
            original_response=original_response,
            verification_context=verification_context,
        )

        regeneration_result = {
            "original_response": original_response,
            "regenerated_response": regenerated_response,
        }

        # ==================================================
        # 7. FINAL VERIFICATION
        # ==================================================

        from backend.core.final_verifier import final_verify

        final_verification_result = final_verify(
            question=question,
            response=regenerated_response,
        )

        final_response = regenerated_response

    # ==================================================
    # 8. FINAL RESULT
    # ==================================================

    return {
        "question": question,

        "query_analysis": query_analysis,

        "verification_plan": verification_plan,

        "modules_used": modules_used,

        "original_response": original_response,

        "claims": claim_results,

        "overall_scores": {
            "truth_score": fusion_result[
                "truth_score"
            ],

            "hallucination_probability": fusion_result[
                "hallucination_probability"
            ],

            "confidence_score": fusion_result[
                "confidence_score"
            ],
        },

        "risk_decision": risk_result,

        "regeneration": regeneration_result,

        "final_verification": final_verification_result,

        "final_response": final_response,
    }