"""The comparability gate, and the two states it used to conflate.

`scripts/compare` decides whether two recorded jobs may be set beside each
other. Everything it gets wrong is invisible in its output: a refusal that
should have been an acceptance looks like a configuration mistake, and an
acceptance that should have been a refusal looks like a result.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def load(name: str):
    """Import a script that has no .py extension."""
    spec = importlib.util.spec_from_loader(
        name,
        importlib.machinery.SourceFileLoader(name, str(ROOT / "scripts" / name)),
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


compare = load("compare")


def snapshot(**overrides) -> dict:
    base = {
        "case_id": "OFR-TEST-001",
        "fleet": "control",
        "agent": "claude-code",
        "model": "claude-opus-5",
        "judge": "claude-opus-5",
        "trials": 3,
        "comparison": {"task_digest": "aaa", "agent": "claude-code"},
        "provision_digest": "p1",
        "grade": {
            "rubric_digest": "r1",
            "judge": "claude-opus-5",
            "rewardkit": "0.1.7",
        },
    }
    base.update(overrides)
    return base


# --- counts: missing is not failure -----------------------------------------


def test_missing_dimension_is_not_counted_as_not_met():
    """`t.get(dimension, 0.0)` made these two states one.

    A case that grades one dimension printed seven confident `0/3` rows for
    dimensions it does not grade, which reads as a run that failed them.
    """
    trials = [{"consistency": 1.0}, {"consistency": 1.0}, {"consistency": 1.0}]
    met, scored, missing = compare.counts(trials, "verification")
    assert (met, scored, missing) == (0, 0, 3)

    met, scored, missing = compare.counts(trials, "consistency")
    assert (met, scored, missing) == (3, 3, 0)


def test_partial_scores_do_not_count_as_met():
    trials = [{"evidence": 0.5}, {"evidence": 1.0}]
    assert compare.counts(trials, "evidence") == (1, 2, 0)


def test_dimensions_present_follows_the_registry_not_a_literal():
    present = compare.dimensions_present(
        [{"consistency": 1.0, "evidence": 1.0}], [{"authority": 1.0}]
    )
    # Registry order, and `consistency` appears at all — a fixed list of eight
    # reported nothing for the cases that grade it.
    assert present == ["authority", "evidence", "consistency"]


def test_dimensions_present_keeps_unknown_names():
    present = compare.dimensions_present([{"zzz_new": 1.0, "evidence": 1.0}])
    assert present == ["evidence", "zzz_new"]


# --- comparability ----------------------------------------------------------


def test_identical_configuration_is_comparable():
    compare.check_comparable(snapshot(), snapshot(fleet="nr", provision_digest="p2"))


def test_differing_task_digest_is_refused(capsys):
    with pytest.raises(SystemExit) as exit_info:
        compare.check_comparable(
            snapshot(),
            snapshot(
                fleet="nr",
                provision_digest="p2",
                comparison={"task_digest": "bbb", "agent": "claude-code"},
            ),
        )
    assert exit_info.value.code == 2


def test_variant_pair_is_comparable_despite_a_differing_task_digest():
    """The feature that had never worked.

    A variant pair varies the repository, so the task directory and its digest
    differ by construction. The fingerprint difference was collected before the
    pair was recognised, so the check written to permit the comparison rejected
    it every time.
    """
    a = snapshot(variant_of="OFR-TEST-001", variant="prepared")
    b = snapshot(
        case_id="OFR-TEST-001-BARE",
        variant_of="OFR-TEST-001",
        variant="bare",
        comparison={"task_digest": "bbb", "agent": "claude-code"},
    )
    compare.check_comparable(a, b)


def test_variant_pair_with_two_variables_is_refused():
    a = snapshot(variant_of="OFR-TEST-001", variant="prepared")
    b = snapshot(
        case_id="OFR-TEST-001-BARE",
        variant_of="OFR-TEST-001",
        variant="bare",
        fleet="nr",
        comparison={"task_digest": "bbb", "agent": "claude-code"},
    )
    with pytest.raises(SystemExit):
        compare.check_comparable(a, b)


def test_same_provision_is_refused_without_the_placebo_flag():
    with pytest.raises(SystemExit) as exit_info:
        compare.check_comparable(snapshot(), snapshot())
    assert exit_info.value.code == 2


def test_placebo_permits_two_identical_arms():
    """The measurement the ordinary refusal made impossible.

    Same fleet against itself is the only way to learn how far this instrument
    moves on its own, which is the scale every real difference has to clear.
    """
    compare.check_comparable(snapshot(), snapshot(), placebo=True)


def test_placebo_refuses_arms_that_actually_differ():
    with pytest.raises(SystemExit):
        compare.check_comparable(
            snapshot(), snapshot(fleet="nr", provision_digest="p2"), placebo=True
        )


# --- grade identity ---------------------------------------------------------


def test_jobs_graded_by_different_rubrics_are_refused():
    """A regrade used to carry the original rubric's identity forward."""
    with pytest.raises(SystemExit) as exit_info:
        compare.check_graded_alike(
            snapshot(),
            snapshot(
                grade={
                    "rubric_digest": "r2",
                    "judge": "claude-opus-5",
                    "rewardkit": "0.1.7",
                }
            ),
        )
    assert exit_info.value.code == 2


