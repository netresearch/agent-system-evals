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
