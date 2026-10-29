from unittest.mock import Mock

import pytest

from core.scoring.repeatability import summarize_repeatability
from core.orchestartion.runner import ProbeRunner

def test_consistent_outcomes_have_no_variance():
    reports = [
        {"finding": {"outcome": "blocked"}},
        {"finding": {"outcome": "blocked"}},
        {"finding": {"outcome": "blocked"}},
    ]

    summary = summarize_repeatability(reports)

    assert summary["trial_count"] == 3
    assert summary["outcome_counts"] == {"blocked": 3}
    assert summary["variance_detected"] is False
    assert summary["consistent"] is True


def test_different_outcomes_detect_variance():
    reports = [
        {"finding": {"outcome": "blocked"}},
        {"finding": {"outcome": "successful"}},
        {"finding": {"outcome": "inconclusive"}},
    ]

    summary = summarize_repeatability(reports)

    assert summary["variance_detected"] is True
    assert summary["consistent"] is False
    assert summary["outcome_counts"] == {
        "blocked": 1,
        "successful": 1,
        "inconclusive": 1,
    }


def test_empty_reports_are_consistent():
    summary = summarize_repeatability([])

    assert summary["trial_count"] == 0
    assert summary["variance_detected"] is False
    assert summary["consistent"] is True


def test_analysis_outcome_is_supported():
    reports = [
        {"analysis": {"outcome": "blocked"}},
        {"analysis": {"outcome": "blocked"}},
    ]

    summary = summarize_repeatability(reports)

    assert summary["observed_outcomes"] == ["blocked", "blocked"]


def test_missing_outcome_defaults_to_inconclusive():
    summary = summarize_repeatability([{}])

    assert summary["observed_outcomes"] == ["inconclusive"]


def test_run_repeated_summarizes_trial_outcomes():
    runner = ProbeRunner.__new__(ProbeRunner)
    runner.run = Mock(
        side_effect=[
            {"finding": {"outcome": "blocked"}},
            {"finding": {"outcome": "successful"}},
            {"finding": {"outcome": "blocked"}},
        ]
    )

    result = runner.run_repeated(probe=None, trials=3)

    assert len(result["trials"]) == 3
    assert result["repeatability"]["outcome_counts"] == {
        "blocked": 2,
        "successful": 1,
    }
    assert result["repeatability"]["variance_detected"] is True


def test_run_repeated_rejects_zero_trials():
    runner = ProbeRunner.__new__(ProbeRunner)

    with pytest.raises(ValueError, match="trials must be at least 1"):
        runner.run_repeated(probe=None, trials=0)
