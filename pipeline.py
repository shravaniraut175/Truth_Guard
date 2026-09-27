from backend.core.generator import generate_response
from backend.core.claim_extractor import extract_claims
from backend.core.evidence import verify_claim
from backend.core.judge import judge_claim
from backend.core.fusion import calculate_truth_score
from backend.core.risk import make_risk_decision


def main():

    # =========================================================
    # 1. USER QUESTION
    # =========================================================


    question = input(
        "\nEnter a question for TruthGuard: "
    )
    


    print("\n" + "=" * 70)
    print("TRUTHGUARD END-TO-END TEST")
    print("=" * 70)

    print("\nUSER QUESTION:")
    print(question)


    # =========================================================
    # 2. GENERATE INITIAL RESPONSE
    # =========================================================

    print("\n" + "-" * 70)
    print("1. GENERATING INITIAL RESPONSE")
    print("-" * 70)

    original_response = generate_response(question)

    print("\nGENERATED RESPONSE:")
    print(original_response)


    # =========================================================
    # 3. CLAIM EXTRACTION
    # =========================================================

    print("\n" + "-" * 70)
    print("2. EXTRACTING CLAIMS")
    print("-" * 70)

    extraction_result = extract_claims(original_response)

    claims = extraction_result.claims

    print(f"\nNumber of claims extracted: {len(claims)}")

    for claim in claims:
        print(
            f"\nClaim {claim.id}: "
            f"{claim.text}"
        )
        print(f"Type: {claim.type}")


    if not claims:
        print("\nNo claims found.")
        return


    # =========================================================
    # 4. VERIFY EACH CLAIM
    # =========================================================

    claim_results = []

    evidence_scores = []
    judge_scores = []

    for claim in claims:

        print("\n" + "=" * 70)
        print(f"VERIFYING CLAIM {claim.id}")
        print("=" * 70)

        print("\nCLAIM:")
        print(claim.text)

        # -----------------------------------------------------
        # 4A. EVIDENCE VERIFICATION
        # -----------------------------------------------------

        print("\n" + "-" * 70)
        print("3. EVIDENCE VERIFICATION")
        print("-" * 70)

        try:

            evidence_result = verify_claim(
                claim.text
            )

            print("\nEVIDENCE RESULT:")
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

            print("\nSources:")

            for source in evidence_result.get(
                "sources",
                []
            ):

                print(
                    f"- {source.get('title')}"
                )
                print(
                    f"  {source.get('url')}"
                )

            evidence_scores.append(
                evidence_result["score"]
            )

        except Exception as exc:

            print(
                f"\nEvidence verification failed: {exc}"
            )

            evidence_result = None


        # -----------------------------------------------------
        # 4B. LLM JUDGE
        # -----------------------------------------------------

        print("\n" + "-" * 70)
        print("4. LLM-AS-A-JUDGE")
        print("-" * 70)

        try:

            judge_result = judge_claim(
                claim=claim.text,
                response=original_response,
                evidence=evidence_result,
            )

            print("\nJUDGE RESULT:")

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
                f"\nJudge verification failed: {exc}"
            )

            judge_result = None


        # -----------------------------------------------------
        # 4C. CLAIM RESULT
        # -----------------------------------------------------

        claim_results.append({

            "claim": {
                "id": claim.id,
                "text": claim.text,
                "type": claim.type,
            },

            "evidence": evidence_result,

            "judge": judge_result,

        })


    # =========================================================
    # 5. AVERAGE SCORES
    # =========================================================

    print("\n" + "=" * 70)
    print("5. SCORE FUSION")
    print("=" * 70)

    evidence_average = (
        sum(evidence_scores) /
        len(evidence_scores)
        if evidence_scores
        else None
    )

    judge_average = (
        sum(judge_scores) /
        len(judge_scores)
        if judge_scores
        else None
    )

    print(
        f"\nEvidence Average: "
        f"{evidence_average}"
    )

    print(
        f"Judge Average: "
        f"{judge_average}"
    )


    # =========================================================
    # 6. FUSION
    # =========================================================

    fusion_result = calculate_truth_score(

        evidence_score=evidence_average,

        judge_score=judge_average,

    )


    print("\nFUSION RESULT:")

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


    # =========================================================
    # 7. RISK DECISION
    # =========================================================

    print("\n" + "=" * 70)
    print("6. RISK DECISION")
    print("=" * 70)

    risk_result = make_risk_decision(

        truth_score=fusion_result[
            "truth_score"
        ],

        hallucination_probability=
            fusion_result[
                "hallucination_probability"
            ],

        confidence_score=
            fusion_result[
                "confidence_score"
            ],
    )


    print("\nRISK RESULT:")

    print(
        f"Decision: "
        f"{risk_result['decision']}"
    )

    print(
        f"Risk Level: "
        f"{risk_result.get('risk_level')}"
    )

    print(
        f"Reason: "
        f"{risk_result.get('reason', '')}"
    )


    # =========================================================
    # 8. FINAL SUMMARY
    # =========================================================

    print("\n" + "=" * 70)
    print("TRUTHGUARD TEST SUMMARY")
    print("=" * 70)

    print("\nQuestion:")
    print(question)

    print("\nOriginal Response:")
    print(original_response)

    print(
        f"\nClaims Extracted: "
        f"{len(claims)}"
    )

    print(
        f"Evidence Average: "
        f"{evidence_average}"
    )

    print(
        f"Judge Average: "
        f"{judge_average}"
    )

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
        f"Final Decision: "
        f"{risk_result['decision']}"
    )

    print("\n" + "=" * 70)
    print("TEST COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    main()