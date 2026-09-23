"""A record carries its trials, and reading them agrees with reading jobs/.

Instrument failure 35: a record named its jobs and held nothing per trial, so
a removed worktree left a record that could be named and not analysed.
`scripts/analyze --write-inline` writes every per-trial value the analysis
reads into the record; `InlineArm` reads them back when the job directories
are gone. These tests pin that the two readings agree and that a record with
no jobs on disk analyses from its inline trials alone.
"""

from __future__ import annotations

import importlib.machinery
import importlib.util
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CASE = "OFR-TYPO3-REGISTRATION-001"  # graded on outcome_quality, has a mechanical check


def load_analyze():
    loader = importlib.machinery.SourceFileLoader(
        "analyze", str(ROOT / "scripts" / "analyze")
    )
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


def make_trial(
    root: Path, name: str, cost: float, score: float, skill: bool, passed: bool
) -> Path:
    trial = root / "job-x" / name
    (trial / "verifier").mkdir(parents=True)
    (trial / "artifacts" / "logs" / "artifacts").mkdir(parents=True)
    (trial / "result.json").write_text(
        json.dumps(
            {"agent_result": {"cost_usd": cost, "n_input_tokens": int(cost * 1e6)}}
        )
    )
    (trial / "verifier" / "reward.json").write_text(
        json.dumps({"outcome_quality": score})
    )
    calls = [{"function_name": "Bash"}] + (
        [{"function_name": "Skill"}] if skill else []
    )
    (trial / "verifier" / "trajectory.json").write_text(
        json.dumps(
            {
                "steps": [
                    {"tool_calls": calls},
                    {"tool_calls": [{"function_name": "Read"}]},
                ]
            }
        )
    )
    (trial / "verifier" / "reward-details.json").write_text(
        json.dumps(
            {
                "outcome_quality": [
                    {"criteria": [{"value": 1.0}, {"value": 0.5}, {"value": 0.0}]}
                ]
            }
        )
    )
    (trial / "artifacts" / "logs" / "artifacts" / "validation-check.txt").write_text(
        "validation: ok\n" if passed else "validation: incomplete\n"
    )
    return trial


def disk_arm(analyze, tmp_path: Path):
    arm = object.__new__(analyze.Arm)
    arm.name = "nr"
    arm.case_id = CASE
    arm.jobs = [tmp_path / "job-x"]
    arm.snapshot = {"case_id": CASE}
    arm.excluded = ["job-x/t9: INVALID_AGENT: none"]
    arm.trials = [
        make_trial(tmp_path, "t1", 0.12, 0.75, True, True),
        make_trial(tmp_path, "t2", 0.34, 0.25, False, False),
        make_trial(tmp_path, "t3", 0.56, 0.5, True, False),
    ]
    return arm


def test_every_reading_agrees_between_disk_and_inline(tmp_path):
    analyze = load_analyze()
    disk = disk_arm(analyze, tmp_path)
    inline = analyze.InlineArm("nr", analyze.inline_arm(disk))

    assert inline.rewards() == disk.rewards()
    assert inline.scores("outcome_quality") == disk.scores("outcome_quality")
    assert inline.cost() == disk.cost()
    assert inline.cost("n_input_tokens") == disk.cost("n_input_tokens")
    assert inline.tool_calls() == disk.tool_calls()
    assert inline.invoked_skill() == disk.invoked_skill()
    assert inline.mechanical() == disk.mechanical() == [1.0, 0.0, 0.0]
    assert inline.categories("outcome_quality") == disk.categories("outcome_quality")
    assert inline.excluded == disk.excluded
    assert len(inline.trials) == len(disk.trials)


def test_inline_data_survives_json(tmp_path):
    """What is written is JSON; what is read back must still agree."""
    analyze = load_analyze()
    disk = disk_arm(analyze, tmp_path)
    data = json.loads(json.dumps(analyze.inline_arm(disk)))
    inline = analyze.InlineArm("nr", data)
    assert inline.cost() == disk.cost()
    assert inline.categories("outcome_quality") == disk.categories("outcome_quality")


def test_a_record_without_jobs_on_disk_analyses_from_its_inline_trials(tmp_path):
    analyze = load_analyze()
    disk = disk_arm(analyze, tmp_path)
    arms = {}
    for name, digest in (("control", "a" * 12), ("nr", "b" * 12)):
        data = json.loads(json.dumps(analyze.inline_arm(disk)))
        data["snapshot"] = {
            "case_id": CASE,
            "agent": "claude-code",
            "model": "m",
            "judge": "j",
            "provision_digest": digest,
        }
        arms[name] = data
    record = tmp_path / "record.json"
    record.write_text(
        json.dumps(
            {
                "case": CASE,
                "primary_endpoint": "mechanical_outcome",
                "jobs": {"control": ["jobs/gone-control"], "nr": ["jobs/gone-nr"]},
                "inline": {"version": analyze.INLINE_VERSION, "arms": arms},
            }
        )
    )
    result = subprocess.run(
        [str(ROOT / "scripts" / "analyze"), str(record)],
        capture_output=True,
        check=False,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "source    the record's inline trials" in result.stdout
    assert "control: 3 valid of 4" in result.stdout


def test_a_missing_job_without_inline_trials_names_the_repair(tmp_path):
    record = tmp_path / "record.json"
    record.write_text(
        json.dumps(
            {
                "case": CASE,
                "jobs": {"control": ["jobs/gone-control"], "nr": ["jobs/gone-nr"]},
            }
        )
    )
    result = subprocess.run(
        [str(ROOT / "scripts" / "analyze"), str(record)],
        capture_output=True,
        check=False,
        text=True,
    )
    assert result.returncode != 0
    message = " ".join((result.stdout + result.stderr).split())
    assert "job directory missing" in message
    assert "carries no inline trials" in message
    assert "--write-inline" in message


def test_the_runner_writes_inline_trials_at_the_end_of_every_run():
    source = (ROOT / "scripts" / "run-comparison").read_text()
    assert '"--write-inline", str(log)' in source