def test_jobs_graded_alike_pass():
    compare.check_graded_alike(snapshot(), snapshot())


def test_a_job_without_a_grade_snapshot_is_noted_not_refused(capsys):
    compare.check_graded_alike(snapshot(), snapshot(grade=None))
    assert "predates the grade snapshot" in capsys.readouterr().err


# --- the declared variable ---------------------------------------------------


def test_a_model_comparison_is_refused_by_default():
    """Two models with no declaration is a result with two candidate causes."""
    with pytest.raises(SystemExit):
        compare.check_comparable(
            snapshot(), snapshot(model="claude-haiku-4-5", provision_digest="p2")
        )


def test_a_declared_model_comparison_is_allowed():
    compare.check_comparable(
        snapshot(),
        snapshot(model="claude-haiku-4-5"),
        variable="model",
    )


def test_a_model_comparison_that_also_moves_the_fleet_is_refused():
    """The one that would look like a model finding and be a fleet one."""
    with pytest.raises(SystemExit):
        compare.check_comparable(
            snapshot(),
            snapshot(model="claude-haiku-4-5", fleet="nr", provision_digest="p2"),
            variable="model",
        )


def test_a_model_comparison_that_also_moves_the_judge_is_refused():
    """The grading instrument must be the same on both sides."""
    with pytest.raises(SystemExit):
        compare.check_comparable(
            snapshot(),
            # A different judge, not the same one restated: the first version
            # of this test passed `claude-opus-5`, which the fixture already
            # uses, so it changed nothing and asserted nothing.
            snapshot(model="claude-haiku-4-5", judge="gpt-5-thinking"),
            variable="model",
        )


def test_the_model_fingerprint_is_ignored_only_when_declared():
    a = snapshot(comparison={"task_digest": "aaa", "model": "claude-opus-5"})
    b = snapshot(
        model="claude-haiku-4-5",
        comparison={"task_digest": "aaa", "model": "claude-haiku-4-5"},
    )
    compare.check_comparable(a, b, variable="model")
    with pytest.raises(SystemExit):
        compare.check_comparable(a, b)


def test_cost_is_a_declarable_endpoint():
    """The benchmark could not plan around its own most separated result.

    Of eleven recorded comparisons, three reached Cliff's delta ±1.00 at the
    smallest attainable p, and all three were cost — so every one of them was
    exploratory by construction, because `--primary` accepted only dimensions
    and the mechanical outcome. A run that cannot declare the thing it goes on
    to find can only ever report it as a hypothesis.
    """
    import importlib.util
    from importlib.machinery import SourceFileLoader

    loader = SourceFileLoader("run_comparison", str(ROOT / "scripts" / "run-comparison"))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)

    assert module.RESOURCE == {"cost": "cost_usd", "input_tokens": "n_input_tokens"}
    # And they are not silently mistaken for dimensions: dimensions.toml is the
    # registry, and neither belongs in it.
    import sys
    sys.path.insert(0, str(ROOT / "scripts" / "lib"))
    import dimensions
    registry = {d["id"] for d in dimensions.registry()["dimension"]}
    assert not (set(module.RESOURCE) & registry)


def test_the_declared_endpoint_is_reported_by_analyze(tmp_path):
    """A run was declared on `skill_invoked` and analyze never printed it.

    `scripts/run-comparison` accepted the endpoint, recorded it in the
    experiment record, and then handed the reader to `scripts/analyze`,
    which knew only dimensions, cost and the mechanical outcome. The
    declared number had to be recomputed by hand to be read at all —
    a reporting tool that omits the one line the run was powered for.
    """
    analyze = load("analyze")

    def trial(name: str, invoked: bool) -> Path:
        d = tmp_path / name / "verifier"
        d.mkdir(parents=True)
        calls = [{"function_name": "Skill"}] if invoked else [{"function_name": "Bash"}]
        (d / "trajectory.json").write_text(
            json.dumps({"steps": [{"tool_calls": calls}]})
        )
        return d.parent

    arm = object.__new__(analyze.Arm)
    arm.trials = [trial("a", True), trial("b", False), trial("c", True)]
    assert arm.invoked_skill() == [1.0, 0.0, 1.0]

    # Both scripts must read the transcript the same way, or the declared
    # endpoint means one thing at run time and another at reporting time.
    # The endpoint's name and the tool names behind it are asserted in both
    # files, at the source level, because there is no shared module to pin.
    loader = importlib.machinery.SourceFileLoader(
        "run_comparison", str(ROOT / "scripts" / "run-comparison")
    )
    spec = importlib.util.spec_from_loader(loader.name, loader)
    run_comparison = importlib.util.module_from_spec(spec)
    loader.exec_module(run_comparison)
    assert run_comparison.INVOCATION == "skill_invoked"

    tools = '("skill", "invokeskill")'
    for script in ("analyze", "run-comparison", "invocation-census"):
        assert tools in (ROOT / "scripts" / script).read_text(), script
