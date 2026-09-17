import re


def analyze_query(question: str) -> dict:
    if not question or not question.strip():
        raise ValueError("Question cannot be empty.")

    question = question.strip()
    lower_question = question.lower()

    # HIGH: complex, technical, multi-step, or future/current questions
    high_patterns = [
    r"\bhow will\b",
    r"\bhow would\b",
    r"\bhow might\b",
    r"\bhow could\b",
    r"\bhow may\b",
    r"\bwhat will happen\b",
    r"\bin the next\b",
    r"\bover the next\b",
    r"\bover the next \d+ years?\b",
    r"\bnext \d+ years?\b",
    r"\bimpact\b.*\b(future|next|decade|years)\b",
    r"\bwhy\b.*\band\b.*\bhow\b",
    r"\bdesign\b",
    r"\bdevelop\b",
    r"\bimplement\b",
    r"\barchitecture\b",
    r"\balgorithm\b",
    r"\bmachine learning\b",
    r"\bdeep learning\b",
    r"\bneural network\b",
    r"\bquantum computing\b",
    r"\bcybersecurity\b",
    r"\bcompare\b.*\bmultiple\b",
]

    if any(re.search(pattern, lower_question) for pattern in high_patterns):
        return {
            "level": "HIGH",
            "domain": detect_domain(lower_question),
            "reason": "The question requires complex, technical, multi-step, or future-oriented reasoning.",
        }

    # MEDIUM: comparison, advantages/disadvantages, explanations,
    # multiple related facts, moderate reasoning
    medium_patterns = [
        r"\badvantages\b",
        r"\bdisadvantages\b",
        r"\bpros\b.*\bcons\b",
        r"\bpros and cons\b",
        r"\bcompare\b",
        r"\bdifference between\b",
        r"\bexplain\b",
        r"\bbenefits\b",
        r"\blimitations\b",
        r"\btypes of\b",
        r"\bfeatures of\b",
        r"\bhow does\b",
        r"\bhow do\b",
        r"\bwhy does\b",
        r"\bwhy do\b",
        r"\bwhat are\b",
    ]

    if any(re.search(pattern, lower_question) for pattern in medium_patterns):
        return {
            "level": "MEDIUM",
            "domain": detect_domain(lower_question),
            "reason": "The question requires multiple related facts, explanation, comparison, or moderate reasoning.",
        }

    # LOW: simple factual questions
    return {
        "level": "LOW",
        "domain": detect_domain(lower_question),
        "reason": "The question is straightforward and can be answered with a simple factual response.",
    }


def detect_domain(question: str) -> str:
    current_patterns = [
        r"\btoday\b",
        r"\bcurrently\b",
        r"\blatest\b",
        r"\brecent\b",
        r"\bthis year\b",
        r"\b2026\b",
        r"\bnews\b",
        r"\bcurrent\b",
    ]

    technical_patterns = [
        r"\bpython\b",
        r"\bjavascript\b",
        r"\bjava\b",
        r"\bprogramming\b",
        r"\balgorithm\b",
        r"\bdatabase\b",
        r"\bmachine learning\b",
        r"\bdeep learning\b",
        r"\bai\b",
        r"\bartificial intelligence\b",
        r"\bneural network\b",
        r"\bcomputer\b",
        r"\bsoftware\b",
        r"\bcybersecurity\b",
        r"\bquantum computing\b",
    ]

    opinion_patterns = [
        r"\bdo you think\b",
        r"\bwhat do you think\b",
        r"\bshould\b",
        r"\bbetter\b",
        r"\bworth\b",
        r"\bopinion\b",
    ]

    if any(re.search(pattern, question) for pattern in current_patterns):
        return "CURRENT"

    if any(re.search(pattern, question) for pattern in technical_patterns):
        return "TECHNICAL"

    if any(re.search(pattern, question) for pattern in opinion_patterns):
        return "OPINION"

    if any(word in question for word in ["how", "why", "compare", "difference"]):
        return "MULTI_STEP"

    return "FACTUAL"