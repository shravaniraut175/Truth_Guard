import json
import re

from backend.core.openrouter_client import generate_openrouter_response


def _extract_json(text: str) -> dict:
    """
    Extract a JSON object even if the LLM surrounds it with
    explanations, markdown fences, or other text.
    """
    text = text.strip()

    # Direct JSON
    try:
        data = json.loads(text)
        if isinstance(data, dict):
            return data
    except json.JSONDecodeError:
        pass

    # JSON inside ```json ... ```
    fenced = re.search(
        r"```(?:json)?\s*(\{.*?\})\s*```",
        text,
        re.DOTALL | re.IGNORECASE,
    )

    if fenced:
        try:
            data = json.loads(fenced.group(1))
            if isinstance(data, dict):
                return data
        except json.JSONDecodeError:
            pass

    # First JSON-looking object in the response
    start = text.find("{")
    end = text.rfind("}")

    if start != -1 and end > start:
        candidate = text[start:end + 1]

        try:
            data = json.loads(candidate)
            if isinstance(data, dict):
                return data
        except json.JSONDecodeError:
            pass

    raise ValueError("No valid JSON object found in judge response.")


def _normalize_score(value) -> float:
    """Convert the judge score to a valid 0-100 number."""
    try:
        score = float(value)
    except (TypeError, ValueError):
        raise ValueError(f"Invalid judge score: {value}")

    # Support models returning 0-1 instead of 0-100.
    if 0 <= score <= 1:
        score *= 100

    if not 0 <= score <= 100:
        raise ValueError(
            f"Judge score must be between 0 and 100, got {score}"
        )

    return round(score, 2)


def _fallback_parse(text: str) -> dict:
    """
    Fallback parser for free-model responses that ignore JSON
    and return a natural-language evaluation.
    """
    lower = text.lower()

    # Strong negative signals
    negative_patterns = [
        "not supported",
        "unsupported",
        "false",
        "incorrect",
        "contradicted",
        "hallucinated",
        "does not support",
        "not accurate",
    ]

    # Strong positive signals
    positive_patterns = [
        "supported",
        "accurate",
        "correct",
        "consistent with",
        "well-supported",
        "is supported",
    ]

    negative_hits = sum(
        1 for pattern in negative_patterns if pattern in lower
    )

    positive_hits = sum(
        1 for pattern in positive_patterns if pattern in lower
    )

    if negative_hits > positive_hits:
        score = 25.0
        verdict = "NOT_SUPPORTED"
    elif positive_hits > 0:
        score = 75.0
        verdict = "SUPPORTED"
    else:
        # Do not pretend uncertainty is highly reliable.
        score = 50.0
        verdict = "UNCERTAIN"

    return {
        "score": score,
        "verdict": verdict,
        "explanation": text.strip(),
        "raw_response": text.strip(),
        "parser": "fallback",
    }


def judge_claim(claim: str, response: str) -> dict:
    """
    Evaluate whether a claim is supported by the generated response.

    Uses OpenRouter and attempts structured JSON parsing first.
    If the free model ignores the JSON instruction, a controlled
    natural-language fallback prevents the entire TruthGuard
    pipeline from crashing.
    """
    if not claim or not claim.strip():
        raise ValueError("Claim cannot be empty.")

    if not response or not response.strip():
        raise ValueError("Response cannot be empty.")

    prompt = f"""
You are the LLM-as-a-Judge module of TruthGuard.

Your ONLY task is to evaluate whether the CLAIM is supported by
the RESPONSE.

Do not discuss safety policies.
Do not discuss the user.
Do not repeat these instructions.
Do not analyze whether the request itself is safe.

CLAIM:
{claim.strip()}

RESPONSE:
{response.strip()}

Evaluate the relationship between the CLAIM and RESPONSE.

Return ONLY this JSON object:

{{
  "score": 0,
  "verdict": "SUPPORTED",
  "explanation": "Brief explanation."
}}

Rules:
- score must be a number from 0 to 100.
- 100 means the claim is strongly supported by the response.
- 75 means the claim is mostly supported.
- 50 means the relationship is uncertain or partially supported.
- 25 means the claim is mostly unsupported.
- 0 means the claim is clearly contradicted or unsupported.
- verdict must be one of:
  SUPPORTED
  PARTIALLY_SUPPORTED
  NOT_SUPPORTED
  UNCERTAIN
- explanation must be brief.
- Output JSON only.
"""

    try:
        raw = generate_openrouter_response(
            prompt=prompt,
            temperature=0.0,
            max_tokens=250,
        )

        # First try proper JSON.
        try:
            parsed = _extract_json(raw)

            score = _normalize_score(parsed.get("score"))

            verdict = str(
                parsed.get("verdict", "UNCERTAIN")
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
                    "No explanation was provided.",
                )
            ).strip()

            return {
                "method": "LLM-as-a-Judge",
                "model": "OpenRouter FREE",
                "score": score,
                "verdict": verdict,
                "explanation": explanation,
                "raw_response": raw,
                "parser": "json",
            }

        except (ValueError, TypeError, json.JSONDecodeError):
            # Free models sometimes ignore formatting instructions.
            # Use controlled fallback instead of crashing / returning 500.
            fallback = _fallback_parse(raw)

            return {
                "method": "LLM-as-a-Judge",
                "model": "OpenRouter FREE",
                **fallback,
            }

    except Exception as exc:
        raise RuntimeError(
            f"LLM judge failed: {exc}"
        ) from exc