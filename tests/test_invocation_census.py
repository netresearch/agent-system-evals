"""The census names an arm by what it carries and by what ran it."""

from __future__ import annotations

import importlib.machinery
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(name: str):
    loader = importlib.machinery.SourceFileLoader(name.replace("-", "_"), str(ROOT / "scripts" / name))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


def job(root: Path, name: str, model: str, invoked: list[bool]) -> None:
    d = root / name
    d.mkdir(parents=True)
    (d / "nr-snapshot.json").write_text(
        json.dumps({"case_id": "CASE-1", "fleet": "nr", "model": model})
    )
    for i, hit in enumerate(invoked):
        v = d / f"trial{i}" / "verifier"
        v.mkdir(parents=True)
        calls = [{"function_name": "Skill" if hit else "Bash"}]
        (v / "trajectory.json").write_text(json.dumps({"steps": [{"tool_calls": calls}]}))


def test_one_model_keeps_the_bare_arm_name(tmp_path):
    job(tmp_path, "a", "claude-haiku-4-5-20251001", [True, False])
    census = load("invocation-census").census(tmp_path)
    assert set(census["CASE-1"]["by_fleet"]) == {"nr"}
    assert census["CASE-1"]["by_fleet"]["nr"] == {"invoked": 1, "trials": 2}


def test_two_models_are_never_pooled_into_one_rate(tmp_path):
    """`candidate 11 of 12` was six Opus trials and six Haiku trials in one cell.

    One number over two models is a rate of nothing, and the pooled figure hid
    that the two models did not agree. Same defect as pooling two fleets, one
    level further out.
    """
    job(tmp_path, "a", "claude-haiku-4-5-20251001", [True, False])
    job(tmp_path, "b", "claude-opus-5", [True, True])
    by_fleet = load("invocation-census").census(tmp_path)["CASE-1"]["by_fleet"]
    assert by_fleet == {
        "nr on haiku-4-5": {"invoked": 1, "trials": 2},
        "nr on opus-5": {"invoked": 2, "trials": 2},
    }


def test_a_dated_model_id_loses_only_its_date(tmp_path):
    short = load("invocation-census").short_model
    assert short("claude-haiku-4-5-20251001") == "haiku-4-5"
    assert short("claude-opus-5") == "opus-5"
    # Not a date: an eight-digit tail is required, and a version is not one.
    assert short("claude-sonnet-4-5") == "sonnet-4-5"


def test_short_forms_that_collide_keep_the_full_identifier(tmp_path):
    """`claude-opus-5` and `claude-opus-5-20251001` both shorten to `opus-5`.

    Folding both into one key would let the second overwrite the first and
    silently restore the pooling the split exists to prevent.
    """
    job(tmp_path, "a", "claude-opus-5", [True])
    job(tmp_path, "b", "claude-opus-5-20251001", [False, False])
    by_fleet = load("invocation-census").census(tmp_path)["CASE-1"]["by_fleet"]
    assert by_fleet == {
        "nr on claude-opus-5": {"invoked": 1, "trials": 1},
        "nr on claude-opus-5-20251001": {"invoked": 0, "trials": 2},
    }


def test_a_model_split_is_always_printed_even_when_every_arm_invoked(tmp_path):
    """`split` used to stay silent when no arm was at zero.

    Two models at 5/6 and 6/6 then printed as a pooled 11 of 12 and read as one
    rate, which is the disagreement the split exists to show.
    """
    census = load("invocation-census")
    job(tmp_path, "a", "claude-haiku-4-5-20251001", [True, True, True, True, True, False])
    job(tmp_path, "b", "claude-opus-5", [True] * 6)
    row = census.census(tmp_path)["CASE-1"]
    assert {bool(v["invoked"]) for v in row["by_fleet"].values()} == {True}
    note = census.split(row)
    assert note is not None
    assert "nr on haiku-4-5 5 of 6" in note
    assert "nr on opus-5 6 of 6" in note
