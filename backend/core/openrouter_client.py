import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL_NAME = os.getenv(
    "OPENROUTER_MODEL",
    "openrouter/free"
)

if not API_KEY:
    raise RuntimeError("OPENROUTER_API_KEY is not configured.")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=API_KEY,
)


def generate_openrouter_response(
    prompt: str,
    temperature: float = 0.1,
    max_tokens: int = 500,
) -> str:

    if not prompt or not prompt.strip():
        raise ValueError("Prompt cannot be empty.")

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "user",
                    "content": prompt.strip(),
                }
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )

        # Debug information
        if not response.choices:
            raise RuntimeError(
                f"OpenRouter returned no choices. Response: {response}"
            )

        message = response.choices[0].message

        content = message.content

        # Some reasoning models may return empty content.
        if not content:
            reasoning = getattr(message, "reasoning", None)

            if reasoning:
                content = reasoning

        if not content:
            raise RuntimeError(
                "OpenRouter returned an empty response.\n"
                f"Model: {MODEL_NAME}\n"
                f"Message: {message}\n"
                f"Full response: {response}"
            )

        return content.strip()

    except Exception as exc:
        raise RuntimeError(
            f"OpenRouter request failed: {exc}"
        ) from exc