"""Mechanical evidence for Open Forward Reviews.

Reads Harbor's recorded trajectory and collected artifacts and turns them into
facts the rubric can rest on. It answers "what did the agent actually do",
never "was that good" — adequacy is the judge's question, and mixing the two is
what makes judges disagree with themselves.

Two rules shape everything here.

**Observable behaviour only.** ``reasoning_content`` is deliberately never
read. An agent that reaches a defensible result by an unstated route has done
the job; one that narrates excellent intentions and does nothing has not.
Grading the narration rewards the second. See docs/open-forward-review.md
section 5.

**Absent infrastructure raises; absent behaviour returns False.** A missing
trajectory is a broken run, not a lazy agent, and scoring it zero would quietly
convert harness failures into evidence about the system under test. RewardKit
records a raised exception as a criterion error, which is visible; a silent 0.0
is not.

This file is the canonical copy. Cases carry a byte-identical copy at
``tests/nreval.py``, synced by ``scripts/sync-verifier-lib`` and checked in CI.
"""

from __future__ import annotations

import json
import os
import re
import shlex
from pathlib import Path
from typing import Any

try:  # available when running under RewardKit; optional for unit tests
    from rewardkit.session import criterion
except ImportError:  # pragma: no cover - exercised only outside the verifier

    def criterion(*_args: Any, **_kwargs: Any):  # type: ignore[misc]
        def wrap(fn):
            return fn

        return wrap


# Container defaults. The environment overrides exist so the rubric can be run
# against recorded fixtures outside a trial — which is how the verifier is
# proved to discriminate at all, given that an open case has no oracle
# (ADR 0003). They are read once at import; tests reassign the constants.
TRAJECTORY_PATH = os.environ.get("NREVAL_TRAJECTORY", "")
ARTIFACTS_DIR = os.environ.get("NREVAL_ARTIFACTS", "/logs/artifacts")
WORKSPACE = os.environ.get("NREVAL_WORKSPACE", "/app")

# Where the trajectory may be, in order of preference.
#
# A separate verifier is not given the agent's log directory: it sees /tests,
# its own /logs/verifier, and whatever was collected as an artifact. So the
# trajectory arrives only because the case declares /logs/agent in
# `artifacts`, and it arrives under the artifact tree rather than at its
# original path. RewardKit's own default (/logs/trajectory.json) is kept last
# as a fallback rather than relied upon.
#
# Searching a list rather than asserting one path is deliberate: the exact
# artifact layout is Harbor's to change, and a hard-coded path would fail as a
# missing trajectory — which reads as a broken run rather than as a moved file.
TRAJECTORY_CANDIDATES = (
    "/logs/artifacts/logs/agent/trajectory.json",
    "/logs/artifacts/agent/trajectory.json",
    "/logs/agent/trajectory.json",
    "/logs/trajectory.json",
)


class MissingEvidence(RuntimeError):
    """Evidence the harness was supposed to record is not there.

    Raised rather than returning a falsy value so a broken run is reported as
    an error instead of being scored as agent failure.
    """


# --------------------------------------------------------------------------
# trajectory
# --------------------------------------------------------------------------


def resolve_trajectory_path() -> Path:
    """The first trajectory that exists, explicit setting winning.

    Resolved at call time, not bound as a default argument: a default is
    evaluated once at import, so reassigning TRAJECTORY_PATH afterwards would
    silently have no effect.
    """
    if TRAJECTORY_PATH:
        return Path(TRAJECTORY_PATH)
    for candidate in TRAJECTORY_CANDIDATES:
        if Path(candidate).exists():
            return Path(candidate)
    raise MissingEvidence(
        "no trajectory found at any of: " + ", ".join(TRAJECTORY_CANDIDATES) + ". "
        "A separate verifier only receives the trajectory if the case declares "
        "/logs/agent in its `artifacts`."
    )


# The trajectory schema this file knows how to read. A new major version may
# rename `steps` or restructure `tool_calls`, and every extractor below would
# then find nothing — which scores as an agent that did nothing rather than as
# a reader that cannot read.
SUPPORTED_ATIF_MAJOR = 1


