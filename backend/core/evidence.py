import re
from typing import List, Dict

from ddgs import DDGS

from backend.core.openrouter_client import (
    generate_openrouter_response
)


# =========================================================
# Web Search
# =========================================================

def search_web(
    query: str,
    max_results: int = 5
) -> List[Dict]:
    """
    Search the web using DuckDuckGo and return
    normalized search results.
    """

    if not query or not query.strip():
        raise ValueError(
            "Search query cannot be empty."
        )

    results = []

    try:
        with DDGS() as ddgs:

            search_results = ddgs.text(
                query.strip(),
                max_results=max_results
            )

            for item in search_results:

                results.append({
                    "title": item.get(
                        "title",
                        "Untitled"
                    ),
                    "url": item.get(
                        "href",
                        ""
                    ),
                    "snippet": item.get(
                        "body",
                        ""
                    )
                })

    except Exception as exc:

        raise RuntimeError(
            f"Web search failed: {exc}"
        ) from exc

    return results


# =========================================================
# Build Evidence Context
# =========================================================

def _build_evidence_context(
    sources: List[Dict]
) -> str:
    """
    Convert retrieved web results into a compact
    context for the OpenRouter judge.
    """

    evidence_parts = []

    for index, source in enumerate(
        sources,
        start=1
    ):

        evidence_parts.append(
            f"""
SOURCE {index}

TITLE:
{source.get("title", "Untitled")}

URL:
{source.get("url", "")}

SNIPPET:
{source.get("snippet", "")}
"""
        )

    return "\n".join(evidence_parts)


# =========================================================
# Parse Score
# =========================================================

def _parse_score(
    assessment: str
) -> float:
    """
    Extract a score from the OpenRouter response.

    Supports formats such as:

    SCORE: 95
    SCORE: 95.5
    Score - 95
    TRUTH SCORE: 95
    CONFIDENCE SCORE: 95
    95/100
    95%
    """

    # -----------------------------------------------------
    # Standard score format
    # -----------------------------------------------------

    score_match = re.search(
        r"(?:SCORE|TRUTH\s*SCORE|CONFIDENCE\s*SCORE)"
        r"\s*[:\-]?\s*"
        r"(\d+(?:\.\d+)?)",
        assessment,
        re.IGNORECASE
    )

    if score_match:

        score = float(
            score_match.group(1)
        )

        return max(
            0.0,
            min(100.0, score)
        )

    # -----------------------------------------------------
    # Percentage / 100 format
    # -----------------------------------------------------

    percentage_match = re.search(
        r"\b(\d+(?:\.\d+)?)\s*(?:%|/100)\b",
        assessment,
        re.IGNORECASE
    )

    if percentage_match:

        score = float(
            percentage_match.group(1)
        )

        return max(
            0.0,
            min(100.0, score)
        )

    # -----------------------------------------------------
    # No score found
    # -----------------------------------------------------

    raise ValueError(
        "Could not extract evidence score.\n"
        f"OpenRouter response:\n{assessment}"
    )


# =========================================================
# Parse Verdict
# =========================================================

def _parse_verdict(
    assessment: str
) -> str:
    """
    Extract the verification verdict.
    """

    verdict_match = re.search(
        r"VERDICT\s*[:\-]?\s*"
        r"(SUPPORTED|"
        r"PARTIALLY\s+SUPPORTED|"
        r"CONTRADICTED|"
        r"INSUFFICIENT\s+EVIDENCE)",
        assessment,
        re.IGNORECASE
    )

    if not verdict_match:

        return "INSUFFICIENT EVIDENCE"

    return (
        verdict_match
        .group(1)
        .upper()
    )


# =========================================================
# Parse Explanation
# =========================================================

def _parse_explanation(
    assessment: str
) -> str:
    """
    Extract the explanation from the OpenRouter response.
    """

    explanation_match = re.search(
        r"EXPLANATION\s*[:\-]?\s*(.*)",
        assessment,
        re.IGNORECASE | re.DOTALL
    )

    if explanation_match:

        explanation = (
            explanation_match
            .group(1)
            .strip()
        )

        if explanation:
            return explanation

    # If the model didn't follow the format,
    # return the complete response rather than losing it.
    return assessment.strip()


