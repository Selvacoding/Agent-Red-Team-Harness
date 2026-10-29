def calculate_severity(analysis: dict) -> str:
    if analysis["attack_succeeded"]:
        return "critical"

    if analysis["attack_blocked"]:
        return "low"

    return "none"
