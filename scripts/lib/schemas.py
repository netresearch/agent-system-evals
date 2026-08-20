"""Typed records for the artefacts this repository writes, with versions.

Everything here used to be a dictionary passed between scripts, and each
consumer decided for itself what a field meant and what to do when it was
absent. That is how a comparison came to read a missing dimension as a failure,
how a regrade carried a rubric identity it no longer had, and how
`offered_nothing` once reported "nothing was provisioned" for a fleet carrying
twelve skills — a field an older run never wrote, read as evidence that the
thing did not exist.

Three properties, in the order they matter:

**A version on every record.** Without one, an old artefact and a new one are
indistinguishable until a consumer trips over a field. With one, a reader can
say "I do not understand this" instead of extracting nothing.

**Migration rather than exclusion.** Ninety-odd recorded jobs predate this and
are the only evidence this project has. A schema that cannot read them is not a
schema, it is a reason to delete history.

**Absent is not false.** Every migration below leaves a field it cannot fill as
`None`, never as a default that reads as a measurement.

Deliberately dataclasses and not pydantic: these are consumed by
`uv run --script` files that declare their own dependencies, and a validation
library in each header is a cost paid on every invocation to check shapes that
this file can check in twenty lines.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# Bump when a writer changes what a record means, not when it adds a field a
# reader can ignore.
SNAPSHOT_VERSION = 1
EXPERIMENT_VERSION = 1
CALIBRATION_VERSION = 1


class UnreadableRecord(RuntimeError):
    """A record this reader does not understand, said out loud.

    Raised rather than returning something empty: an unreadable artefact that
    degrades to zeros is the failure mode this whole file exists to prevent.
    """


@dataclass
class Snapshot:
    """What one job ran, and how it was graded.

    The two are separate on purpose. A regrade replaces `grade` and leaves
    everything else alone; before that separation existed, a job re-scored with
    today's rubric still claimed the rubric that scored it months ago.
    """

    case_id: str | None = None
    fleet: str | None = None
    benchmark_version: str | None = None
    agent: str | None = None
    model: str | None = None
    judge: str | None = None
    trials: int | None = None
    variant: str | None = None
    variant_of: str | None = None
    comparison: dict[str, Any] | None = None
    comparison_digest: str | None = None
    provision: dict[str, Any] | None = None
    provision_digest: str | None = None
    grade: dict[str, Any] | None = None
    fleet_declares: dict[str, Any] | None = None
    fleet_requested: list[str] | None = None
    companion: dict[str, Any] | None = None
    mcp_server: str | None = None
    regraded_from: str | None = None
    schema_version: int = SNAPSHOT_VERSION
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @property
    def graded_alike_fields(self) -> tuple[str, ...]:
        return ("rubric_digest", "judge", "rewardkit")

    @classmethod
    def from_dict(cls, data: dict[str, Any], source: str = "<memory>") -> Snapshot:
        version = data.get("schema_version", 0)
        if version == 0:
            data = migrate_snapshot_v0(data)
        elif version > SNAPSHOT_VERSION:
            raise UnreadableRecord(
                f"{source} declares snapshot schema {version}; this reader "
                f"understands {SNAPSHOT_VERSION}. Update the reader rather than "
                f"guessing at the fields."
            )
        if not data.get("case_id"):
            # Every consumer keys on it. Raised here with the reason rather
            # than surfacing later as a lookup that quietly found nothing.
            raise UnreadableRecord(f"{source} has no case_id")
        known = {f for f in cls.__dataclass_fields__ if f != "raw"}
        return cls(raw=data, **{k: v for k, v in data.items() if k in known})

    @classmethod
    def load(cls, path: Path) -> Snapshot:
        if not path.is_file():
            raise UnreadableRecord(f"no snapshot at {path}")
        try:
            data = json.loads(path.read_text())
        except json.JSONDecodeError as exc:
            raise UnreadableRecord(f"{path} is not valid JSON: {exc}") from exc
        return cls.from_dict(data, str(path))


def migrate_snapshot_v0(data: dict[str, Any]) -> dict[str, Any]:
    """Snapshots written before 20 August 2026.

    They carry no `schema_version` and no `grade` block, because what was run
    and how it was judged were one record then. The grade stays `None` rather
    than being reconstructed: the rubric that scored those jobs is knowable
    from git history and is not knowable from the file, and inventing it here
    would let a comparison believe two jobs were graded alike when nothing
    checked.
    """
    migrated = dict(data)
    migrated["schema_version"] = SNAPSHOT_VERSION
    migrated.setdefault("grade", None)
    return migrated


def stamp(record: dict[str, Any], version: int) -> dict[str, Any]:
    """Put the version first, so a reader sees it before anything else."""
    return {"schema_version": version, **record}
