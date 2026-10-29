def calculate_severity(analysis: dict) -> str:
    """Score severity using demonstrated impact and evaluation evidence."""

    if analysis.get("outcome") == "not_exposed":
        return "none"

    if analysis.get("attack_succeeded") is True:
        return "critical"

    if analysis.get("attack_blocked") is True:
        return "low"

    # Missing or inconclusive evidence is not proof of success.
    return "none"