def validate_trajectory(traj: Any, where: str = "trajectory") -> dict[str, Any]:
    """Refuse a shape this file cannot read, instead of extracting nothing.

    Every extractor here ends in `.get("steps") or []`, so any change to the
    recorded format degrades to an empty trajectory: no commands, no reads, no
    skills, no final answer. That is a complete, well-formed, entirely wrong
    vector — the failure mode this repository keeps finding and the one no
    number reveals. So the shape is checked once, loudly, up front.

    Deliberately structural rather than a full schema: this asserts what the
    extractors actually depend on, so it cannot pass while they fail.
    """
    if not isinstance(traj, dict):
        raise MissingEvidence(
            f"{where} is a {type(traj).__name__}, not an object; this reader "
            f"expects an ATIF trajectory"
        )

    declared = str(traj.get("schema_version") or "")
    match = re.match(r"ATIF-v(\d+)", declared)
    if match and int(match.group(1)) != SUPPORTED_ATIF_MAJOR:
        raise MissingEvidence(
            f"{where} declares {declared}; this reader understands ATIF-v"
            f"{SUPPORTED_ATIF_MAJOR}.x. Read the new format before grading "
            f"against it — an unreadable trajectory scores as an idle agent."
        )

    recorded = traj.get("steps")
    if not isinstance(recorded, list):
        raise MissingEvidence(
            f"{where} has no `steps` list (found "
            f"{type(recorded).__name__}); every extractor in this file reads it"
        )
    if not recorded:
        raise MissingEvidence(
            f"{where} records no steps. An agent phase that produced nothing is "
            f"a broken run, and grading it would report a perfect zero."
        )
    for index, step in enumerate(recorded):
        if not isinstance(step, dict):
            raise MissingEvidence(
                f"{where} step {index} is a {type(step).__name__}, not an object"
            )
        calls = step.get("tool_calls")
        if calls is not None and not isinstance(calls, list):
            raise MissingEvidence(
                f"{where} step {index} has non-list `tool_calls` "
                f"({type(calls).__name__})"
            )
    return traj


def load_trajectory(path: str | Path | None = None) -> dict[str, Any]:
    p = Path(path) if path is not None else resolve_trajectory_path()
    if not p.exists():
        raise MissingEvidence(f"no trajectory at {p}")
    try:
        loaded = json.loads(p.read_text())
    except json.JSONDecodeError as exc:
        raise MissingEvidence(f"trajectory at {p} is not valid JSON: {exc}") from exc
    return validate_trajectory(loaded, where=f"trajectory at {p}")


