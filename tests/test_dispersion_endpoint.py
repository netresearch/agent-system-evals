"""A spread endpoint is read as Brown-Forsythe and never stops after three."""

from __future__ import annotations

import importlib.machinery
import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "lib"))

import stats  # noqa: E402


def load():
    loader = importlib.machinery.SourceFileLoader(
        "run_comparison", str(ROOT / "scripts" / "run-comparison")
    )
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


# The review case's 28 August costs, six per arm: medians one cent apart,
# ranges 22x apart.
BARE = [1.79, 0.38, 0.44, 0.13, 0.08, 0.26]
EQUIPPED = [0.13, 0.13, 0.14, 0.12, 0.09, 0.15]


def test_deviations_are_distances_from_the_own_median():
    assert stats.deviations_from_median([]) == []
    assert stats.deviations_from_median([0.1, 0.2, 0.3]) == pytest.approx([0.1, 0.0, 0.1])
    # An even sample takes the midpoint, so no value is at distance zero.
    assert min(stats.deviations_from_median([1.0, 2.0])) == 0.5


def test_a_tail_the_location_test_calls_flat_separates_on_spread():
    """The finding the location endpoint read as nothing, three times."""
    p_location, _ = stats.permutation_p(BARE, EQUIPPED)
    dev_a = stats.deviations_from_median(BARE)
    dev_b = stats.deviations_from_median(EQUIPPED)
    p_spread, exact = stats.permutation_p(dev_a, dev_b)
    assert exact
    assert p_spread < p_location
    assert p_spread < 0.05
    assert stats.cliffs_delta(dev_a, dev_b) < -0.8


def test_a_spread_endpoint_is_declarable_and_never_stops_at_discovery():
    module = load()
    assert set(module.SPREAD) == {"cost_spread", "input_tokens_spread"}
    assert module.SPREAD["cost_spread"] == module.RESOURCE["cost"]
    source = (ROOT / "scripts" / "run-comparison").read_text()
    # The branch that decides after the discovery round sets `moved = True`
    # for a spread, and says why, in the same block.
    block = source[source.index("elif args.primary in SPREAD:"):]
    block = block[: block.index("else:")]
    assert "moved = True" in block
    assert "deviations_from_median" in block
    assert '"dispersion" if args.primary in SPREAD' in source


def test_run_out_keeps_a_floor_round_going_past_discovery():
    """Two arms at 2/3 ended a floor round at three per arm that had named six."""
    source = (ROOT / "scripts" / "run-comparison").read_text()
    assert '"--run-out"' in source
    block = source[source.index('record["blocks"][-1]["primary_p"] = p'):]
    block = block[: block.index("stopped = True")]
    assert "elif args.run_out:" in block
    assert "continuing to the budget" in block
    assert "(--run-out)" in source  # the stopping rule written into the record says so
