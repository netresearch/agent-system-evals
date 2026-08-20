"""Small-sample statistics, chosen for samples this small and no larger.

Everything here is exact or non-parametric. With three to eight trials per arm
there is no distribution to lean on, and a t-test would produce a number whose
confidence comes from an assumption nobody checked. The previous statistic was
"do the two samples overlap at all", reported as one chance in twenty when it
is one in ten, read across eight dimensions with no correction for looking
eight times.

No dependencies on purpose: these scripts run under `uv run --script` with the
package list written in their own headers, and a statistics module that drags
SciPy into every consumer is a module people stop importing.

What each function is for:

- `permutation_p` — continuous outcomes (cost, tokens, tool calls). Exact when
  the sample is small enough to enumerate, which for two arms of five is
  always, and it says so when it falls back to sampling.
- `cliffs_delta` — how far apart two small samples are, on a scale that does
  not pretend the values are normally distributed. -1 and +1 mean complete
  separation, which is where the old check stopped.
- `fisher_p` — pass/fail outcomes, the case's mechanical ground truth.
- `wilson` — an interval around a rate. Never `k/n ± 1.96·√(p(1-p)/n)`: at 3/3
  that gives the interval [1, 1], which claims certainty from three trials.
- `bootstrap_ci` — an interval around a difference of medians.
- `holm` — because a run reads every dimension a case grades.
"""

from __future__ import annotations

import math
import random
from itertools import combinations

# Enumerating C(n+m, n) assignments is exact and cheap while the count is
# small. Two arms of eight is 12870; two of twelve is 2.7 million, which is
# where sampling starts being the sane choice.
EXACT_LIMIT = 200_000


def median(values: list[float]) -> float:
    if not values:
        raise ValueError("median of an empty sample")
    ordered = sorted(values)
    middle = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[middle]
    return (ordered[middle - 1] + ordered[middle]) / 2


def cliffs_delta(a: list[float], b: list[float]) -> float:
    """P(b > a) - P(a > b), from -1 to +1.

    Positive means b tends to be the larger sample. |delta| == 1 is complete
    separation — the condition the old comparison used as its only signal,
    here reported as one number among several rather than as a verdict.
    """
    if not a or not b:
        return 0.0
    greater = sum(1 for x in a for y in b if y > x)
    lesser = sum(1 for x in a for y in b if y < x)
    return (greater - lesser) / (len(a) * len(b))


def permutation_p(
    a: list[float],
    b: list[float],
    statistic=None,
    seed: int = 0,
    samples: int = 20_000,
) -> tuple[float, bool]:
    """Two-sided p for a difference between two samples, and whether it is exact.

    Under the null the two arms are interchangeable, so every way of splitting
    the pooled values into groups of the same sizes is equally likely. Count
    the splits whose statistic is at least as extreme as the observed one. No
    distributional assumption enters anywhere.

    The default statistic is Cliff's delta rather than a difference of medians,
    which matters at these sizes. On the review case's costs — three per arm,
    completely separated — the median difference ties with two further splits
    and returns 0.2, while the ranks return the 0.1 that complete separation of
    three against three actually is. A median of three discards most of what
    three numbers say.
    """
    if not a or not b:
        return 1.0, True
    statistic = statistic or cliffs_delta
    pooled = list(a) + list(b)
    n = len(a)
    observed = abs(statistic(a, b))

    total = math.comb(len(pooled), n)
    if total <= EXACT_LIMIT:
        extreme = 0
        for indices in combinations(range(len(pooled)), n):
            left = [pooled[i] for i in indices]
            right = [pooled[i] for i in range(len(pooled)) if i not in set(indices)]
            if abs(statistic(left, right)) >= observed - 1e-12:
                extreme += 1
        return extreme / total, True

    rng = random.Random(seed)
    extreme = 0
    for _ in range(samples):
        shuffled = pooled[:]
        rng.shuffle(shuffled)
        if abs(statistic(shuffled[:n], shuffled[n:])) >= observed - 1e-12:
            extreme += 1
    # +1 in both places: a Monte Carlo p of exactly zero claims an impossibility
    # the sampling cannot establish.
    return (extreme + 1) / (samples + 1), False


