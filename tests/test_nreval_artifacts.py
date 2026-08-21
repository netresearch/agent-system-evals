"""Absence of a collected artifact is agent behaviour, not broken infrastructure.

The distinction this file pins was learned the expensive way. `nr_artifact_matches`
used to raise when an artifact was missing, on the reasoning that a collector
which did not run is an infrastructure failure and must not be scored against the
agent. That reasoning holds for a verdict file the collector always writes, and
fails completely for a `cp` of a file the agent may never create — `cp` leaves no
target when its source is missing.

The documentation case hit it on its first trial: the agent wrote no
`Documentation/guides.xml`, so `guides.after.xml` was absent, the criterion
raised, RewardKit aborted the entire reward, and `scripts/trial-validity`
recorded `INVALID_INFRASTRUCTURE`. A plain agent shortcoming had erased the
measurement of itself — the one failure mode this repository exists to avoid.

Which question a case wants answered is now declared rather than inferred:
`metadata.required_artifacts` names what must exist, and the validity gate voids
the trial by name when it does not.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def load_nreval(artifacts: Path):
    """Import a fresh copy bound to `artifacts`.

    ARTIFACTS_DIR is read at import time, so a plain import would bind whatever
    the previous test left behind and the assertions would silently describe the
    wrong directory.
    """
    spec = importlib.util.spec_from_file_location(
        "nreval_under_test", ROOT / "verifier" / "common" / "nreval.py"
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules["nreval_under_test"] = module
    spec.loader.exec_module(module)
    module.ARTIFACTS_DIR = str(artifacts)
    return module


@pytest.fixture()
def nreval(tmp_path):
    artifacts = tmp_path / "artifacts"
    artifacts.mkdir()
    module = load_nreval(artifacts)
    module.ARTIFACTS = artifacts
    return module


def test_present_and_matching(nreval, tmp_path):
    (Path(nreval.ARTIFACTS_DIR) / "docs-check.txt").write_text("docs: ok\n")
    assert nreval.nr_artifact_matches(tmp_path, "docs-check.txt", r"docs: ok")


def test_present_and_not_matching(nreval, tmp_path):
    (Path(nreval.ARTIFACTS_DIR) / "docs-check.txt").write_text("docs: incomplete\n")
    assert not nreval.nr_artifact_matches(tmp_path, "docs-check.txt", r"docs: ok")


def test_absent_is_false_not_an_exception(nreval, tmp_path):
    """The regression pin. Before the fix this raised MissingEvidence."""
    assert not nreval.nr_artifact_matches(tmp_path, "guides.after.xml", r"anything")


def test_trajectory_absence_still_raises(nreval, tmp_path):
    """The other half of the rule, so the fix cannot be read as "never raise".

    A missing trajectory really is a broken run: no collector produces it
    conditionally on what the agent did, and scoring it zero would report a
    perfect failure for a harness that never started.
    """
    nreval.TRAJECTORY_PATH = str(tmp_path / "nope.json")
    with pytest.raises(nreval.MissingEvidence):
        nreval.load_trajectory()
