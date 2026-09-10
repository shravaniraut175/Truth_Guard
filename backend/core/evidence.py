import os
import re
from typing import List, Dict

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

API_KEY = os.getenv("GEMINI_API_KEY")

MODEL_NAME = os.getenv(
    "EVIDENCE_MODEL",
    "gemini-2.5-flash"
)

# Comma-separated fallback models
FALLBACK_MODELS = [
    model.strip()
    for model in os.getenv(
        "EVIDENCE_FALLBACK_MODELS",
        "gemini-2.5-flash-lite,gemini-3.5-flash-lite,gemini-3.5-flash"
    ).split(",")
    if model.strip()
]


if not API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY is not configured."
    )


client = genai.Client(api_key=API_KEY)


# ---------------------------------------------------------
# Build model list
# ---------------------------------------------------------

def get_evidence_models() -> List[str]:
    """
    Return the primary model followed by fallback models.
    Removes duplicates while preserving order.
    """

    models = [MODEL_NAME] + FALLBACK_MODELS

    unique_models = []

    for model in models:
        if model not in unique_models:
            unique_models.append(model)

    return unique_models


# ---------------------------------------------------------
# Parse Gemini response
# ---------------------------------------------------------

def parse_evidence_response(
    assessment_text: str,
    response
) -> Dict:

    # -----------------------------------------------------
    # Extract score
    # -----------------------------------------------------

    score_match = re.search(
        r"SCORE:\s*(\d+)",
        assessment_text,
        re.IGNORECASE
    )

    if not score_match:
        raise RuntimeError(
            "Could not extract evidence score from Gemini response."
        )

    score = int(score_match.group(1))
    score = max(0, min(100, score))

    # -----------------------------------------------------
    # Extract verdict
    # -----------------------------------------------------

    verdict_match = re.search(
        r"VERDICT:\s*"
        r"(SUPPORTED|PARTIALLY SUPPORTED|CONTRADICTED|INSUFFICIENT EVIDENCE)",
        assessment_text,
        re.IGNORECASE
    )

    if not verdict_match:
        raise RuntimeError(
            "Could not extract evidence verdict."
        )

    verdict = verdict_match.group(1).upper()

    # -----------------------------------------------------
    # Extract explanation
    # -----------------------------------------------------

    explanation_match = re.search(
        r"EXPLANATION:\s*(.*)",
        assessment_text,
        re.IGNORECASE | re.DOTALL
    )

    if explanation_match:
        explanation = explanation_match.group(1).strip()
    else:
        explanation = assessment_text

    # -----------------------------------------------------
    # Extract grounding sources
    # -----------------------------------------------------

    sources: List[Dict] = []

    if response.candidates:

        candidate = response.candidates[0]

        grounding_metadata = getattr(
            candidate,
            "grounding_metadata",
            None
        )

        if grounding_metadata:

            grounding_chunks = getattr(
                grounding_metadata,
                "grounding_chunks",
                []
            )

            for chunk in grounding_chunks:

                web = getattr(
                    chunk,
                    "web",
                    None
                )

                if web:

                    title = getattr(
                        web,
                        "title",
                        None
                    )

                    uri = getattr(
                        web,
                        "uri",
                        None
                    )

                    if uri:

                        sources.append({
                            "title": title or "Source",
                            "url": uri
                        })

    return {
        "score": score,
        "verdict": verdict,
        "explanation": explanation,
        "sources": sources,
    }


# ---------------------------------------------------------
# Evidence Verification
# ---------------------------------------------------------

def verify_claim(claim: str) -> Dict:

    if not claim or not claim.strip():
        raise ValueError(
            "Claim cannot be empty."
        )

    claim = claim.strip()

    prompt = f"""
You are the Evidence Verification module of TruthGuard.

Verify the following claim using reliable and relevant
information retrieved from the web.

CLAIM:

{claim}

Evaluate the claim carefully.

Scoring rules:

90-100:
Strongly supported by reliable evidence.

70-89:
Mostly supported, with minor uncertainty.

40-69:
Partially supported, ambiguous, or missing important context.

1-39:
Evidence mostly contradicts the claim.

0:
Clearly contradicted by reliable evidence.

Return your answer EXACTLY in this format:

SCORE: <number from 0 to 100>

VERDICT: <one of SUPPORTED, PARTIALLY SUPPORTED, CONTRADICTED, INSUFFICIENT EVIDENCE>

EXPLANATION: <short explanation>

Important:

- Search the web before making the assessment.
- Prefer authoritative sources.
- Consider the date for time-sensitive claims.
- Do not invent sources.
- If reliable sources disagree, mention it briefly.
"""

    models_to_try = get_evidence_models()

    errors = []

    # -----------------------------------------------------
    # Try primary model + fallbacks
    # -----------------------------------------------------

    for index, model in enumerate(models_to_try):

        try:

            print(
                f"[TruthGuard Evidence] "
                f"Trying model: {model}"
            )

            grounding_tool = types.Tool(
                google_search=types.GoogleSearch()
            )

            response = client.models.generate_content(
                model=model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.0,
                    tools=[grounding_tool],
                ),
            )

            # -------------------------------------------------
            # Check response
            # -------------------------------------------------

            if not response.text:

                raise RuntimeError(
                    "Evidence verification returned "
                    "an empty response."
                )

            assessment_text = response.text.strip()

            # -------------------------------------------------
            # Parse response
            # -------------------------------------------------

            parsed = parse_evidence_response(
                assessment_text,
                response
            )

            print(
                f"[TruthGuard Evidence] "
                f"Success with model: {model}"
            )

            return {
                "claim": claim,
                "score": parsed["score"],
                "verdict": parsed["verdict"],
                "explanation": parsed["explanation"],
                "sources": parsed["sources"],
                "model_used": model,
            }

        except Exception as exc:

            error_message = str(exc)

            errors.append(
                f"{model}: {error_message}"
            )

            print(
                f"[TruthGuard Evidence] "
                f"Model failed: {model}"
            )

            print(
                f"[TruthGuard Evidence] "
                f"Error: {error_message}"
            )

            # ---------------------------------------------
            # Try next model
            # ---------------------------------------------

            if index < len(models_to_try) - 1:

                print(
                    "[TruthGuard Evidence] "
                    "Trying fallback model..."
                )

                continue

    # -----------------------------------------------------
    # All models failed
    # -----------------------------------------------------

    error_summary = "\n".join(errors)

    raise RuntimeError(
        "Evidence verification failed. "
        "All configured Gemini models failed.\n\n"
        f"{error_summary}"
    )