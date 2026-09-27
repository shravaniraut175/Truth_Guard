from backend.core.generator import generate_response
from backend.core.claim_extractor import extract_claims
from backend.core.evidence import verify_claim
from backend.core.judge import judge_claim
from backend.core.fusion import calculate_truth_score
from backend.core.risk import make_risk_decision


# ============================================================
# TEST QUESTION
# ============================================================

QUESTION = (
    "What is the capital of France, and can you provide some historical context "
    "about its significance in European history?"
)


# ============================================================
# MAIN TEST
# ============================================================

def main():

    print("\n" + "=" * 70)
    print("TRUTHGUARD FULL PIPELINE TEST")
    print("=" * 70)

    # --------------------------------------------------------
    # 1. GENERATE INITIAL RESPONSE
    # --------------------------------------------------------

    print("\n[1] GENERATING RESPONSE...")
    print("-" * 70)

    response = generate_response(QUESTION)

    print("\nGenerated Response:")
    print(response)


    # --------------------------------------------------------
    # 2. CLAIM EXTRACTION
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("[2] EXTRACTING CLAIMS...")
    print("-" * 70)

    extraction_result = extract_claims(response)

    claims = extraction_result.claims

    print(f"\nClaims extracted: {len(claims)}")

    for claim in claims:
        print(
            f"\nClaim {claim.id}"
            f"\nType: {claim.type}"
            f"\nText: {claim.text}"
        )


    if not claims:
        print("\nNo claims found.")
        return


    # --------------------------------------------------------
    # 3. VERIFY EACH CLAIM
    # --------------------------------------------------------

    claim_results = []

    evidence_scores = []
    judge_scores = []

    print("\n" + "=" * 70)
    print("[3] VERIFYING CLAIMS")
    print("=" * 70)

    for claim in claims:

        print("\n" + "-" * 70)
        print(f"CLAIM {claim.id}")
        print("-" * 70)

        print(f"Text: {claim.text}")
        print(f"Type: {claim.type}")


        # ====================================================
        # 3A. EVIDENCE VERIFICATION
        # ====================================================

        print("\n[Evidence Verification]")

        try:

            evidence_result = verify_claim(
                claim.text
            )

            print(
                f"Score: {evidence_result['score']}"
            )

            print(
                f"Verdict: {evidence_result['verdict']}"
            )

            print(
                f"Explanation: "
                f"{evidence_result['explanation']}"
            )

            evidence_scores.append(
                evidence_result["score"]
            )

        except Exception as exc:

            print(
                f"Evidence verification FAILED: {exc}"
            )

            evidence_result = None


        # ====================================================
        # 3B. LLM JUDGE
        # ====================================================

        print("\n[LLM Judge]")

        try:

            judge_result = judge_claim(
                claim=claim.text,
                response=response,
                evidence=evidence_result,
            )

            print(
                f"Score: {judge_result['score']}"
            )

            print(
                f"Verdict: {judge_result['verdict']}"
            )

            print(
                f"Explanation: "
                f"{judge_result['explanation']}"
            )

            judge_scores.append(
                judge_result["score"]
            )

        except Exception as exc:

            print(
                f"Judge verification FAILED: {exc}"
            )

            judge_result = None


        # ====================================================
        # 3C. STORE RESULT
        # ====================================================

        claim_results.append({

            "claim": {
                "id": claim.id,
                "text": claim.text,
                "type": claim.type,
            },

            "evidence": evidence_result,

            "judge": judge_result,
        })


    # --------------------------------------------------------
    # 4. CALCULATE OVERALL FUSION
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("[4] CALCULATING FUSION SCORE")
    print("=" * 70)

    if not evidence_scores and not judge_scores:

        print(
            "\nNo verification scores were available."
        )

        return


    evidence_average = (
        sum(evidence_scores) / len(evidence_scores)
        if evidence_scores
        else None
    )

    judge_average = (
        sum(judge_scores) / len(judge_scores)
        if judge_scores
        else None
    )


    print(
        f"\nEvidence Average: "
        f"{evidence_average:.2f}"
        if evidence_average is not None
        else "\nEvidence Average: N/A"
    )

    print(
        f"Judge Average: "
        f"{judge_average:.2f}"
        if judge_average is not None
        else "Judge Average: N/A"
    )


    # --------------------------------------------------------
    # 5. FUSION
    # --------------------------------------------------------

    fusion_result = calculate_truth_score(

        evidence_score=evidence_average,

        judge_score=judge_average,

        # No black-box / white-box in this test.
        blackbox_score=None,

        whitebox_score=None,
    )


    print("\nFusion Result:")

    print(
        f"Truth Score: "
        f"{fusion_result['truth_score']}"
    )

    print(
        f"Hallucination Probability: "
        f"{fusion_result['hallucination_probability']}"
    )

    print(
        f"Confidence Score: "
        f"{fusion_result['confidence_score']}"
    )

    print(
        f"Risk Level: "
        f"{fusion_result['risk_level']}"
    )

    print(
        f"Component Scores: "
        f"{fusion_result['component_scores']}"
    )

    print(
        f"Weights: "
        f"{fusion_result['weights']}"
    )


    # --------------------------------------------------------
    # 6. RISK DECISION
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("[5] RISK DECISION")
    print("=" * 70)

    risk_result = make_risk_decision(

        truth_score=fusion_result["truth_score"],

        hallucination_probability=(
            fusion_result[
                "hallucination_probability"
            ]
        ),

        confidence_score=(
            fusion_result[
                "confidence_score"
            ]
        ),
    )


    print(
        f"\nDecision: "
        f"{risk_result['decision']}"
    )

    print(
        f"Risk Level: "
        f"{risk_result.get('risk_level')}"
    )

    print(
        f"Reason: "
        f"{risk_result.get('reason', 'N/A')}"
    )


    # --------------------------------------------------------
    # 7. FINAL SUMMARY
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("TRUTHGUARD TEST SUMMARY")
    print("=" * 70)

    print(
        f"\nQuestion:\n{QUESTION}"
    )

    print(
        f"\nOriginal Response:\n{response}"
    )

    print(
        f"\nNumber of Claims: {len(claims)}"
    )

    print(
        f"\nTruth Score: "
        f"{fusion_result['truth_score']}"
    )

    print(
        f"Hallucination Probability: "
        f"{fusion_result['hallucination_probability']}"
    )

    print(
        f"Confidence Score: "
        f"{fusion_result['confidence_score']}"
    )

    print(
        f"Risk Level: "
        f"{fusion_result['risk_level']}"
    )

    print(
        f"Decision: "
        f"{risk_result['decision']}"
    )


    # --------------------------------------------------------
    # 8. CLAIM-BY-CLAIM SUMMARY
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("CLAIM-BY-CLAIM RESULTS")
    print("=" * 70)

    for item in claim_results:

        claim_data = item["claim"]

        print("\n" + "-" * 70)

        print(
            f"Claim {claim_data['id']}: "
            f"{claim_data['text']}"
        )

        print(
            f"Type: "
            f"{claim_data['type']}"
        )


        evidence = item["evidence"]

        if evidence:

            print(
                f"\nEvidence:"
                f"\n  Score: {evidence['score']}"
                f"\n  Verdict: {evidence['verdict']}"
            )

        else:

            print(
                "\nEvidence: FAILED"
            )


        judge = item["judge"]

        if judge:

            print(
                f"\nJudge:"
                f"\n  Score: {judge['score']}"
                f"\n  Verdict: {judge['verdict']}"
            )

        else:

            print(
                "\nJudge: FAILED"
            )


    print("\n" + "=" * 70)
    print("FULL PIPELINE TEST COMPLETED")
    print("=" * 70)


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()