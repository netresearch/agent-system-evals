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


def test_trajectory_is_searched_across_candidate_paths(tmp_path, monkeypatch):
    """The verifier's trajectory location is not fixed.

    A separate verifier receives the trajectory only as a collected artifact,
    under the artifact tree rather than at its original path. Searching a list
    keeps a layout change from presenting itself as a missing trajectory, which
    would read as a broken run.
    """
    monkeypatch.setattr(nreval, "TRAJECTORY_PATH", "")
    present = tmp_path / "second" / "trajectory.json"
    present.parent.mkdir(parents=True)
    # A minimal *valid* trajectory: an empty `steps` list is now refused,
    # because an agent phase that recorded nothing is a broken run and grading
    # it reports a perfect zero.
    present.write_text(
        '{"schema_version": "ATIF-v1.7", "steps": [{"step_id": 1}]}'
    )

    monkeypatch.setattr(
        nreval,
        "TRAJECTORY_CANDIDATES",
        (str(tmp_path / "first" / "trajectory.json"), str(present)),
    )
    assert nreval.resolve_trajectory_path() == present
    assert nreval.load_trajectory()["schema_version"] == "ATIF-v1.7"


def test_no_candidate_raises_with_the_reason(tmp_path, monkeypatch):
    monkeypatch.setattr(nreval, "TRAJECTORY_PATH", "")
    monkeypatch.setattr(
        nreval, "TRAJECTORY_CANDIDATES", (str(tmp_path / "nowhere.json"),)
    )
    with pytest.raises(nreval.MissingEvidence, match="declares /logs/agent"):
        nreval.resolve_trajectory_path()


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


def test_transcript_is_bounded(use_fixture):
    """The judge's input has a ceiling.

    An agent judge pages through what it is given. Handed the raw trajectory it
    spent 40 turns and then exited, taking the whole verifier run with it. The
    bound is the fix, so it has to hold.
    """
    traj = use_fixture("thorough")
    rendered = nreval.transcript(traj, budget=500)
    assert len(rendered) < 1500  # the last emitted chunk may overshoot slightly
    assert "truncated" in rendered


def test_transcript_always_carries_the_whole_final_answer(use_fixture):
    """The report survives any budget, because most dimensions grade it.

    It sits at the end of the trajectory, which is where a running budget and a
    per-message cap both eat it. Capped at 4000 characters, an 8000-character
    report reached the judges as half a sentence and every report-shaped
    dimension collapsed. So it is reserved and rendered whole.
    """
    traj = use_fixture("thorough")
    complete = nreval.final_answer(traj)
    for budget in (100, 2_000, 120_000):
        rendered = nreval.transcript(traj, budget=budget)
        assert complete in rendered, f"final answer lost at budget {budget}"
        assert "FINAL ANSWER (complete)" in rendered


def test_transcript_carries_the_gradable_evidence(use_fixture):
    traj = use_fixture("thorough")
    rendered = nreval.transcript(traj)
    assert "composer.json" in rendered          # a path that was read
    assert "phpstan" in rendered                # a command that was run
    assert "What needs attention" in rendered   # the final answer
    assert "automated-assessment" in rendered   # a skill that was invoked


def test_transcript_never_carries_reasoning(use_fixture):
    """Same rule as everywhere else: only observable behaviour is graded."""
    for name in ("thorough", "nop"):
        traj = use_fixture(name)
        rendered = nreval.transcript(traj)
        assert "must never be graded" not in rendered
        assert "I will answer directly" not in rendered


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


# --------------------------------------------------------------------------
# schema guard
#
# Every extractor in nreval ends in `.get("steps") or []`, so any shape this
# reader does not understand degrades to an empty trajectory: no commands, no
# reads, no skills, no final answer. That scores as an agent that did nothing —
# a complete, well-formed, entirely wrong vector, and the failure mode nothing
# downstream can detect. These are the shapes that used to pass silently.
# --------------------------------------------------------------------------


def test_a_future_schema_version_is_refused_not_read_as_idleness():
    with pytest.raises(nreval.MissingEvidence) as excinfo:
        nreval.validate_trajectory({"schema_version": "ATIF-v2.0", "steps": []})
    assert "ATIF-v2.0" in str(excinfo.value)


def test_the_current_schema_version_is_accepted():
    traj = {"schema_version": "ATIF-v1.7", "steps": [{"step_id": 1}]}
    assert nreval.validate_trajectory(traj) is traj


def test_a_renamed_steps_key_is_refused():
    """What a format change looks like: everything else intact."""
    with pytest.raises(nreval.MissingEvidence):
        nreval.validate_trajectory({"schema_version": "ATIF-v1.7", "events": []})


def test_a_trajectory_with_no_steps_is_refused():
    with pytest.raises(nreval.MissingEvidence):
        nreval.validate_trajectory({"schema_version": "ATIF-v1.7", "steps": []})


def test_a_list_at_the_top_level_is_refused():
    with pytest.raises(nreval.MissingEvidence):
        nreval.validate_trajectory([{"step_id": 1}])


def test_a_step_that_is_not_an_object_is_refused():
    with pytest.raises(nreval.MissingEvidence):
        nreval.validate_trajectory(
            {"schema_version": "ATIF-v1.7", "steps": ["step one"]}
        )


def test_restructured_tool_calls_are_refused():
    with pytest.raises(nreval.MissingEvidence):
        nreval.validate_trajectory(
            {
                "schema_version": "ATIF-v1.7",
                "steps": [{"step_id": 1, "tool_calls": {"0": {}}}],
            }
        )


def test_a_trajectory_without_a_declared_version_is_still_read():
    """Fixtures predate the field; refusing them would gate on the wrong thing."""
    traj = {"steps": [{"step_id": 1}]}
    assert nreval.validate_trajectory(traj) is traj


# --------------------------------------------------------------------------
# ran versus worked
# --------------------------------------------------------------------------


def _with_result(command, *, is_error=False, content=""):
    return {
        "schema_version": "ATIF-v1.7",
        "steps": [
            {
                "step_id": 1,
                "tool_calls": [
                    {
                        "tool_call_id": "c1",
                        "function_name": "Bash",
                        "arguments": {"command": command},
                    }
                ],
                "observation": {
                    "results": [
                        {
                            "source_call_id": "c1",
                            "content": content,
                            "extra": {"tool_result_is_error": is_error},
                        }
                    ]
                },
            }
        ],
    }


def test_a_command_that_ran_is_not_a_command_that_worked():
    """`ran_command` is True either way; the dimension's question is not."""
    failed = _with_result("vendor/bin/phpstan analyse", is_error=True)
    assert nreval.ran_command("phpstan", failed)
    assert not nreval.ran_command_successfully("phpstan", failed)


def test_a_successful_command_is_reported_as_such():
    ok = _with_result("vendor/bin/phpstan analyse", content="No errors")
    assert nreval.ran_command_successfully("phpstan", ok)
    assert nreval.failed_commands(ok) == []


def test_an_exit_code_in_the_output_counts_as_failure():
    """The harness prefixes non-zero shell output with `Exit code N`."""
    traj = _with_result("composer update", content="Exit code 2\nconflict")
    assert nreval.command_results(traj)[0]["exit_code"] == 2
    assert not nreval.ran_command_successfully("composer", traj)


def test_an_unrecorded_exit_code_is_none_never_zero():
    """Absence of a status must not be read as success."""
    traj = _with_result("ls", content="a\nb")
    assert nreval.command_results(traj)[0]["exit_code"] is None
    assert nreval.command_results(traj)[0]["failed"] is False
