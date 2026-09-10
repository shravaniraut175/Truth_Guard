import os
import re

from dotenv import load_dotenv
from google import genai
from google.genai import types


load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = os.getenv("EVIDENCE_MODEL", "gemini-2.5-flash")

if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not configured.")

client = genai.Client(api_key=API_KEY)


def final_verify(
    question: str,
    response: str,
) -> dict:

    if not question.strip():
        raise ValueError("Question cannot be empty.")

    if not response.strip():
        raise ValueError("Response cannot be empty.")

    prompt = f"""
You are the final verification module of TruthGuard.

Evaluate the following answer for factual reliability.

USER QUESTION:
{question.strip()}

ANSWER:
{response.strip()}

Use reliable information available through your knowledge.

Return EXACTLY in this format:

SCORE: <0-100>
VERDICT: <SUPPORTED | PARTIALLY SUPPORTED | CONTRADICTED | INSUFFICIENT EVIDENCE>
EXPLANATION: <short explanation>

Rules:
- 90-100 = highly reliable
- 70-89 = mostly reliable
- 40-69 = partially reliable or uncertain
- 0-39 = unreliable or contradicted
- Do not invent evidence.
- Keep the explanation concise.
"""

    try:
        response_obj = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.1,
                max_output_tokens=400,
            ),
        )

        text = response_obj.text

        if not text:
            raise RuntimeError("Final verification returned an empty response.")

        score_match = re.search(
            r"SCORE:\s*(\d+(?:\.\d+)?)",
            text,
            re.IGNORECASE,
        )

        verdict_match = re.search(
            r"VERDICT:\s*(SUPPORTED|PARTIALLY SUPPORTED|CONTRADICTED|INSUFFICIENT EVIDENCE)",
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
                f"Unable to parse final verification response: {text}"
            )

        score = float(score_match.group(1))

        verdict = verdict_match.group(1).upper()

        explanation = (
            explanation_match.group(1).strip()
            if explanation_match
            else ""
        )

        return {
            "method": "Final Verification",
            "score": round(score, 2),
            "verdict": verdict,
            "explanation": explanation,
        }

    except Exception as exc:
        raise RuntimeError(
            f"Final verification failed: {exc}"
        ) from exc