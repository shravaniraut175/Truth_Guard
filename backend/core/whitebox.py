import torch
from transformers import AutoTokenizer, AutoModelForCausalLM


MODEL_NAME = "Qwen/Qwen3-0.6B"


print("Loading White-Box UQ model...")

tokenizer = AutoTokenizer.from_pretrained(
    MODEL_NAME
)

model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    torch_dtype="auto"
)

model.eval()

print("White-Box UQ model loaded.")


def calculate_whitebox_score(
    text: str
) -> dict:

    if not text or not text.strip():
        raise ValueError(
            "Text cannot be empty."
        )

    # Tokenize the response
    inputs = tokenizer(
        text.strip(),
        return_tensors="pt"
    )

    input_ids = inputs["input_ids"]

    with torch.no_grad():

        outputs = model(
            input_ids=input_ids
        )

    logits = outputs.logits

    # ---------------------------------------------------------
    # Next-token probabilities
    # ---------------------------------------------------------

    # Logits at position i predict token i+1.
    next_token_logits = logits[:, :-1, :]

    target_tokens = input_ids[:, 1:]

    probabilities = torch.softmax(
        next_token_logits,
        dim=-1
    )

    # Probability assigned to the actual token
    token_probabilities = probabilities.gather(
        2,
        target_tokens.unsqueeze(-1)
    ).squeeze(-1)

    # ---------------------------------------------------------
    # Average token confidence
    # ---------------------------------------------------------

    average_probability = (
        token_probabilities.mean().item()
    )

    whitebox_score = round(
        average_probability * 100,
        2
    )

    # ---------------------------------------------------------
    # Minimum token confidence
    # ---------------------------------------------------------

    minimum_probability = (
        token_probabilities.min().item()
    )

    minimum_score = round(
        minimum_probability * 100,
        2
    )

    # ---------------------------------------------------------
    # Number of tokens
    # ---------------------------------------------------------

    token_count = int(
        target_tokens.shape[1]
    )

    return {
        "method": "White-Box UQ",
        "model": MODEL_NAME,
        "whitebox_score": whitebox_score,
        "minimum_token_confidence": minimum_score,
        "token_count": token_count,
    }