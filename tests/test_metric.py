"""What the dataset metric must do with imperfect input.

Every case here is a mistake this file actually made. The metric's docstring
promised that a missing dimension would be "reported, not zeroed" and the code
three lines below wrote `0.0` and averaged it in; CI called the file with a
dimension name no case had emitted since the rename and asserted nothing about
the output, so both stood for weeks. An executability check cannot fail in the
direction that matters.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
METRIC = ROOT / "datasets" / "open-forward-reviews" / "metric.py"


def run(rewards: list[dict | None], tmp_path: Path) -> dict:
    source = tmp_path / "rewards.jsonl"
    source.write_text("\n".join(json.dumps(r) for r in rewards) + "\n")
    output = tmp_path / "metric.json"
    subprocess.run(
        [sys.executable, str(METRIC), "-i", str(source), "-o", str(output)],
        check=True,
    )
    return json.loads(output.read_text())


def test_missing_dimension_is_not_a_zero(tmp_path):
    """The failure this file's own docstring warned about, and committed."""
    result = run(
        [
            {"verification": 1.0, "outcome_quality": 1.0},
            {"verification": 1.0},
        ],
        tmp_path,
    )
    assert result["outcome_quality_missing"] == 1
    # One trial scored it, and it scored 1.0. Averaging in a zero for the trial
    # that never produced it would say 0.5 — a system that half worked.
    assert result["outcome_quality"] == 1.0
    assert result["outcome_quality_met"] == 1


def test_dimension_absent_from_every_trial_has_no_value(tmp_path):
    result = run([{"consistency": 1.0}, {"consistency": 0.5}], tmp_path)
    assert "verification" not in result
    assert result["verification_missing"] == 2
    # And what was measured is reported with its own denominator.
    assert result["consistency_n"] == 2


def test_no_figure_averages_across_dimensions(tmp_path):
    """The one number that could be quoted as a score, deliberately absent.

    Ordinal categories mapped to 0/0.5/1 and averaged across dimensions of
    different criterion counts is not a measurement of anything, and a
    disclaimer in a docstring does not travel with the number.
    """
    result = run([{"evidence": 1.0, "authority": 0.5}], tmp_path)
    assert "mean" not in result
    assert "mean_over" not in result
    assert result["evidence"] == 1.0 and result["authority"] == 0.5


def test_trial_without_reward_is_counted_never_averaged(tmp_path):
    result = run([{"evidence": 1.0}, None], tmp_path)
    assert result["trials"] == 1
    assert result["trials_without_reward"] == 1
    assert result["evidence"] == 1.0


def test_unknown_dimension_is_surfaced(tmp_path):
    """A rubric can name a dimension faster than this file learns it.

    `consistency` graded two cases for a week while nothing aggregated it. The
    metric cannot report a dimension it does not know, but it can refuse to
    swallow one.
    """
    result = run([{"evidence": 1.0, "invented_dimension": 1.0}], tmp_path)
    assert result["dimensions_unexpected"] == 1
    assert result["dimensions_unexpected_names"] == "invented_dimension"


def test_met_threshold_excludes_partial_only(tmp_path):
    result = run([{"evidence": 0.5}, {"evidence": 0.75}, {"evidence": 1.0}], tmp_path)
    assert result["evidence_met"] == 2


def test_no_trials_at_all(tmp_path):
    result = run([None], tmp_path)
    assert result["trials"] == 0
    assert result["trials_without_reward"] == 1


def test_the_first_key_is_a_number(tmp_path):
    """Harbor formats the first key of this output with `:.3f`.

    A list or a null there raises a TypeError inside Harbor's progress
    display, which is a long way from the file that caused it.
    """
    result = run([{"evidence": 1.0, "unknown_one": 1.0}], tmp_path)
    first = next(iter(result.values()))
    assert isinstance(first, (int, float)) and not isinstance(first, bool)


@pytest.mark.parametrize("name", ["capability_selection", "consistency"])
def test_current_dimension_names_are_aggregated(name, tmp_path):
    """The rename that the metric slept through, pinned per name."""
    result = run([{name: 1.0}], tmp_path)
    assert result[name] == 1.0
    assert result[f"{name}_met"] == 1


def test_retired_dimension_name_is_not_aggregated(tmp_path):
    result = run([{"skill_routing": 1.0}], tmp_path)
    assert "skill_routing" not in result
    assert result["dimensions_unexpected_names"] == "skill_routing"
