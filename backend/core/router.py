VERIFICATION_PLAN = {

    "LOW": {
        "claim_extraction": False,
        "evidence": True,
        "blackbox": False,
        "whitebox": False,
        "judge": True,
    },

    "MEDIUM": {
        "claim_extraction": True,
        "evidence": True,
        "blackbox": True,
        "whitebox": False,
        "judge": True,
    },

    "HIGH": {
        "claim_extraction": True,
        "evidence": True,
        "blackbox": True,
        "whitebox": True,
        "judge": True,
    },
}


def get_verification_plan(level: str) -> dict:

    level = level.upper()

    if level not in VERIFICATION_PLAN:
        raise ValueError(
            f"Unknown complexity level: {level}"
        )

    return VERIFICATION_PLAN[level].copy()