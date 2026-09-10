from typing import List

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from backend.core.openrouter_client import (
    generate_openrouter_response
)


# Lightweight local embedding model
embedding_model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)


def generate_multiple_responses(
    question: str,
    num_responses: int = 3
) -> List[str]:

    if not question or not question.strip():
        raise ValueError("Question cannot be empty.")

    if num_responses < 2:
        raise ValueError(
            "At least two responses are required."
        )

    responses = []

    prompt = f"""
Answer the following question independently.

Question:
{question.strip()}

Provide a clear and factual answer.

Do not mention that you are generating multiple responses.
"""

    for _ in range(num_responses):

        try:

            response = generate_openrouter_response(
                prompt=prompt,
                temperature=0.7,
                max_tokens=500,
            )

            if response:
                responses.append(response)

        except Exception as exc:

            raise RuntimeError(
                f"Black-box response generation failed: {exc}"
            ) from exc

    if len(responses) < 2:

        raise RuntimeError(
            "Black-box UQ requires at least two responses."
        )

    return responses


def calculate_consistency_score(
    responses: List[str]
) -> float:

    if len(responses) < 2:
        raise ValueError(
            "At least two responses are required."
        )

    embeddings = embedding_model.encode(
        responses,
        normalize_embeddings=True
    )

    similarity_matrix = cosine_similarity(
        embeddings
    )

    similarities = []

    for i in range(len(responses)):

        for j in range(i + 1, len(responses)):

            similarities.append(
                similarity_matrix[i][j]
            )

    score = sum(similarities) / len(similarities)

    return round(
        float(score) * 100,
        2
    )


def blackbox_score(
    question: str,
    num_responses: int = 3
) -> dict:

    responses = generate_multiple_responses(
        question,
        num_responses
    )

    consistency = calculate_consistency_score(
        responses
    )

    return {
        "method": "Black-Box UQ",
        "model": "OpenRouter FREE",
        "num_responses": len(responses),
        "consistency_score": consistency,
        "responses": responses,
    }