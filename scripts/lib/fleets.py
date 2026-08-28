"""Resolve a fleet, including one derived from another.

A fleet changes several things at once — skills, an MCP server, a companion
package, a PATH, environment variables — which answers "does the equipped stack
help" and cannot answer which part did the work. The review case makes that
concrete: the agent reached exactly one skill of nine in every trial, and the
cost separated. Whether the other eight contributed anything is not a question
the existing fleets can put.

An ablation is that question, and it should not cost a copy of a fleet file.
A copy drifts: the day `nr` moves to a new skill version, every hand-made
variant of it silently measures the old one, and nothing says so. So a derived
fleet states the difference and inherits the rest:

    name: nr-minus-conformance
    derives_from: nr
    without:
      - netresearch/typo3-conformance-skill

`without` names repositories to drop; `only` names the ones to keep. Anything
else — companion, MCP server, environment, `min_typo3_line` — is inherited and
may be overridden by stating it.
"""

from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]

# Keys a derived fleet inherits unless it states its own.
INHERITED = (
    "skills",
    "companion",
    "mcp_server",
    "env",
    "package",
    "requires",
    "min_typo3_line",
)


class FleetError(RuntimeError):
    pass


def read(name: str, _seen: tuple[str, ...] = ()) -> dict:
    """One fleet, with any `derives_from` chain already applied."""
    path = ROOT / "fleets" / f"{name}.yaml"
    if not path.is_file():
        available = sorted(p.stem for p in (ROOT / "fleets").glob("*.yaml"))
        raise FleetError(f"no fleet {name!r}; available: {', '.join(available)}")

    fleet = yaml.safe_load(path.read_text()) or {}
    parent_name = fleet.get("derives_from")
    if not parent_name:
        return fleet

    if name in _seen:
        raise FleetError(
            f"fleet {name!r} derives from itself: {' -> '.join([*_seen, name])}"
        )
    parent = read(parent_name, (*_seen, name))

    resolved = dict(parent)
    for key in INHERITED:
        if key in fleet:
            resolved[key] = fleet[key]
    resolved["name"] = fleet.get("name", name)
    resolved["description"] = fleet.get("description", parent.get("description", ""))
    resolved["derives_from"] = parent_name

    skills = list(resolved.get("skills") or [])
    drop = set(fleet.get("without") or [])
    keep = set(fleet.get("only") or [])
    if drop and keep:
        raise FleetError(f"fleets/{name}.yaml: use `without` or `only`, not both")

    # `add` is the counterpart of `without`: an arm that carries one capability
    # the parent lacks. Without it the only way to add a skill is to restate
    # the parent's whole list, which is the failure `derives_from` exists to
    # prevent — the copy still names the parent's versions on the day the
    # parent moves, and the arm measures two changes while reporting one.
    added = list(fleet.get("add") or [])
    if added:
        carried = {s.get("repo") for s in skills}
        already = [s.get("repo") for s in added if s.get("repo") in carried]
        if already:
            raise FleetError(
                f"fleets/{name}.yaml: `add` names {sorted(already)}, which "
                f"{parent_name} already carries. The arm would have been "
                f"identical to its parent and read as a capability that "
                f"changes nothing — use `at` to move a ref instead."
            )
        skills = skills + added

    if drop:
        remaining = [s for s in skills if s.get("repo") not in drop]
        unknown = drop - {s.get("repo") for s in skills}
        if unknown:
            # A typo here removes nothing and the arm silently equals its
            # parent — an ablation that ablates nothing, reported as a
            # component making no difference.
            raise FleetError(
                f"fleets/{name}.yaml: `without` names {sorted(unknown)}, which "
                f"{parent_name} does not carry. The arm would have been "
                f"identical to its parent and read as a component that changes "
                f"nothing."
            )
        skills = remaining
    elif keep:
        unknown = keep - {s.get("repo") for s in skills}
        if unknown:
            raise FleetError(
                f"fleets/{name}.yaml: `only` names {sorted(unknown)}, which "
                f"{parent_name} does not carry"
            )
        skills = [s for s in skills if s.get("repo") in keep]

    if not skills and (drop or keep):
        raise FleetError(
            f"fleets/{name}.yaml: the ablation removes every skill. That is a "
            f"control run with a different name — compare against `control`."
        )

    # `at` moves a skill's ref instead of dropping it. Without it a candidate
    # fleet had to be a full copy of its parent with one line changed, which is
    # the failure `derives_from` exists to prevent: the copy still names the
    # parent's other versions on the day the parent moves, and the arm then
    # measures two changes while reporting one.
    at = dict(fleet.get("at") or {})
    if at:
        known = {s.get("repo") for s in skills}
        unknown = set(at) - known
        if unknown:
            raise FleetError(
                f"fleets/{name}.yaml: `at` names {sorted(unknown)}, which "
                f"{parent_name} does not carry. A ref cannot be moved for a "
                f"skill the parent does not have — add it to the parent, or "
                f"name it as its own entry under `skills`."
            )
        moved = []
        for skill in skills:
            repo = skill.get("repo")
            if repo in at:
                if skill.get("ref") == at[repo]:
                    # The same failure as an ablation that ablates nothing: the
                    # arm equals its parent and reads as a change with no effect.
                    raise FleetError(
                        f"fleets/{name}.yaml: `at` pins {repo} to "
                        f"{at[repo]}, which is what {parent_name} already "
                        f"carries. The arm would have been identical to its "
                        f"parent."
                    )
                skill = dict(skill, ref=at[repo])
            moved.append(skill)
        skills = moved

    resolved["skills"] = skills
    resolved["ablation"] = {
        "of": parent_name,
        "without": sorted(drop),
        "only": sorted(keep),
        "at": dict(sorted(at.items())),
        "add": sorted(s.get("repo") for s in added),
    }
    return resolved


def skill_refs(name: str) -> list[str]:
    """`repo@ref` per skill, with the checks a fleet manifest has to pass."""
    fleet = read(name)
    entries = []
    for skill in fleet.get("skills") or []:
        ref = skill.get("ref")
        if not ref:
            raise FleetError(f"fleets/{name}.yaml: {skill.get('repo')} has no ref")
        # A full commit SHA cannot be used: Harbor resolves the ref with
        # `git ls-remote <url> <ref>`, which returns nothing for a bare SHA and
        # fails with "No matching ref". Tags and branches work; the resolved SHA
        # is recovered afterwards from the job lock.
        if len(ref) == 40 and all(c in "0123456789abcdef" for c in ref.lower()):
            raise FleetError(
                f"fleets/{name}.yaml: {skill['repo']} is pinned to a commit "
                f"SHA. Harbor resolves refs via git ls-remote, which cannot "
                f"answer for a bare SHA. Use a tag."
            )
        entries.append(f"{skill['repo']}@{ref}")
    return entries
