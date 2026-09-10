import os
import json
from typing import List, Literal

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from google import genai
from google.genai import types

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
CLAIM_MODEL = os.getenv(
    "CLAIM_MODEL",
    "gemini-2.5-flash-lite"
)

if not API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY is not configured. "
        "Add it to the .env file."
    )

client = genai.Client(api_key=API_KEY)


class Claim(BaseModel):
    id: int = Field(
        description="Unique sequential ID of the claim."
    )

    text: str = Field(
        description="The exact factual claim extracted from the response."
    )

    type: Literal[
        "factual",
        "numerical",
        "temporal",
        "causal",
        "comparative",
        "opinion"
    ] = Field(
        description="Type of claim."
    )


class ClaimExtractionResult(BaseModel):
    claims: List[Claim]


def extract_claims(response_text: str) -> ClaimExtractionResult:

    if not response_text or not response_text.strip():
        raise ValueError("Response text cannot be empty.")

    prompt = f"""
You are the claim extraction module of TruthGuard,
an AI hallucination detection framework.

Your task is to extract meaningful claims from the
LLM-generated response.

Rules:

1. Extract claims that can potentially be checked or verified.
2. Break complex sentences into separate claims when appropriate.
3. Preserve the meaning of the original response.
4. Do not add facts that are not present in the response.
5. Do not rewrite claims to make them more accurate.
6. Include numerical, temporal, causal and comparative claims.
7. Opinions should only be included when they are explicitly stated.
8. Ignore greetings, filler text and instructions.
9. Give each claim a unique sequential ID starting from 1.
10. Return only the structured JSON result.

LLM-generated response:

{response_text.strip()}
"""

    try:
        result = client.models.generate_content(
            model=CLAIM_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.0,
                response_mime_type="application/json",
                response_schema=ClaimExtractionResult,
            ),
        )

        if not result.text:
            raise RuntimeError(
                "Claim extraction model returned an empty response."
            )

        extracted = ClaimExtractionResult.model_validate_json(
            result.text
        )

        return extracted

    except Exception as exc:
        raise RuntimeError(
            f"Claim extraction failed: {exc}"
        ) from exc