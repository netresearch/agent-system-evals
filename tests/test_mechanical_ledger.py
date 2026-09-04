"""The ledger recomputes a case's ground-truth check from recorded artefacts."""

from __future__ import annotations

import importlib.machinery
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load():
    loader = importlib.machinery.SourceFileLoader(
        "mechanical_ledger", str(ROOT / "scripts" / "mechanical-ledger")
    )
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


def test_a_missing_artefact_is_a_failure_not_a_gap(tmp_path):
    """The collector runs whatever the agent did.

    A missing file means the check could not be made; counting that as anything
    but a failure invents a pass for a trial nobody measured.
    """
    ledger = load()
    check = {"artifacts": "calendar-check.txt", "all_of": ["calendar: ok"]}
    empty = tmp_path / "empty"
    empty.mkdir()
    assert ledger.passed(empty, check) is False

    good = tmp_path / "good"
    good.mkdir()
    (good / "calendar-check.txt").write_text("calendar: ok\n")
    assert ledger.passed(good, check) is True

    bad = tmp_path / "bad"
    bad.mkdir()
    (bad / "calendar-check.txt").write_text("calendar: FAILED\n")
    assert ledger.passed(bad, check) is False


def test_every_leg_must_pass_not_just_one(tmp_path):
    """`matrix-*.txt` is several legs, and a partial upgrade is not an upgrade."""
    ledger = load()
    check = {"artifacts": "matrix-*.txt", "all_of": ["resolve: ok"]}
    d = tmp_path / "legs"
    d.mkdir()
    (d / "matrix-13.4.txt").write_text("resolve: ok\n")
    (d / "matrix-14.3.txt").write_text("resolve: failed\n")
    assert ledger.passed(d, check) is False
    (d / "matrix-14.3.txt").write_text("resolve: ok\n")
    assert ledger.passed(d, check) is True


def test_the_declared_cases_are_read_from_the_task_files():
    """Ten cases declare one; the ledger must find them without a hardcoded list."""
    declared = load().declarations()
    assert "OFR-TYPO3-UPGRADE-001" in declared
    assert declared["OFR-TYPO3-UPGRADE-001"]["artifacts"] == "matrix-*.txt"
    # A case without the block is absent rather than present-and-empty.
    assert "OFR-TYPO3-CONSISTENT-001" not in declared


def test_a_trial_that_never_ran_is_not_a_failure(tmp_path):
    """Counting invalid trials turned a rate-limited night into six failures.

    Six control trials from 19 August raised ApiRateLimitError, spent zero
    tokens and produced no transcript. Counted, they took the arm from 4/6 to
    4/10 and the comparison from p 0.14 to p 0.011 -- the difference between a
    direction and a headline.
    """
    ledger = load()
    job = tmp_path / "OFR-TYPO3-CALENDAR-001-nr-20260819-000000"
    (job / "x").mkdir(parents=True)
    (job / "nr-snapshot.json").write_text(
        json.dumps({"case_id": "OFR-TYPO3-CALENDAR-001", "fleet": "nr",
                    "model": "claude-opus-5"})
    )
    (job / "x" / "result.json").write_text(
        json.dumps({"exception_info": {"exception_type": "ApiRateLimitError"}})
    )
    art = job / "x" / "artifacts" / "logs" / "artifacts"
    art.mkdir(parents=True)
    assert ledger.ledger(tmp_path) == {}
