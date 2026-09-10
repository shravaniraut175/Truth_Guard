import re

from backend.core.openrouter_client import (
    generate_openrouter_response
)


def judge_claim(
    claim: str,
    response: str,
) -> dict:

    if not claim or not claim.strip():
        raise ValueError("Claim cannot be empty.")

    if not response or not response.strip():
        raise ValueError("Response cannot be empty.")

    prompt = f"""
You are the LLM-as-a-Judge module of TruthGuard.

Evaluate whether the CLAIM is supported by the RESPONSE.

CLAIM:
{claim.strip()}

RESPONSE:
{response.strip()}

Return EXACTLY:

SCORE: <0-100>
VERDICT: <SUPPORTED | PARTIALLY SUPPORTED | CONTRADICTED | INSUFFICIENT CONTEXT>
EXPLANATION: <short explanation>

Scoring:
90-100 = strongly supported
70-89 = mostly supported
40-69 = partially supported or uncertain
0-39 = contradicted or unsupported

Important:
- Judge only the relationship between the claim and response.
- Do not invent external evidence.
- Do not use web search.
- Keep the explanation concise.
"""

    try:

        text = generate_openrouter_response(
            prompt=prompt,
            temperature=0.1,
            max_tokens=300,
        )

        score_match = re.search(
            r"SCORE:\s*(\d+(?:\.\d+)?)",
            text,
            re.IGNORECASE,
        )

        verdict_match = re.search(
            r"VERDICT:\s*"
            r"(SUPPORTED|PARTIALLY SUPPORTED|CONTRADICTED|INSUFFICIENT CONTEXT)",
            text,
            re.IGNORECASE,
        )

        explanation_match = re.search(
            r"EXPLANATION:\s*(.*)",
            text,
            re.IGNORECASE | re.DOTALL,
        )

        if not score_match or not verdict_match:
            raise RuntimeError(
                f"Unable to parse judge response: {text}"
            )

        score = float(score_match.group(1))

        score = max(0, min(100, score))

        verdict = verdict_match.group(1).upper()

        explanation = (
            explanation_match.group(1).strip()
            if explanation_match
            else ""
        )

        return {
            "claim": claim,
            "score": round(score, 2),
            "verdict": verdict,
            "explanation": explanation,
        }

    except Exception as exc:

        raise RuntimeError(
            f"LLM judge failed: {exc}"
        ) from exc