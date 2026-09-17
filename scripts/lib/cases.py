"""Find a case and read what it declares.

Every consumer used to locate cases its own way — a glob here, a `case_id`
comparison there — and each one decided independently what a case grades. The
declarations live in `task.toml`; this reads them once.
"""

from __future__ import annotations

import sys
from functools import cache
from pathlib import Path

import tomllib

ROOT = Path(__file__).resolve().parents[2]

sys.path.insert(0, str(Path(__file__).resolve().parent))
from dimensions import ids_for  # noqa: E402  (after the path insert, by necessity)


@cache
def by_id(case_id: str) -> Path | None:
    for path in sorted(ROOT.glob("tasks/*/*/task.toml")):
        config = tomllib.loads(path.read_text())
        if config.get("metadata", {}).get("case_id") == case_id:
            return path.parent
    return None


@cache
def metadata(case_id: str) -> dict:
    case_dir = by_id(case_id)
    if case_dir is None:
        return {}
    return tomllib.loads((case_dir / "task.toml").read_text()).get("metadata", {})


def graded_dimensions(case_id: str) -> set[str]:
    """What this case's rubric produces.

    Declared where a case grades fewer than the open eight, so that no
    comparison mixes rubrics silently and no aggregation reports a dimension
    the case never had.
    """
    meta = metadata(case_id)
    if meta.get("dimensions"):
        return set(meta["dimensions"])
    if meta.get("contract"):
        return set(ids_for("contract"))
    return set(ids_for("open"))


def required_artifacts(case_id: str) -> list[str]:
    return list(metadata(case_id).get("required_artifacts") or [])


def check_ran_markers(case_id: str) -> tuple[str, list[str]]:
    """The artefact a case is graded from, and what proves the check ran.

    A collector redirects into its file before doing anything, so the file
    exists whether the check completed or died in its first second. Those two
    look identical to a gate that tests existence, and the second one grades
    every arm at zero — a crashed check reads as a clean null result, which is
    how a round on OFR-TYPO3-RESIZE-001 came to report 0 of 3 against 0 of 3
    after the functional suite ran out of memory three tests in
    (docs/instrument-failures.md 33).

    The case says what its own evidence of having run looks like, under
    `[metadata.mechanical_outcome] ran_if`. Absent, nothing is checked: this is
    a statement only the case can make, and a generic content rule over
    artefacts would fail the cases whose correct result is an empty file.
    """
    outcome = metadata(case_id).get("mechanical_outcome") or {}
    return str(outcome.get("artifacts") or ""), list(outcome.get("ran_if") or [])
