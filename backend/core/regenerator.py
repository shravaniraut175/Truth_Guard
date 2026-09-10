import os

from dotenv import load_dotenv
from google import genai
from google.genai import types


load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

if not API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY is not configured."
    )

client = genai.Client(api_key=API_KEY)


def regenerate_response(
    question: str,
    original_response: str,
    verification_context: str,
) -> str:

    if not question.strip():
        raise ValueError("Question cannot be empty.")

    if not original_response.strip():
        raise ValueError("Original response cannot be empty.")

    prompt = f"""
You are the response regeneration module of TruthGuard.

The original answer may contain hallucinated, unsupported,
or unreliable information.

Your task is to produce a safer and more reliable answer.

RULES:
1. Keep information that is supported by the verification evidence.
2. Remove unsupported or contradicted claims.
3. Correct claims when the verification evidence provides a correction.
4. Do not invent replacement facts.
5. If reliable information is insufficient, explicitly say so.
6. Answer the user's original question directly.
7. Do not mention TruthGuard, hallucination detection,
   scoring, internal verification, or this regeneration process.
8. Do not claim that you verified something unless the evidence
   provided below supports it.

USER QUESTION:
{question.strip()}

ORIGINAL RESPONSE:
{original_response.strip()}

VERIFICATION INFORMATION:
{verification_context.strip()}

Generate the final improved answer.
"""

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.2,
                max_output_tokens=700,
            ),
        )

        if not response.text:
            raise RuntimeError(
                "Gemini returned an empty regenerated response."
            )

        return response.text.strip()

    except Exception as exc:
        raise RuntimeError(
            f"Response regeneration failed: {exc}"
        ) from exc