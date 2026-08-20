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
