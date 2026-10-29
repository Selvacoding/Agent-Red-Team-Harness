from collections import Counter


def summarize_repeatability(reports: list[dict]) -> dict:
    outcomes = [
        report.get(
            "finding", {}
        ).get(
            "outcome",
            report.get("analysis", {}).get("outcome", "inconclusive"),
        )
        for report in reports
    ]

    counts = Counter(outcomes)

    return {
        "trial_count": len(reports),
        "outcome_counts": dict(counts),
        "observed_outcomes": outcomes,
        "variance_detected": len(set(outcomes)) > 1,
        "consistent": len(set(outcomes)) <= 1,
    }
