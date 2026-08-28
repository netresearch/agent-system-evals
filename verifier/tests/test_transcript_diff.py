"""The judge's transcript ends with the collected diff (instrument failure 23).

Asserted through the same function the verifier calls, against the recorded
fixtures: `modified` collected a diff, `nop` did not.
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

FIXTURES = Path(__file__).resolve().parent / "fixtures"


def load(fixture: str):
    import os
    os.environ["NREVAL_TRAJECTORY"] = str(FIXTURES / fixture / "logs" / "trajectory.json")
    os.environ["NREVAL_ARTIFACTS"] = str(FIXTURES / fixture / "logs" / "artifacts")
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "common"))
    import nreval
    return importlib.reload(nreval)


def test_modified_fixture_transcript_carries_its_diff():
    nreval = load("modified")
    text = nreval.transcript()
    assert "## Working tree after the run" in text
    patch = (FIXTURES / "modified" / "logs" / "artifacts" / "git-diff.patch").read_text()
    header = next(l for l in patch.splitlines() if l.startswith("diff --git "))
    assert header in text, "the diff has to reach the judge verbatim, not summarised"
    # It is the last thing the judge reads, after the final answer and the steps.
    assert text.rstrip().endswith(patch.rstrip()[-40:])


def test_nop_fixture_says_the_diff_is_empty():
    """An empty collected diff is a finding — the agent changed nothing — and
    the judge is told so rather than left to infer it from silence. Only an
    absent artifact yields no section: that is a run with no collector, which
    is a different thing from a run that collected nothing."""
    nreval = load("nop")
    text = nreval.transcript()
    assert "## Working tree after the run" in text
    assert "(no changes" in text


def test_no_artifact_means_no_section(tmp_path, monkeypatch):
    nreval = load("nop")
    monkeypatch.setattr(nreval, "ARTIFACTS_DIR", str(tmp_path))
    assert nreval.collected_diff_section() == ""


def test_the_blind_transcript_carries_it_too(tmp_path):
    nreval = load("modified")
    out = nreval.write_blind_transcript(tmp_path / "blind.txt")
    assert "## Working tree after the run" in out.read_text()


def test_a_long_diff_is_cut_with_the_cut_marked(tmp_path, monkeypatch):
    nreval = load("modified")
    artifacts = tmp_path / "artifacts"; artifacts.mkdir()
    (artifacts / "git-diff.patch").write_text("+++ b/x\n" + "+line\n" * 20_000)
    monkeypatch.setattr(nreval, "ARTIFACTS_DIR", str(artifacts))
    section = nreval.collected_diff_section()
    assert "[cut:" in section and len(section) < nreval.DIFF_LIMIT + 400
