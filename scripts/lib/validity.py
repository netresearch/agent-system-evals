"""One state per trial, decided once, read by everything that aggregates.

A trial can fail as infrastructure, as provisioning, as a dead agent, as a
missing collector or as an errored judge — and it can be perfectly fine and
simply not applicable to a dimension. Before this module each consumer invented
its own answer: `compare` read a missing dimension as a failure, `metric.py`
scored it zero against its own docstring, and a judge that errored was recorded
by RewardKit as `0.0`, which is a number the system under test never earned.

The rule this enforces: **only `VALID` enters a statistic.** Everything else is
reported by reason and never silently replaced, because a failed trial that
gets quietly re-run is a sample chosen by its outcome.

The checks run most-upstream first and the first failure wins. A trial whose
agent never started has nothing to say about its collectors, and reporting the
downstream symptom would send the reader after the wrong cause.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

VALID = "VALID"
INVALID_INFRASTRUCTURE = "INVALID_INFRASTRUCTURE"
INVALID_PROVISION = "INVALID_PROVISION"
INVALID_AGENT = "INVALID_AGENT"
INVALID_COLLECTOR = "INVALID_COLLECTOR"
INVALID_JUDGE = "INVALID_JUDGE"

STATES = (
    VALID,
    INVALID_INFRASTRUCTURE,
    INVALID_PROVISION,
    INVALID_AGENT,
    INVALID_COLLECTOR,
    INVALID_JUDGE,
)

# A dimension-level state, not a trial-level one: an arm offered nothing had no
# capability decision to get right, and scoring it zero inflates every
# comparison against a control.
NOT_APPLICABLE = "NOT_APPLICABLE"


@dataclass
class Verdict:
    state: str
    reason: str = ""
    unchecked: list[str] = field(default_factory=list)

    @property
    def valid(self) -> bool:
        return self.state == VALID

    def __str__(self) -> str:
        return self.state if self.valid else f"{self.state}: {self.reason}"


def read_json(path: Path):
    try:
        return json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return None


def trial_dirs(job_dir: Path) -> list[Path]:
    return sorted(p for p in job_dir.glob("*__*") if p.is_dir())


def _rewards(result: dict) -> dict:
    return ((result or {}).get("verifier_result") or {}).get("rewards") or {}


def judge_errors(trial: Path) -> list[str]:
    """Criteria whose judge failed rather than scored.

    RewardKit records a timed-out or errored judge as 0.0, indistinguishable
    from a criterion the run genuinely failed. Nine such zeros were once
    published as findings, one of them as the headline difference between two
    fleets.
    """
    details = read_json(trial / "verifier" / "reward-details.json")
    if not isinstance(details, dict):
        return []
    problems = []
    for dimension, groups in details.items():
        for group in groups if isinstance(groups, list) else [groups]:
            if not isinstance(group, dict):
                continue
            for score in group.get("criteria") or []:
                if isinstance(score, dict) and score.get("error"):
                    problems.append(f"{dimension}/{score.get('name')}")
    return problems


def mcp_calls(trial: Path, server: str) -> int:
    """How many times this trial called a tool of `server`.

    Read from the recorded trajectory rather than from the configuration: a
    server that was configured and never answered leaves a fleet
    indistinguishable from a control run, and the trials are then not a result
    for that arm.
    """
    prefix = f"mcp__{server}__"
    total = 0
    for name in ("trajectory.json", "transcript.txt"):
        path = trial / "verifier" / name
        if path.is_file():
            total += path.read_text(errors="ignore").count(prefix)
    return total


def classify(
    trial: Path,
    expected_dimensions: set[str] | None = None,
    snapshot: dict | None = None,
    required_artifacts: list[str] | None = None,
) -> Verdict:
    snapshot = snapshot or {}
    unchecked: list[str] = []

    result = read_json(trial / "result.json")
    if result is None:
        return Verdict(INVALID_INFRASTRUCTURE, "no readable result.json")

    if result.get("exception_info"):
        detail = str(result["exception_info"])[:120]
        return Verdict(INVALID_INFRASTRUCTURE, f"trial raised: {detail}")

    execution = result.get("agent_execution") or {}
    if not execution.get("finished_at"):
        return Verdict(INVALID_AGENT, "agent phase never finished")

    trajectory = read_json(trial / "verifier" / "trajectory.json")
    if trajectory is None:
        return Verdict(INVALID_AGENT, "no readable trajectory")
    steps = trajectory if isinstance(trajectory, list) else trajectory.get("steps")
    if not steps:
        # An empty trajectory scores as a run that did nothing, which is a
        # plausible number for a recording failure.
        return Verdict(INVALID_AGENT, "trajectory records no steps")

    # Treatment delivered. Only checkable where the arm's provision is a server
    # that has to answer; a skill set is delivered by Harbor into the session
    # directory and its non-use is a result rather than a fault.
    server = snapshot.get("mcp_server") or (
        "typo3-dev-companion" if snapshot.get("companion") else None
    )
    if server and not mcp_calls(trial, server):
        return Verdict(
            INVALID_PROVISION,
            f"no tool of {server} was ever called; this arm is "
            f"indistinguishable from a control run",
        )

    if required_artifacts:
        # Existence only, deliberately. Every collector redirects into its file
        # before doing anything (`cmd > file 2>&1 || true`), so the file exists
        # if and only if the collector ran — which is exactly the distinction
        # between "ran and produced nothing" and "did not run". Emptiness is
        # not the same question and is often the answer: a review case that
        # correctly changes nothing leaves an empty `git-diff.patch`, and
        # failing the trial for it would penalise the right behaviour.
        artifacts = trial / "artifacts" / "logs" / "artifacts"
        for name in required_artifacts:
            if not (artifacts / name).is_file():
                return Verdict(INVALID_COLLECTOR, f"artifact {name} was not collected")
    else:
        unchecked.append("collectors (the case declares no required_artifacts)")

    errored = judge_errors(trial)
    if errored:
        return Verdict(
            INVALID_JUDGE,
            f"{len(errored)} criterion/criteria errored rather than scored "
            f"({', '.join(errored[:3])})",
        )

    rewards = _rewards(result)
    if not rewards:
        rewards = read_json(trial / "verifier" / "reward.json") or {}
    if not rewards:
        return Verdict(INVALID_JUDGE, "no rewards were produced")

    if expected_dimensions:
        missing = sorted(expected_dimensions - set(rewards))
        if missing:
            return Verdict(
                INVALID_JUDGE, f"dimension(s) not produced: {', '.join(missing)}"
            )

    return Verdict(VALID, unchecked=unchecked)


def offered_nothing(snapshot: dict) -> bool | None:
    """Did this arm have any capability to choose among?

    `None` where the snapshot cannot say. Absence of a field an older run never
    recorded is not evidence that the arm was offered nothing — read that way,
    it once reported n/a for a fleet carrying twelve skills.
    """
    declares = snapshot.get("fleet_declares")
    provision = snapshot.get("provision")
    requested = snapshot.get("fleet_requested")
    if declares is None and provision is None and requested is None:
        return None

    return not (
        (declares or {}).get("skills")
        or (declares or {}).get("package")
        or (declares or {}).get("companion_ref")
        or (provision or {}).get("mcp_servers")
        or requested
        or snapshot.get("companion")
        or snapshot.get("mcp_server")
    )


def dimension_state(dimension: str, snapshot: dict) -> str:
    if dimension == "capability_selection" and offered_nothing(snapshot):
        return NOT_APPLICABLE
    return VALID


def gate(
    job_dir: Path,
    expected_dimensions: set[str] | None = None,
    required_artifacts: list[str] | None = None,
) -> tuple[list[Path], dict[Path, Verdict]]:
    """Every trial of a job, split into the valid ones and the rest."""
    snapshot = read_json(job_dir / "nr-snapshot.json") or {}
    verdicts = {
        trial: classify(trial, expected_dimensions, snapshot, required_artifacts)
        for trial in trial_dirs(job_dir)
    }
    return [t for t, v in verdicts.items() if v.valid], verdicts
