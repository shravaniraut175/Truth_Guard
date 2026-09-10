# import os

# from dotenv import load_dotenv
# from google import genai
# from google.genai import types


# # Load environment variables
# load_dotenv()


# # ---------------------------------------------------------
# # Configuration
# # ---------------------------------------------------------

# API_KEY = os.getenv("GEMINI_API_KEY")
# MODEL_NAME = os.getenv(
#     "GEMINI_MODEL",
#     "gemini-2.5-flash"
# )


# if not API_KEY:
#     raise RuntimeError(
#         "GEMINI_API_KEY is not configured. "
#         "Add it to the .env file."
#     )


# # ---------------------------------------------------------
# # Gemini Client
# # ---------------------------------------------------------

# client = genai.Client(
#     api_key=API_KEY
# )


# # ---------------------------------------------------------
# # Response Generator
# # ---------------------------------------------------------

# def generate_response(question: str) -> str:

#     if not question or not question.strip():
#         raise ValueError(
#             "Question cannot be empty."
#         )

#     prompt = f"""
# You are the primary language model for TruthGuard.

# Answer the user's question clearly and accurately.

# Important instructions:
# - Answer only what is relevant to the question.
# - Do not invent facts.
# - If you are uncertain about something, clearly state the uncertainty.
# - Do not claim that you verified information externally.
# - Keep the response concise but sufficiently informative.

# User question:
# {question.strip()}
# """

#     try:

#         response = client.models.generate_content(
#             model=MODEL_NAME,
#             contents=prompt,
#             config=types.GenerateContentConfig(
#                 temperature=0.2,
#                 max_output_tokens=700,
#             ),
#         )

#         if not response.text:
#             raise RuntimeError(
#                 "Gemini returned an empty response."
#             )

#         return response.text.strip()

#     except Exception as exc:

#         raise RuntimeError(
#             f"Gemini generation failed: {exc}"
#         ) from exc

from backend.core.openrouter_client import (
    generate_openrouter_response
)


def generate_response(question: str) -> str:

    if not question or not question.strip():
        raise ValueError("Question cannot be empty.")

    prompt = f"""
You are the primary language model for TruthGuard.

Answer the user's question clearly and accurately.

Important instructions:
- Answer only what is relevant to the question.
- Do not invent facts.
- If you are uncertain, clearly state the uncertainty.
- Do not claim that you verified information externally.
- Keep the response concise but sufficiently informative.

USER QUESTION:
{question.strip()}
"""

    try:

        return generate_openrouter_response(
            prompt=prompt,
            temperature=0.2,
            max_tokens=700,
        )

    except Exception as exc:

        raise RuntimeError(
            f"Response generation failed: {exc}"
        ) from exc