def fisher_p(a_hits: int, a_n: int, b_hits: int, b_n: int, two_sided: bool = True) -> float:
    """Exact test for two pass/fail rates.

    The upgrade case pooled 6 of 6 against 4 of 6 across two independent runs;
    this is the number that says what that is worth (0.23 one-sided), and it is
    the reason that result is written down as a direction rather than a claim.
    """
    a_miss, b_miss = a_n - a_hits, b_n - b_hits
    row1, row2 = a_hits + b_hits, a_miss + b_miss
    total = a_n + b_n
    if min(a_n, b_n) == 0 or row1 == 0 or row2 == 0:
        return 1.0

    def probability(k: int) -> float:
        return (
            math.comb(row1, k)
            * math.comb(row2, a_n - k)
            / math.comb(total, a_n)
        )

    observed = probability(a_hits)
    lower = max(0, a_n - row2)
    upper = min(row1, a_n)
    if two_sided:
        return min(
            1.0,
            sum(probability(k) for k in range(lower, upper + 1)
                if probability(k) <= observed + 1e-12),
        )
    # One-sided in the observed direction.
    if a_hits / a_n >= b_hits / b_n:
        return min(1.0, sum(probability(k) for k in range(a_hits, upper + 1)))
    return min(1.0, sum(probability(k) for k in range(lower, a_hits + 1)))


def wilson(hits: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """Score interval for a rate.

    Chosen because the textbook interval is worst exactly where this benchmark
    lives: at 3 of 3 it returns [1.0, 1.0] and claims certainty from three
    trials. Wilson returns roughly [0.44, 1.0], which is what three trials
    actually support.
    """
    if n == 0:
        return (0.0, 1.0)
    p = hits / n
    denominator = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denominator
    spread = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denominator
    return (max(0.0, centre - spread), min(1.0, centre + spread))


def bootstrap_ci(
    a: list[float],
    b: list[float],
    statistic=None,
    confidence: float = 0.95,
    resamples: int = 10_000,
    seed: int = 0,
) -> tuple[float, float, float]:
    """Point estimate and percentile interval for a difference.

    A bootstrap of three values resamples three values; the interval is wide
    and is meant to be. Reporting the point estimate without it is how a median
    of three got published as a 53% saving.
    """
    statistic = statistic or (lambda x, y: median(y) - median(x))
    point = statistic(a, b)
    if len(a) < 2 or len(b) < 2:
        return point, float("-inf"), float("inf")

    rng = random.Random(seed)
    draws = []
    for _ in range(resamples):
        draws.append(
            statistic(
                [rng.choice(a) for _ in a],
                [rng.choice(b) for _ in b],
            )
        )
    draws.sort()
    tail = (1 - confidence) / 2
    low = draws[int(tail * len(draws))]
    high = draws[min(len(draws) - 1, int((1 - tail) * len(draws)))]
    return point, low, high


def holm(pvalues: dict[str, float]) -> dict[str, float]:
    """Holm-Bonferroni, for the dimensions read beside the primary endpoint.

    A run looks at every dimension a case grades. At eight looks, a threshold
    meant for one is a coin flip. This does not make an exploratory result
    confirmatory — it stops the list from reading as eight independent
    findings.
    """
    ordered = sorted(pvalues.items(), key=lambda kv: kv[1])
    total = len(ordered)
    adjusted: dict[str, float] = {}
    running = 0.0
    for rank, (name, p) in enumerate(ordered):
        running = max(running, min(1.0, (total - rank) * p))
        adjusted[name] = running
    return adjusted


def separated(a: list[float], b: list[float]) -> bool:
    """Do the two samples not overlap at all?

    Kept because it is the trigger for spending more trials, not because it is
    a result. For two groups of three it happens by chance one time in ten — 2
    of the 20 orderings, one in each direction — and the repository called it
    one in twenty until August 2026.
    """
    return bool(a) and bool(b) and (max(a) < min(b) or max(b) < min(a))
