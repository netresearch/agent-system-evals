"""The validity gate: which trials may enter a statistic, and why not.

Each case below is a way a trial can be worthless while leaving a well-formed
number behind. That is the whole point of the gate — none of these crash, and
before it existed every one of them was averaged in as evidence about the
system under test.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "lib"))

import validity  # noqa: E402


def build_trial(
    job: Path,
    name: str = "case__aaa",
    *,
    exception=None,
    agent_finished: bool = True,
    steps: int = 3,
    trajectory: str | None = None,
    rewards: dict | None = None,
    judge_error: bool = False,
    artifacts: list[str] = (),
    mcp_prefix: str | None = None,
) -> Path:
    trial = job / name
    (trial / "verifier").mkdir(parents=True, exist_ok=True)

    result = {
        "exception_info": exception,
        "agent_execution": {"started_at": "t0"},
        "verifier_result": {
            "rewards": {"verification": 1.0} if rewards is None else rewards
        },
    }
    if agent_finished:
        result["agent_execution"]["finished_at"] = "t1"
    (trial / "result.json").write_text(json.dumps(result))

    if trajectory is None:
        body = json.dumps(
            {
                "steps": [
                    {"tool": f"{mcp_prefix or 'Read'}x", "n": i} for i in range(steps)
                ]
            }
        )
    else:
        body = trajectory
    (trial / "verifier" / "trajectory.json").write_text(body)

    details = {
        "verification": [
            {"criteria": [{"name": "c1", "error": "timed out" if judge_error else None}]}
        ]
    }
    (trial / "verifier" / "reward-details.json").write_text(json.dumps(details))

    collected = trial / "artifacts" / "logs" / "artifacts"
    collected.mkdir(parents=True, exist_ok=True)
    for artifact in artifacts:
        (collected / artifact).write_text("")
    return trial


def test_a_complete_trial_is_valid(tmp_path):
    trial = build_trial(tmp_path)
    assert validity.classify(trial).state == validity.VALID


def test_an_exception_is_infrastructure_not_a_score(tmp_path):
    """A rate-limited trial once counted as an arm that failed the work."""
    trial = build_trial(
        tmp_path, exception={"exception_type": "ApiRateLimitError", "m": "429"}
    )
    verdict = validity.classify(trial)
    assert verdict.state == validity.INVALID_INFRASTRUCTURE
    assert "ApiRateLimitError" in verdict.reason


def test_an_agent_that_never_finished_is_not_a_result(tmp_path):
    trial = build_trial(tmp_path, agent_finished=False)
    assert validity.classify(trial).state == validity.INVALID_AGENT


def test_an_empty_trajectory_is_a_recording_failure(tmp_path):
    """Zero steps scores as a run that did nothing — a plausible number."""
    trial = build_trial(tmp_path, steps=0)
    assert validity.classify(trial).state == validity.INVALID_AGENT


def test_an_unparseable_trajectory_is_a_recording_failure(tmp_path):
    trial = build_trial(tmp_path, trajectory="{not json")
    assert validity.classify(trial).state == validity.INVALID_AGENT


def test_an_errored_judge_is_not_a_zero(tmp_path):
    """RewardKit records a failed judge as 0.0, which nothing downstream could
    tell from a criterion the run genuinely failed."""
    trial = build_trial(tmp_path, judge_error=True)
    verdict = validity.classify(trial)
    assert verdict.state == validity.INVALID_JUDGE
    assert "verification/c1" in verdict.reason


def test_a_missing_dimension_is_the_judge_not_the_agent(tmp_path):
    trial = build_trial(tmp_path, rewards={"verification": 1.0})
    verdict = validity.classify(trial, expected_dimensions={"verification", "evidence"})
    assert verdict.state == validity.INVALID_JUDGE
    assert "evidence" in verdict.reason


def test_a_server_that_never_answered_voids_the_arm(tmp_path):
    """A fleet that is nothing but an MCP server, whose server was never
    called, produced trials indistinguishable from a control run."""
    trial = build_trial(tmp_path)
    verdict = validity.classify(trial, snapshot={"mcp_server": "typo3-dev-mcp"})
    assert verdict.state == validity.INVALID_PROVISION


def test_a_server_that_answered_is_valid_even_if_barely(tmp_path):
    trial = build_trial(tmp_path, mcp_prefix="mcp__typo3-dev-mcp__")
    verdict = validity.classify(trial, snapshot={"mcp_server": "typo3-dev-mcp"})
    assert verdict.state == validity.VALID


def test_a_skill_fleet_is_not_voided_by_going_unused(tmp_path):
    """Not using an offered skill is a result — the runtime case's finding.

    Voiding those trials would delete the most interesting thing the benchmark
    has measured.
    """
    trial = build_trial(tmp_path)
    snapshot = {"fleet_declares": {"skills": ["a", "b"]}, "fleet_requested": ["a", "b"]}
    assert validity.classify(trial, snapshot=snapshot).state == validity.VALID


def test_a_collector_that_never_ran_is_named(tmp_path):
    trial = build_trial(tmp_path, artifacts=["git-status.txt"])
    verdict = validity.classify(
        trial, required_artifacts=["git-status.txt", "matrix-14.3.txt"]
    )
    assert verdict.state == validity.INVALID_COLLECTOR
    assert "matrix-14.3.txt" in verdict.reason


def test_an_empty_artifact_is_not_a_failure(tmp_path):
    """A review that correctly changes nothing leaves an empty diff."""
    trial = build_trial(tmp_path, artifacts=["git-diff.patch"])
    assert (
        validity.classify(trial, required_artifacts=["git-diff.patch"]).state
        == validity.VALID
    )


def test_an_unchecked_collector_is_reported(tmp_path):
    verdict = validity.classify(build_trial(tmp_path))
    assert verdict.valid
    assert any("collectors" in note for note in verdict.unchecked)


def test_the_first_failure_upstream_wins(tmp_path):
    """A trial whose agent died says nothing about its collectors.

    Reporting the downstream symptom sends the reader after the wrong cause.
    """
    trial = build_trial(tmp_path, agent_finished=False, judge_error=True)
    assert validity.classify(trial).state == validity.INVALID_AGENT


def test_capability_selection_is_not_applicable_without_an_offer():
    assert (
        validity.dimension_state("capability_selection", {"fleet_requested": []})
        == validity.NOT_APPLICABLE
    )
    assert (
        validity.dimension_state("capability_selection", {"fleet_requested": ["a"]})
        == validity.VALID
    )


def test_an_unrecorded_offer_is_not_an_absent_one():
    """Absence of a field an older run never wrote is not evidence.

    Read that way, the check once reported n/a for a fleet carrying twelve
    skills.
    """
    assert validity.offered_nothing({}) is None


def test_gate_splits_a_job(tmp_path):
    job = tmp_path / "job"
    (job).mkdir()
    (job / "nr-snapshot.json").write_text(json.dumps({"case_id": "X"}))
    build_trial(job, "case__ok")
    build_trial(job, "case__dead", agent_finished=False)
    valid, verdicts = validity.gate(job)
    assert [t.name for t in valid] == ["case__ok"]
    assert len(verdicts) == 2


@pytest.mark.parametrize("state", validity.STATES)
def test_every_state_is_reachable_by_name(state):
    """The vocabulary is fixed; a consumer inventing its own is the bug."""
    assert isinstance(state, str) and state.isupper()