def steps(traj: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    return (traj or load_trajectory()).get("steps") or []


def tool_calls(traj: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    """Every tool call, in order, with its originating step id attached."""
    out: list[dict[str, Any]] = []
    for step in steps(traj):
        for call in step.get("tool_calls") or []:
            out.append({**call, "step_id": step.get("step_id")})
    return out


def _message_text(message: Any) -> str:
    """ATIF messages are a string or a list of content parts."""
    if isinstance(message, str):
        return message
    if isinstance(message, list):
        parts = [p.get("text", "") for p in message if isinstance(p, dict)]
        return "\n".join(t for t in parts if t)
    return ""


def agent_messages(traj: dict[str, Any] | None = None) -> list[str]:
    return [
        _message_text(s.get("message"))
        for s in steps(traj)
        if s.get("source") == "agent"
    ]


def final_answer(traj: dict[str, Any] | None = None) -> str:
    """The last substantive agent message.

    Agents commonly close with a tool call and no prose, so the last step is
    not reliably the answer; the last agent step carrying text is.
    """
    for text in reversed(agent_messages(traj)):
        if text.strip():
            return text
    return ""


def observations(traj: dict[str, Any] | None = None) -> list[str]:
    """Tool output the agent actually saw."""
    out: list[str] = []
    for step in steps(traj):
        observation = step.get("observation") or {}
        for result in observation.get("results") or []:
            text = _message_text(result.get("content"))
            if text:
                out.append(text)
    return out


# --------------------------------------------------------------------------
# what the agent did
# --------------------------------------------------------------------------

# Argument keys different agents use for the same two ideas. Claude Code emits
# `command` and `file_path`; Codex and shell-style agents emit `cmd`/`path`.
# Matching on the argument rather than the tool name keeps the rubric portable
# across agents, which matters because agent-independence is one of the things
# the benchmark is meant to establish.
_COMMAND_KEYS = ("command", "cmd", "shell_command", "script")
_PATH_KEYS = ("file_path", "path", "filename", "notebook_path")

# Commands that read a file rather than acting on it.
_READING_COMMANDS = {"cat", "head", "tail", "less", "more", "bat", "nl", "od"}


def commands(traj: dict[str, Any] | None = None) -> list[str]:
    """Shell commands the agent executed."""
    found: list[str] = []
    for call in tool_calls(traj):
        args = call.get("arguments") or {}
        for key in _COMMAND_KEYS:
            value = args.get(key)
            if isinstance(value, str) and value.strip():
                found.append(value.strip())
                break
    return found


def ran_command(pattern: str, traj: dict[str, Any] | None = None) -> bool:
    """Whether any executed command matches *pattern* (a regex).

    Says nothing about whether it worked. See `ran_command_successfully`.
    """
    rx = re.compile(pattern)
    return any(rx.search(c) for c in commands(traj))


def _results_by_call(traj: dict[str, Any] | None = None) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for step in steps(traj):
        for result in ((step.get("observation") or {}).get("results") or []):
            if isinstance(result, dict) and result.get("source_call_id"):
                out[result["source_call_id"]] = result
    return out


def command_results(traj: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    """Each command with what happened to it: `{command, failed, exit_code}`.

    A command that ran is not a command that worked, and until this existed the
    rubric could not tell the difference — `ran_command("phpstan")` is True for
    a run where PHPStan was installed and for one where the invocation died on
    a missing binary. "Verification was attempted" and "verification happened"
    are different findings and one of them is the dimension's whole question.

    Two independent signals, because neither is always present: the recorded
    result carries `extra.tool_result_is_error`, and shell output from this
    harness begins with `Exit code N` when it is not zero. `exit_code` is None
    where the trajectory does not say — never 0, which would claim success from
    an absence.
    """
    results = _results_by_call(traj)
    out: list[dict[str, Any]] = []
    for call in tool_calls(traj):
        args = call.get("arguments") or {}
        command = next(
            (
                args[key].strip()
                for key in _COMMAND_KEYS
                if isinstance(args.get(key), str) and args[key].strip()
            ),
            None,
        )
        if command is None:
            continue
        result = results.get(call.get("tool_call_id")) or {}
        extra = result.get("extra") or {}
        content = result.get("content") or ""
        exit_match = re.match(r"\s*Exit code (\d+)", content if isinstance(content, str) else "")
        exit_code = int(exit_match.group(1)) if exit_match else None
        out.append(
            {
                "command": command,
                "failed": bool(extra.get("tool_result_is_error"))
                or bool(exit_code),
                "exit_code": exit_code,
            }
        )
    return out


def ran_command_successfully(
    pattern: str, traj: dict[str, Any] | None = None
) -> bool:
    """Whether a command matching *pattern* ran and did not report failure."""
    rx = re.compile(pattern)
    return any(
        rx.search(entry["command"]) and not entry["failed"]
        for entry in command_results(traj)
    )


def failed_commands(traj: dict[str, Any] | None = None) -> list[str]:
    return [entry["command"] for entry in command_results(traj) if entry["failed"]]


def read_paths(traj: dict[str, Any] | None = None) -> list[str]:
    """Paths the agent opened.

    Covers both file-reading tools and shell commands that read a file, since
    an agent that runs `cat composer.json` has read composer.json as surely as
    one that called a Read tool. Missing the shell route would understate
    context discovery for exactly the agents that prefer a terminal.
    """
    found: list[str] = []
    for call in tool_calls(traj):
        args = call.get("arguments") or {}
        for key in _PATH_KEYS:
            value = args.get(key)
            if isinstance(value, str) and value.strip():
                found.append(value.strip())
                break

    for command in commands(traj):
        try:
            tokens = shlex.split(command)
        except ValueError:
            continue
        for index, token in enumerate(tokens):
            if token in _READING_COMMANDS:
                found.extend(
                    t for t in tokens[index + 1 :] if not t.startswith("-")
                )
                break
    return found


def read_path_matching(pattern: str, traj: dict[str, Any] | None = None) -> bool:
    rx = re.compile(pattern)
    return any(rx.search(p) for p in read_paths(traj))


def skills_used(traj: dict[str, Any] | None = None) -> list[str]:
    """Skills the agent invoked, in order, de-duplicated.

    Harnesses expose skill invocation as a tool call whose argument names the
    skill. Both the argument-based and the command-based route are covered, so
    a skill reached through a slash command is not missed.
    """
    names: list[str] = []
    for call in tool_calls(traj):
        args = call.get("arguments") or {}
        if str(call.get("function_name", "")).lower() in ("skill", "invokeskill"):
            name = args.get("skill") or args.get("name") or args.get("command")
            if isinstance(name, str) and name.strip():
                names.append(name.strip().lstrip("/"))

    for command in commands(traj):
        match = re.match(r"^/([a-z0-9][a-z0-9:_-]*)", command.strip())
        if match:
            names.append(match.group(1))

    seen: set[str] = set()
    ordered: list[str] = []
    for name in names:
        if name not in seen:
            seen.add(name)
            ordered.append(name)
    return ordered


def used_skill(pattern: str, traj: dict[str, Any] | None = None) -> bool:
    rx = re.compile(pattern)
    return any(rx.search(s) for s in skills_used(traj))


# --------------------------------------------------------------------------
# artifacts
# --------------------------------------------------------------------------


def artifact(name: str, required: bool = True) -> str:
    p = Path(ARTIFACTS_DIR) / name
    if not p.exists():
        if required:
            raise MissingEvidence(f"no artifact {name} in {ARTIFACTS_DIR}")
        return ""
    return p.read_text(errors="replace")


def git_status() -> str:
    return artifact("git-status.txt")


def git_diff() -> str:
    return artifact("git-diff.patch")


def workspace_modified() -> bool:
    return bool(git_status().strip())


# --------------------------------------------------------------------------
# normalised view
# --------------------------------------------------------------------------


def evidence_manifest() -> dict[str, Any]:
    """A Netresearch-shaped summary of one trial.

    Not a replacement for Harbor's artifacts — a normalised view over them, so
    the dashboard and the retro bridge read one stable shape rather than
    re-deriving it from raw logs each time.
    """
    traj = load_trajectory()
    executed = commands(traj)
    return {
        "trajectory": {
            "schema_version": traj.get("schema_version"),
            "agent": (traj.get("agent") or {}).get("name"),
            "steps": len(steps(traj)),
            "tool_calls": len(tool_calls(traj)),
        },
        "commands": executed,
        "read_paths": sorted(set(read_paths(traj))),
        "skills_used": skills_used(traj),
        "git": {
            "status": git_status(),
            "modified": workspace_modified(),
        },
        "final_answer": final_answer(traj),
    }


def transcript(traj: dict[str, Any] | None = None, budget: int = 120_000) -> str:
    """A bounded, readable rendering of the trajectory for a judge to read.

    An agent judge opens what it is given as a file and pages through it. The
    raw ATIF trajectory is over a megabyte on a rich run, and reading it that
    way cost 40 turns and then a CLI exit — one failed reward, and RewardKit
    takes the whole run with it. Handing over a digest instead is bounded work
    with no exploration in it.

    It is also better evidence. The same input produces the same reading, where
    a judge left to page through a large file may stop in a different place
    each time.

    Reasoning is not included, here as everywhere: only observable behaviour is
    graded. Long observations are cut with the cut marked, so the judge can see
    that something was elided rather than silently receiving less.
    """
    traj = traj or load_trajectory()

    # The final answer is reserved and rendered whole, before anything else
    # competes for room. It is the single most important piece of evidence in a
    # review case — most dimensions ask about the report — and it sits at the
    # very end of the trajectory, which is exactly where a running budget or a
    # per-message cap eats it.
    #
    # Both happened. Capped at 4000 characters, an 8000-character report
    # reached the judges as half a sentence, and prioritization, evidence and
    # outcome quality collapsed across every fleet. The scores moved so far
    # that they were obviously about the instrument rather than the agents.
    answer = final_answer(traj)
    reserved = len(answer) + 200

    lines: list[str] = []
    used = 0
    truncated = False
    budget = max(budget - reserved, budget // 4)

    def emit(text: str) -> bool:
        """Append unless it would breach the budget; report whether it fit.

        The flag is what marks the cut. An earlier version inferred truncation
        from the running total, which never reaches the budget precisely
        because this refuses to append — so the transcript was silently short
        with nothing saying so.
        """
        nonlocal used, truncated
        if used + len(text) > budget:
            truncated = True
            return False
        lines.append(text)
        used += len(text)
        return True

    for step in steps(traj):
        if truncated:
            break
        source = step.get("source", "?")
        step_id = step.get("step_id")

        message = _message_text(step.get("message")).strip()
        if message:
            if not emit(f"\n[{step_id}] {source}:\n{message[:4000]}"):
                break

        for call in step.get("tool_calls") or []:
            args = call.get("arguments") or {}
            detail = ""
            for key in (*_COMMAND_KEYS, *_PATH_KEYS, "pattern", "skill"):
                value = args.get(key)
                if isinstance(value, str) and value.strip():
                    detail = f" {key}={value.strip()[:300]}"
                    break
            if not emit(f"\n[{step_id}] tool {call.get('function_name')}{detail}"):
                break

        for observation in (step.get("observation") or {}).get("results") or []:
            text = _message_text(observation.get("content")).strip()
            if not text:
                continue
            shown = text[:1200]
            suffix = "" if len(text) <= 1200 else f"\n  … {len(text) - 1200} more characters"
            if not emit(f"\n[{step_id}] observed:\n{shown}{suffix}"):
                break

    if truncated:
        lines.append(
            f"\n\n[intermediate steps truncated at {budget} characters; "
            f"{len(steps(traj))} steps total. The final answer below is complete.]"
        )

    if answer:
        lines.append("\n\n=== FINAL ANSWER (complete) ===\n")
        lines.append(answer)
    return "".join(lines)


def write_transcript(path: str | Path | None = None) -> Path:
    target = Path(path or f"{ARTIFACTS_DIR}/transcript.txt")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(transcript())
    return target


def write_evidence_manifest(path: str | Path | None = None) -> Path:
    target = Path(path or f"{ARTIFACTS_DIR}/evidence-manifest.json")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(evidence_manifest(), indent=2, sort_keys=True))
    return target


# --------------------------------------------------------------------------
# shared criteria
# --------------------------------------------------------------------------
#
# Marked shared so RewardKit exposes them to the per-dimension subdirectories.
# Names stay within ^[a-zA-Z0-9_-]{1,64}$, which structured-output providers
# enforce on response keys.


# RewardKit passes the workspace as the first argument to every criterion. It
# is unused here on purpose: this evidence comes from the recorded trajectory
# and the collected artifacts, not from the live tree, which is what lets the
# same criteria run unchanged during a regrade.


@criterion(shared=True, description="Agent read a path matching '{pattern}'")
def nr_read_path(workspace: Path, pattern: str) -> bool:
    return read_path_matching(pattern)


@criterion(shared=True, description="Agent ran a command matching '{pattern}'")
def nr_ran_command(workspace: Path, pattern: str) -> bool:
    return ran_command(pattern)


@criterion(shared=True, description="Agent invoked a skill matching '{pattern}'")
def nr_used_skill(workspace: Path, pattern: str) -> bool:
    return used_skill(pattern)


@criterion(shared=True, description="Final answer matches '{pattern}'")
def nr_final_answer_matches(workspace: Path, pattern: str) -> bool:
    return bool(re.search(pattern, final_answer(), re.IGNORECASE))


@criterion(shared=True, description="Agent left the working tree unmodified")
def nr_workspace_unmodified(workspace: Path) -> bool:
    return not workspace_modified()


@criterion(shared=True, description="Agent modified the working tree")
def nr_workspace_modified(workspace: Path) -> bool:
    """The positive form, for writing cases where changing nothing is failure.

    Not the negation of the criterion above: a writing case wants a high score
    for having done the work, and a negated criterion inverts the raw value,
    which makes the reward unreadable when a dimension mixes polarities.
    """
    return workspace_modified()


@criterion(shared=True, description="Artifact '{name}' matches '{pattern}'")
def nr_artifact_matches(workspace: Path, name: str, pattern: str) -> bool:
    """Whether a collected artifact's contents match a regex.

    This is how a writing case reads its outcome. The result of such a task is
    not in the trajectory but in the tree the agent left, so collect hooks run
    that tree and write their verdict to a file; this reads the verdict.

    Absence raises rather than returning False. A missing artifact means the
    hook did not run — an infrastructure failure — and scoring it as the
    agent's failure would convert a broken harness into evidence about the
    system under test.
    """
    return bool(re.search(pattern, artifact(name), re.MULTILINE))
