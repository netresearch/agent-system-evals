"""The calibration reads criteria, not only dimensions, and gates on them.

Issue #9 asked for the test-retest spread *per criterion*. The first
calibration reported it per dimension, because the script read reward.json
and not reward-details.json — so it could say `evidence` was noisy without
saying which of its criteria was, which is the only thing a rubric author can
act on.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(script: str):
    # The scripts have no .py suffix, and spec_from_file_location then finds
    # no loader; name the source loader explicitly.
    from importlib.machinery import SourceFileLoader

    loader = SourceFileLoader(script.replace("-", "_"), str(ROOT / "scripts" / script))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


EXPECTED = {"evidence": {"read_manifest": 1.0, "findings_anchored": 0.5, "no_guesswork": 0.0}}

# A job directory: one block per kind.
JOB_SHAPE = {
    "evidence": [
        {"kind": "programmatic", "score": 1.0,
         "criteria": [{"name": "read_manifest", "value": 1.0, "raw": True}]},
        {"kind": "agent", "score": 0.5,
         "criteria": [{"name": "findings_anchored", "value": 0.5, "raw": 2},
                      {"name": "no_guesswork", "value": 0.0, "raw": 1}]},
    ]
}

# `rewardkit --output`, which is how the calibration runs it: one object.
OUTPUT_SHAPE = {
    "evidence": {"score": 0.5, "criteria": [
        {"name": "read_manifest", "value": 1.0, "raw": True},
        {"name": "findings_anchored", "value": 0.5, "raw": 2},
        {"name": "no_guesswork", "value": 0.0, "raw": 1},
    ]}
}


def test_criterion_values_reads_the_job_shape():
    assert load("calibrate-judges").criterion_values(JOB_SHAPE) == EXPECTED


def test_criterion_values_reads_the_output_shape():
    """The shape the calibration actually meets, and the one it crashed on.

    Iterating a per-dimension object as if it were a list of blocks walks its
    keys and calls `.get` on the string "score". That killed a recalibration
    twenty judge calls in, and left the report describing the previous rubric —
    which the gate then correctly refused, so the failure was at least loud.
    """
    assert load("calibrate-judges").criterion_values(OUTPUT_SHAPE) == EXPECTED


def test_summarise_reports_spread_as_max_minus_min():
    calibrate = load("calibrate-judges")
    s = calibrate.summarise([0.5, 1.0, 0.5], expected=0.6)
    assert s == {"values": [0.5, 1.0, 0.5], "median": 0.5, "spread": 0.5, "expected": 0.6}


def test_gate_fails_on_a_noisy_criterion_inside_a_quiet_dimension(tmp_path, monkeypatch):
    """The counter-probe. A dimension whose average is steady while one of its
    criteria flips every repeat must fail, because the average is what hid it."""
    labels = (ROOT / "calibration" / "gold" / "labels.toml").read_text()
    (tmp_path / "calibration" / "gold").mkdir(parents=True)
    (tmp_path / "calibration" / "gold" / "labels.toml").write_text(labels)
    # The gate checks the gold fixtures exist before reading the report; the
    # test is about the report, so the fixtures are directories and nothing else.
    import tomllib
    for spec in tomllib.loads(labels)["fixture"].values():
        (tmp_path / spec["fixture"]).mkdir(parents=True, exist_ok=True)
    report = {
        "schema_version": 1, "case": "no-such-case", "rubric_digest": "x", "repeats": 3,
        "fixtures": {"thorough": {"evidence": {
            "values": [0.75, 0.75, 0.75], "median": 0.75, "spread": 0.0, "expected": None,
            "criteria": {
                "steady": {"values": [1.0, 1.0, 1.0], "median": 1.0, "spread": 0.0, "expected": None},
                "flipping": {"values": [0.0, 1.0, 0.0], "median": 0.0, "spread": 1.0, "expected": None},
            }}}},
    }
    (tmp_path / "calibration" / "report.json").write_text(json.dumps(report))
    script = (ROOT / "scripts" / "check-calibration").read_text().replace(
        "ROOT = Path(__file__).resolve().parents[1]", f"ROOT = Path({str(tmp_path)!r})"
    )
    (tmp_path / "check").write_text(script)
    result = subprocess.run([sys.executable, str(tmp_path / "check")], capture_output=True, text=True)
    assert result.returncode == 1, result.stdout + result.stderr
    assert "thorough/evidence/flipping" in result.stderr
    assert "steady" not in result.stderr


def test_analyze_marks_a_count_that_sits_on_the_threshold(tmp_path):
    """A met-count whose scores straddle the threshold is instrument noise.

    Measured twice on identical input: dimension measurements whose median sat
    within one judge step of 0.75 flipped their verdict in 7 of 12 cases,
    against 1 of 20 further away (instrument failure 24). `scripts/analyze`
    marks such a count so a reader does not take it for a difference.
    """
    analyze = load("analyze")
    assert abs(analyze.BOUNDARY - 1 / 6) < 1e-9, "the margin is one judge step"
    # 0.75 exactly, and one step either side.
    on = [analyze.MET, analyze.MET - 0.125, analyze.MET + 0.125]
    assert all(abs(v - analyze.MET) < analyze.BOUNDARY for v in on)
    # Two steps away is not on the boundary.
    assert not any(
        abs(v - analyze.MET) < analyze.BOUNDARY
        for v in (analyze.MET - 0.25, analyze.MET + 0.25)
    )