# =========================================================
# OpenRouter Evidence Evaluation
# =========================================================

def _evaluate_evidence(
    claim: str,
    sources: List[Dict]
) -> Dict:
    """
    Ask OpenRouter to evaluate the retrieved evidence.
    """

    evidence_context = _build_evidence_context(
        sources
    )

    prompt = f"""
You are the Evidence Verification module
of TruthGuard.

Your ONLY task is to determine whether the CLAIM
is supported by the RETRIEVED WEB EVIDENCE.

Do not use outside knowledge.

Do not invent facts.

Do not invent sources.

Do not claim that you accessed the URLs directly.

Evaluate ONLY the evidence snippets provided below.

CLAIM:
{claim}

RETRIEVED WEB EVIDENCE:
{evidence_context}

SCORING RULES:

90-100:
The evidence strongly supports the claim.

70-89:
The evidence mostly supports the claim,
with minor uncertainty or missing context.

40-69:
The evidence is partial, ambiguous,
or insufficient to confidently verify the claim.

1-39:
The evidence mostly contradicts the claim.

0:
The evidence clearly contradicts the claim.

VERDICT MUST BE ONE OF:

SUPPORTED
PARTIALLY SUPPORTED
CONTRADICTED
INSUFFICIENT EVIDENCE

RETURN ONLY THIS FORMAT:

SCORE: <number from 0 to 100>

VERDICT: <one allowed verdict>

EXPLANATION: <brief factual explanation>

Keep the explanation concise.
"""

    print(
        "[TruthGuard Evidence] "
        "Evaluating retrieved evidence with OpenRouter..."
    )

    assessment = generate_openrouter_response(
        prompt=prompt,
        temperature=0.0,
        max_tokens=250
    )

    if not assessment:
        raise RuntimeError(
            "OpenRouter returned an empty "
            "evidence assessment."
        )

    assessment = assessment.strip()

    return {
        "score": _parse_score(
            assessment
        ),
        "verdict": _parse_verdict(
            assessment
        ),
        "explanation": _parse_explanation(
            assessment
        ),
        "raw_assessment": assessment
    }


# =========================================================
# Main Evidence Verification
# =========================================================

def verify_claim(
    claim: str
) -> Dict:
    """
    Verify a claim using:

        1. DuckDuckGo web search
        2. Retrieved evidence snippets
        3. OpenRouter evaluation

    Gemini is NOT used in this module.

    This prevents Gemini quota problems from
    breaking evidence verification.
    """

    if not claim or not claim.strip():

        raise ValueError(
            "Claim cannot be empty."
        )

    claim = claim.strip()

    print(
        f"[TruthGuard Evidence] "
        f"Searching web for: {claim}"
    )

    # -----------------------------------------------------
    # Step 1: Search web
    # -----------------------------------------------------

    sources = search_web(
        claim,
        max_results=5
    )

    # -----------------------------------------------------
    # Step 2: No evidence
    # -----------------------------------------------------

    if not sources:

        print(
            "[TruthGuard Evidence] "
            "No web evidence found."
        )

        return {
            "claim": claim,
            "score": 50.0,
            "verdict": "INSUFFICIENT EVIDENCE",
            "explanation": (
                "No relevant web sources were "
                "found for this claim."
            ),
            "sources": [],
            "model_used": "OpenRouter",
            "raw_assessment": ""
        }

    # -----------------------------------------------------
    # Step 3: Evaluate evidence
    # -----------------------------------------------------

    try:

        evaluation = _evaluate_evidence(
            claim,
            sources
        )

        print(
            "[TruthGuard Evidence] "
            "Evidence verification successful."
        )

        return {
            "claim": claim,
            "score": round(
                evaluation["score"],
                2
            ),
            "verdict": evaluation["verdict"],
            "explanation": evaluation["explanation"],
            "sources": sources,
            "model_used": "OpenRouter",
            "raw_assessment": evaluation[
                "raw_assessment"
            ]
        }

    except Exception as exc:

        print(
            "[TruthGuard Evidence] "
            f"Verification failed: {exc}"
        )

        raise RuntimeError(
            f"Evidence verification failed: {exc}"
        ) from exc