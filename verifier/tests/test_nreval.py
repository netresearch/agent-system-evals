"""Verifier self-test (ADR 0003).

An open case has no oracle, so nothing proves the case is sound by solving it.
What can be proved is that the verifier discriminates: that it reports
different things about a thorough run, a shallow one, and one that did nothing.
A verifier that scores all three alike would report a healthy system forever.

These tests are also the guard on the evidence extraction itself. Every
mechanical criterion in the rubric rests on this library, so a silent
regression here would move scores without any rubric change.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "common"))

import nreval  # noqa: E402

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def use_fixture(monkeypatch):
    """Point the library at a fixture instead of the live container paths."""

    def _use(name: str):
        base = FIXTURES / name / "logs"
        monkeypatch.setattr(nreval, "TRAJECTORY_PATH", str(base / "trajectory.json"))
        monkeypatch.setattr(nreval, "ARTIFACTS_DIR", str(base / "artifacts"))
        return nreval.load_trajectory()

    return _use


# --------------------------------------------------------------------------
# discrimination: the three runs must not look alike
# --------------------------------------------------------------------------


def test_thorough_run_shows_investigation(use_fixture):
    traj = use_fixture("thorough")
    assert nreval.read_path_matching(r"composer\.json", traj)
    assert nreval.read_path_matching(r"Classes/.*\.php", traj)
    assert nreval.ran_command(r"phpstan", traj)
    assert nreval.ran_command(r"phpunit|ci:test:php:unit", traj)


def test_nop_run_shows_nothing(use_fixture):
    traj = use_fixture("nop")
    assert nreval.commands(traj) == []
    assert nreval.read_paths(traj) == []
    assert nreval.skills_used(traj) == []
    # The failure mode this fixture represents: a confident answer with no work
    # behind it. If it ever satisfies a mechanical criterion, that criterion is
    # measuring the wrong thing.
    assert "everything looks good" in nreval.final_answer(traj).lower()


def test_shallow_run_sits_between(use_fixture):
    traj = use_fixture("shallow")
    assert nreval.read_path_matching(r"composer\.json", traj)
    assert not nreval.ran_command(r"phpstan", traj)
    assert not nreval.read_path_matching(r"Classes/", traj)


# --------------------------------------------------------------------------
# extraction details that criteria depend on
# --------------------------------------------------------------------------


def test_shell_reads_count_as_reads(use_fixture):
    """`cat foo` reads foo as surely as a Read tool call.

    Missing this would understate context discovery for terminal-first agents,
    which is a portability bug, not a scoring preference.
    """
    traj = use_fixture("thorough")
    assert nreval.read_path_matching(r"ext_emconf\.php", traj)


def test_multiple_tool_calls_in_one_step_are_all_seen(use_fixture):
    """Step 3 issues two commands; both must be recorded."""
    traj = use_fixture("thorough")
    commands = nreval.commands(traj)
    assert any("phpstan" in c for c in commands)
    assert any("unit" in c for c in commands)


def test_skills_are_extracted(use_fixture):
    traj = use_fixture("thorough")
    assert "automated-assessment" in nreval.skills_used(traj)
    assert nreval.used_skill(r"assessment|conformance", traj)


def test_final_answer_is_the_last_substantive_message(use_fixture):
    traj = use_fixture("thorough")
    answer = nreval.final_answer(traj)
    assert answer.startswith("## What needs attention")


def test_reasoning_content_is_never_read(use_fixture):
    """Private reasoning must not reach any graded surface.

    Both fixtures carry reasoning_content; nothing the library exposes may
    contain it. See docs/open-forward-review.md section 5.
    """
    for name in ("thorough", "nop"):
        traj = use_fixture(name)
        surfaces = [
            nreval.final_answer(traj),
            " ".join(nreval.agent_messages(traj)),
            " ".join(nreval.commands(traj)),
            " ".join(nreval.observations(traj)),
        ]
        for surface in surfaces:
            assert "must never be graded" not in surface
            assert "I will answer directly" not in surface


# --------------------------------------------------------------------------
# artifacts
# --------------------------------------------------------------------------


def test_clean_tree_is_reported_clean(use_fixture):
    use_fixture("thorough")
    assert not nreval.workspace_modified()


def test_modified_tree_is_detected(use_fixture):
    """The scope-discipline check must be able to fail.

    A criterion that cannot fail is not evidence, so the fixture pair exists to
    prove this one can.
    """
    use_fixture("modified")
    assert nreval.workspace_modified()


# --------------------------------------------------------------------------
# infrastructure failure must not look like agent failure
# --------------------------------------------------------------------------


def test_missing_trajectory_raises(monkeypatch):
    monkeypatch.setattr(nreval, "TRAJECTORY_PATH", "/nonexistent/trajectory.json")
    with pytest.raises(nreval.MissingEvidence):
        nreval.load_trajectory()


def test_corrupt_trajectory_raises(tmp_path, monkeypatch):
    broken = tmp_path / "trajectory.json"
    broken.write_text("{not json")
    monkeypatch.setattr(nreval, "TRAJECTORY_PATH", str(broken))
    with pytest.raises(nreval.MissingEvidence):
        nreval.load_trajectory()


def test_missing_artifact_raises(use_fixture, monkeypatch):
    use_fixture("thorough")
    monkeypatch.setattr(nreval, "ARTIFACTS_DIR", "/nonexistent")
    with pytest.raises(nreval.MissingEvidence):
        nreval.git_status()


# --------------------------------------------------------------------------
# manifest
# --------------------------------------------------------------------------


def test_manifest_is_complete_and_written(use_fixture, tmp_path):
    use_fixture("thorough")
    manifest = nreval.evidence_manifest()
    assert manifest["trajectory"]["agent"] == "claude-code"
    assert manifest["trajectory"]["steps"] == 7
    assert manifest["commands"]
    assert manifest["skills_used"] == ["automated-assessment"]
    assert manifest["git"]["modified"] is False

    out = nreval.write_evidence_manifest(tmp_path / "evidence-manifest.json")
    assert out.exists()
    assert "What needs attention" in out.read_text()
