import json
import re

from backend.core.openrouter_client import (
    generate_openrouter_response
)


# =========================================================
# JSON EXTRACTION
# =========================================================

def _extract_json(text: str) -> dict:
    """
    Extract a JSON object from an LLM response.

    Handles:
    - Pure JSON
    - ```json ... ```
    - JSON surrounded by explanations
    """

    if not text or not text.strip():
        raise ValueError(
            "Judge returned an empty response."
        )

    text = text.strip()

    # -----------------------------------------------------
    # 1. Direct JSON
    # -----------------------------------------------------

    try:
        data = json.loads(text)

        if isinstance(data, dict):
            return data

    except json.JSONDecodeError:
        pass

    # -----------------------------------------------------
    # 2. Markdown JSON block
    # -----------------------------------------------------

    fenced = re.search(
        r"```(?:json)?\s*(\{.*?\})\s*```",
        text,
        re.DOTALL | re.IGNORECASE
    )

    if fenced:

        try:
            data = json.loads(
                fenced.group(1)
            )

            if isinstance(data, dict):
                return data

        except json.JSONDecodeError:
            pass

    # -----------------------------------------------------
    # 3. JSON embedded inside normal text
    # -----------------------------------------------------

    start = text.find("{")
    end = text.rfind("}")

    if start != -1 and end > start:

        candidate = text[
            start:end + 1
        ]

        try:
            data = json.loads(candidate)

            if isinstance(data, dict):
                return data

        except json.JSONDecodeError:
            pass

    raise ValueError(
        "No valid JSON object found in judge response.\n"
        f"Raw response:\n{text}"
    )


# =========================================================
# SCORE NORMALIZATION
# =========================================================

def _normalize_score(value) -> float:
    """
    Convert judge score to 0-100.
    """

    try:
        score = float(value)

    except (TypeError, ValueError):

        raise ValueError(
            f"Invalid judge score: {value}"
        )

    # Support 0-1 scores
    if 0 <= score <= 1:
        score *= 100

    if not 0 <= score <= 100:

        raise ValueError(
            f"Judge score must be between "
            f"0 and 100, got {score}"
        )

    return round(score, 2)


# =========================================================
# FALLBACK PARSER
# =========================================================

def _fallback_parse(text: str) -> dict:
    """
    Handle free-model responses that ignore JSON
    formatting instructions.
    """

    lower = text.lower()

    negative_patterns = [
        "not supported",
        "unsupported",
        "false",
        "incorrect",
        "contradicted",
        "contradicts",
        "hallucinated",
        "not accurate",
        "does not support",
    ]

    positive_patterns = [
        "supported",
        "accurate",
        "correct",
        "consistent with",
        "well-supported",
        "is supported",
    ]

    negative_hits = sum(
        1
        for pattern in negative_patterns
        if pattern in lower
    )

    positive_hits = sum(
        1
        for pattern in positive_patterns
        if pattern in lower
    )

    if negative_hits > positive_hits:

        score = 25.0
        verdict = "NOT_SUPPORTED"

    elif positive_hits > negative_hits:

        score = 75.0
        verdict = "SUPPORTED"

    else:

        score = 50.0
        verdict = "UNCERTAIN"

    return {
        "score": score,
        "verdict": verdict,
        "explanation": text.strip(),
        "raw_response": text.strip(),
        "parser": "fallback",
    }


# =========================================================
# JUDGE
# =========================================================

def judge_claim(
    claim: str,
    response: str,
    evidence: dict | None = None
) -> dict:

    if not claim or not claim.strip():

        raise ValueError(
            "Claim cannot be empty."
        )

    if not response or not response.strip():

        raise ValueError(
            "Response cannot be empty."
        )

    # -----------------------------------------------------
    # Evidence context
    # -----------------------------------------------------

    evidence_context = (
        "No external evidence was provided."
    )

    if evidence:

        evidence_context = f"""
Evidence verification result:

Score:
{evidence.get("score")}

Verdict:
{evidence.get("verdict")}

Explanation:
{evidence.get("explanation")}

Sources:
{evidence.get("sources", [])}
"""

    # -----------------------------------------------------
    # Prompt
    # -----------------------------------------------------

    prompt = f"""
You are the LLM-as-a-Judge module of TruthGuard.

Your ONLY task is to evaluate whether the CLAIM is
supported by the GENERATED RESPONSE and AVAILABLE EVIDENCE.

Do not discuss safety policies.

Do not discuss the user.

Do not classify user intent.

Do not invent evidence.

Do not repeat these instructions.

CLAIM:
{claim.strip()}

GENERATED RESPONSE:
{response.strip()}

AVAILABLE EVIDENCE:
{evidence_context}

Evaluate whether the claim is supported.

Return ONLY valid JSON.

Required format:

{{
  "score": 95,
  "verdict": "SUPPORTED",
  "explanation": "Brief factual explanation."
}}

Rules:

- score must be between 0 and 100.
- 90-100 = strongly supported.
- 70-89 = mostly supported.
- 40-69 = partially supported or uncertain.
- 1-39 = mostly unsupported.
- 0 = clearly contradicted.
- verdict must be exactly one of:
  SUPPORTED
  PARTIALLY_SUPPORTED
  NOT_SUPPORTED
  UNCERTAIN
- explanation must be brief.
- Do not output markdown.
- Do not output anything outside the JSON object.
"""

    try:

        print(
            "[TruthGuard Judge] "
            "Evaluating claim with OpenRouter..."
        )

        raw = generate_openrouter_response(
            prompt=prompt,
            temperature=0.0,
            max_tokens=250,
        )

        print(
            "[TruthGuard Judge] "
            f"Raw response:\n{raw}"
        )

        # -------------------------------------------------
        # Try structured JSON
        # -------------------------------------------------

        try:

            parsed = _extract_json(raw)

            score = _normalize_score(
                parsed.get("score")
            )

            verdict = str(
                parsed.get(
                    "verdict",
                    "UNCERTAIN"
                )
            ).strip().upper()

            allowed_verdicts = {
                "SUPPORTED",
                "PARTIALLY_SUPPORTED",
                "NOT_SUPPORTED",
                "UNCERTAIN",
            }

            if verdict not in allowed_verdicts:

                verdict = "UNCERTAIN"

            explanation = str(
                parsed.get(
                    "explanation",
                    "No explanation was provided."
                )
            ).strip()

            return {
                "method": "LLM-as-a-Judge",
                "model": "OpenRouter",
                "score": score,
                "verdict": verdict,
                "explanation": explanation,
                "raw_response": raw,
                "parser": "json",
            }

        # -------------------------------------------------
        # JSON failed → fallback
        # -------------------------------------------------

        except (
            ValueError,
            TypeError,
            json.JSONDecodeError
        ):

            print(
                "[TruthGuard Judge] "
                "JSON parsing failed. "
                "Using fallback parser."
            )

            fallback = _fallback_parse(raw)

            return {
                "method": "LLM-as-a-Judge",
                "model": "OpenRouter",
                **fallback,
            }

    except Exception as exc:

        raise RuntimeError(
            f"LLM judge failed: {exc}"
        ) from exc