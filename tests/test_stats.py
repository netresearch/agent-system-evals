"""The small-sample statistics, pinned against values computed by hand.

Two of these reproduce numbers already published in this repository, which is
the point: a statistics module nobody can check against a known value is
another instrument that returns plausible numbers.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "lib"))

import stats  # noqa: E402


def test_complete_separation_of_three_against_three_is_one_in_ten():
    """The claim the repository got wrong until August 2026.

    Six exchangeable observations admit C(6,3) = 20 orderings; two of them are
    completely separated, one per direction. The documentation, the comparison
    script and the published page all said one in twenty, which is the
    one-sided figure.
    """
    p, exact = stats.permutation_p([2.21, 2.80, 3.54], [1.27, 1.40, 1.55])
    assert exact
    assert p == 2 / 20


def test_complete_separation_of_four_against_four():
    p, exact = stats.permutation_p([5, 6, 7, 8], [1, 2, 3, 4])
    assert exact
    assert p == 2 / 70


def test_the_rank_statistic_beats_a_median_difference_at_this_size():
    """Why the default statistic is Cliff's delta.

    On completely separated samples of three, a median difference ties with two
    further splits and returns 0.2 — twice the correct figure — because a
    median of three discards most of what three numbers say.
    """
    a, b = [2.21, 2.80, 3.54], [1.27, 1.40, 1.55]
    by_median, _ = stats.permutation_p(
        a, b, statistic=lambda x, y: stats.median(y) - stats.median(x)
    )
    by_rank, _ = stats.permutation_p(a, b)
    assert by_median == 0.2
    assert by_rank == 0.1


def test_overlapping_samples_are_nowhere_near_significant():
    """The runtime case's costs, where control alone spans a factor of 2.5."""
    p, _ = stats.permutation_p([4.20, 5.03, 10.46], [3.63, 4.27, 6.21])
    assert p > 0.5


def test_fisher_reproduces_the_published_upgrade_figure():
    """RESULTS.md reports one-sided p = 0.23 for 6 of 6 against 4 of 6."""
    assert round(stats.fisher_p(6, 6, 4, 6, two_sided=False), 2) == 0.23


def test_fisher_is_symmetric_under_swapping_the_arms():
    assert stats.fisher_p(3, 3, 1, 3) == stats.fisher_p(1, 3, 3, 3)


def test_wilson_does_not_claim_certainty_from_three_trials():
    """The textbook interval returns [1.0, 1.0] here and would be a lie."""
    low, high = stats.wilson(3, 3)
    assert high == 1.0
    assert 0.3 < low < 0.6


def test_wilson_at_zero_hits_is_not_a_point_either():
    low, high = stats.wilson(0, 3)
    assert low == 0.0
    assert 0.4 < high < 0.7


def test_cliffs_delta_is_plus_or_minus_one_only_on_separation():
    assert stats.cliffs_delta([1, 2, 3], [4, 5, 6]) == 1.0
    assert stats.cliffs_delta([4, 5, 6], [1, 2, 3]) == -1.0
    assert abs(stats.cliffs_delta([1, 5], [2, 4])) < 1.0


def test_bootstrap_interval_brackets_its_point_estimate():
    point, low, high = stats.bootstrap_ci([1.0, 2.0, 3.0], [4.0, 5.0, 6.0], seed=1)
    assert low <= point <= high


def test_bootstrap_declines_to_invent_an_interval_from_one_trial():
    point, low, high = stats.bootstrap_ci([1.0], [4.0])
    assert point == 3.0
    assert low == float("-inf") and high == float("inf")


def test_holm_is_monotone_and_never_lowers_a_p_value():
    raw = {"a": 0.01, "b": 0.04, "c": 0.5}
    adjusted = stats.holm(raw)
    assert all(adjusted[k] >= raw[k] for k in raw)
    assert adjusted["a"] <= adjusted["b"] <= adjusted["c"]


def test_holm_of_a_single_endpoint_changes_nothing():
    assert stats.holm({"only": 0.03}) == {"only": 0.03}


def test_a_sampled_p_is_reported_as_sampled():
    """A Monte Carlo p of exactly zero would claim an impossibility."""
    a = list(range(15))
    b = [x + 100 for x in range(15)]
    p, exact = stats.permutation_p(a, b, samples=500, seed=3)
    assert not exact
    assert p > 0


def test_empty_samples_do_not_produce_a_finding():
    assert stats.permutation_p([], [1, 2]) == (1.0, True)
    assert stats.cliffs_delta([], [1, 2]) == 0.0
    assert stats.fisher_p(0, 0, 1, 3) == 1.0
