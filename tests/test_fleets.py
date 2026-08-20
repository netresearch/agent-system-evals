"""Derived fleets, and the failure an ablation makes easy.

A fleet changes several things at once — skills, a server, a package, a PATH —
which answers "does the equipped stack help" and cannot answer which part did
the work. An ablation puts that question, and the way to get it wrong is for the
ablation to remove nothing and be reported as a component that changes nothing.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "lib"))

import fleets  # noqa: E402


@pytest.fixture
def declare(tmp_path, monkeypatch):
    directory = tmp_path / "fleets"
    directory.mkdir()
    monkeypatch.setattr(fleets, "ROOT", tmp_path)

    def write(name: str, body: dict) -> None:
        (directory / f"{name}.yaml").write_text(yaml.safe_dump(body))

    write(
        "parent",
        {
            "name": "parent",
            "skills": [
                {"repo": "org/a-skill", "ref": "v1"},
                {"repo": "org/b-skill", "ref": "v2"},
            ],
            "env": {"PATH": "/opt/tools/bin:$PATH"},
            "companion": {"ref": "abc"},
        },
    )
    return write


def test_a_derived_fleet_drops_only_what_it_names(declare):
    declare("child", {"derives_from": "parent", "without": ["org/a-skill"]})
    resolved = fleets.read("child")
    assert [s["repo"] for s in resolved["skills"]] == ["org/b-skill"]


def test_a_derived_fleet_inherits_everything_it_does_not_state(declare):
    """The part that would fail silently.

    An ablation of a fleet that carries a toolchain must still carry it. A PATH
    entry that does not exist is not an error on any system — the shell skips
    it — so an arm labelled as the stack would run with none of its tools and
    nothing would fail.
    """
    declare("child", {"derives_from": "parent", "without": ["org/a-skill"]})
    resolved = fleets.read("child")
    assert resolved["env"] == {"PATH": "/opt/tools/bin:$PATH"}
    assert resolved["companion"] == {"ref": "abc"}


def test_an_override_wins_over_the_inherited_value(declare):
    declare("child", {"derives_from": "parent", "env": {"PATH": "/bin"}})
    assert fleets.read("child")["env"] == {"PATH": "/bin"}


def test_removing_a_skill_the_parent_does_not_have_is_refused(declare):
    """A typo removes nothing, and the arm silently equals its parent.

    Reported as a result, that is "this component makes no difference" — the
    exact conclusion an ablation exists to reach honestly.
    """
    declare("child", {"derives_from": "parent", "without": ["org/typo-skill"]})
    with pytest.raises(fleets.FleetError) as excinfo:
        fleets.read("child")
    assert "typo-skill" in str(excinfo.value)


def test_only_keeps_what_it_names(declare):
    declare("child", {"derives_from": "parent", "only": ["org/a-skill"]})
    assert [s["repo"] for s in fleets.read("child")["skills"]] == ["org/a-skill"]


def test_without_and_only_together_are_refused(declare):
    declare(
        "child",
        {"derives_from": "parent", "without": ["org/a-skill"], "only": ["org/b-skill"]},
    )
    with pytest.raises(fleets.FleetError):
        fleets.read("child")


def test_an_ablation_that_removes_everything_is_refused(declare):
    """That is a control run with a different name."""
    declare(
        "child",
        {"derives_from": "parent", "without": ["org/a-skill", "org/b-skill"]},
    )
    with pytest.raises(fleets.FleetError) as excinfo:
        fleets.read("child")
    assert "control" in str(excinfo.value)


def test_a_cycle_is_refused(declare):
    declare("a", {"derives_from": "b"})
    declare("b", {"derives_from": "a"})
    with pytest.raises(fleets.FleetError) as excinfo:
        fleets.read("a")
    assert "derives from itself" in str(excinfo.value)


def test_the_resolution_records_what_was_ablated(declare):
    declare("child", {"derives_from": "parent", "without": ["org/a-skill"]})
    assert fleets.read("child")["ablation"] == {
        "of": "parent",
        "without": ["org/a-skill"],
        "only": [],
    }


# --- the real fleets in this repository -------------------------------------


def test_the_committed_ablation_removes_exactly_one_skill():
    base = {s["repo"] for s in fleets.read("nr")["skills"]}
    ablated = {s["repo"] for s in fleets.read("nr-minus-conformance")["skills"]}
    assert base - ablated == {"netresearch/typo3-conformance-skill"}


def test_every_committed_fleet_resolves():
    for path in sorted((ROOT / "fleets").glob("*.yaml")):
        fleets.skill_refs(path.stem)
