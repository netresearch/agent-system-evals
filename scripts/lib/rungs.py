"""How far a trial got, for a case whose ground truth is a matrix of legs.

The mechanical outcome is a switch: every leg green or nothing. That is the
right endpoint -- an upgrade that half works has not happened -- and it is
blind to movement. On the upgrade case the same arm went from never resolving
the dependency, to resolving it and failing to load the suite, to running 719
tests with three errors. All of that reads 0.

So the rungs are recorded beside it, never instead of it. They are read off the
same artefacts and they are exploratory by construction: no run is declared on
them, and a run that improves a rung without reaching the top has still not
passed.

Shared rather than duplicated: `scripts/mechanical-ledger` reports the rungs on
the command line and `scripts/build-site` puts them on the published page, and
two readers of the same artefacts drift apart -- this repository has already
had `run-comparison` and `analyze` disagree about what `skill_invoked` counts.
"""

from __future__ import annotations

import re
from pathlib import Path


def passed(artifacts: Path, check: dict) -> bool:
    """The same reading `scripts/analyze` uses, against one trial's artefacts.

    An absent artefact is a failure rather than a gap: the collector runs
    whatever the agent did, so a missing file means the check could not be
    made, and counting that as anything else invents a pass.
    """
    legs = sorted(artifacts.glob(check["artifacts"]))
    if not legs:
        return False
    return all(
        all(token in leg.read_text(errors="ignore") for token in check["all_of"])
        for leg in legs
    )


RUNGS = (
    "1 no install",       # the manifest did not admit that line
    "2 suite will not load",  # installed; PHPUnit died resolving something
    "3 suite runs",       # tests executed, some failed
    "4 green",            # what mechanical_outcome counts
)
# Whether the *target* leg passed is the question; whether the leg the
# extension already supported still passes is a second one, and pooling them
# answers neither. The first trial ever to pass this case's v14 leg had reached
# v14 by dropping v13 from the manifest, and a pooled reading called the whole
# trial "the suite would not load" -- the opposite of what happened. A pooled
# reading the other way would have called it "some legs green", which is true
# of almost every trial, because the old leg passes until someone breaks it.


def leg_rung(text: str) -> str:
    """Which rung one leg reached, from its own file."""
    # Nothing that says the target was installed puts a leg on the bottom rung,
    # and that includes a collected file with nothing in it. An empty artefact
    # is the same information as a missing one, and reading it as "the suite
    # would not load" would credit the leg with an install it never
    # demonstrated -- the absence-as-evidence mistake this repository keeps
    # finding in its own instruments.
    if not re.search(r"resolve:|^LEG=", text, re.M):
        return RUNGS[0]
    if re.search(r"^RESOLVE=failed", text, re.M) or "INSTALLED=none" in text:
        return RUNGS[0]
    if re.search(r"^LEG=\S+ RESOLVE=ok TESTS=passed", text, re.M):
        return RUNGS[3]
    # A test summary line means PHPUnit got far enough to run something; a
    # fatal or "an error occurred inside PHPUnit" means it did not.
    if re.search(r"^Tests: \d+", text, re.M):
        return RUNGS[2]
    return RUNGS[1]


def rung(artifacts: Path, check: dict) -> str:
    """How far a trial got, per leg rather than pooled.

    The target leg -- the highest version -- decides the rung, and every other
    leg that is not green is appended to it. Where the legs disagree and one of
    them is green, that is said outright, because a trial which passed one
    version and dropped the other is a different failure from one that never
    installed.
    """
    legs = sorted(artifacts.glob(check["artifacts"]))
    if not legs:
        return RUNGS[0]
    if passed(artifacts, check):
        return RUNGS[3]
    # The target is the highest version among the legs; the rest are the ones
    # the extension already supported.
    by_version = {}
    for leg in legs:
        text = leg.read_text(errors="ignore")
        name = re.search(r"matrix-(.+)\.txt$", leg.name)
        by_version[name.group(1) if name else leg.name] = leg_rung(text)
    target = max(by_version, key=lambda v: [int(p) for p in v.split(".")
                                            if p.isdigit()] or [0])
    reached = by_version[target]
    # Any non-target leg that is not green has to survive into the string, not
    # only a dropped one: "target green, the other leg's suite would not load"
    # would otherwise return "4 green" and be filtered out of the table as a
    # clean result.
    broke = {v: r for v, r in by_version.items()
             if v != target and r != RUNGS[3]}
    if broke:
        detail = ", ".join(
            f"dropped {v}" if r == RUNGS[0] else f"{v} {r[2:]}"
            for v, r in sorted(broke.items())
        )
        return f"{reached} + {detail}"
    return reached
