# OFR-TYPO3-UPGRADE-001 — recorded results (Haiku)

Two fleets, three trials each, six of six valid. Measured 22 August 2026 on
**`claude-haiku-4-5-20251001`**, benchmark version 0.8.0.

The last case of the Haiku sweep and the one where the two arms behave least
alike — while the declared endpoint stays flat.

## What the run was

`scripts/run-comparison OFR-TYPO3-UPGRADE-001 --arms control,nr --primary outcome_quality --model claude-haiku-4-5-20251001 --seed 91`

Experiment record: `experiments/OFR-TYPO3-UPGRADE-001-20260822-101714.json`.

## Neither arm completed the upgrade

| | control | nr |
|---|---|---|
| mechanical outcome | 0/3 | 0/3 |
| `outcome_quality` met | 0/3 | 0/3 |
| per-trial score | 0.44 / 0.50 / 0.50 | 0.46 / 0.50 / 0.56 |
| permutation p | — | 0.700 |

The primary is flat and the runner stopped after the discovery round. Everything
below is exploratory.

## Two dimensions separate completely

| dimension | control | nr | delta | p | Holm |
|---|---|---|---|---|---|
| `verification` | 0/3 | 1/3 | +1.00 | 0.100 | 0.600 |
| `prioritization` | 0/3 | 2/3 | +1.00 | 0.100 | 0.600 |
| `context_discovery` | 0/3 | 0/3 | +0.56 | 0.500 | 1.000 |
| `authority` | 0/3 | 0/3 | +0.56 | 0.400 | 1.000 |
| `evidence` | 1/3 | 1/3 | +0.11 | 1.000 | 1.000 |
| `unsupported_claims` | 2/3 | 1/3 | −0.44 | 0.700 | 1.000 |

The counts understate what moved. Behind `verification` the criteria go from
**0 met / 5 partial / 19 not met** to **11 met / 6 partial / 7 not met**; behind
`prioritization`, from 0 met / 8 partial / 1 not met to 5 met / 4 partial / 0 not
met. Those are not one-trial wobbles, and both are completely separated at
delta +1.00 — the strongest statement three trials per arm admit.

They are still exploratory, and Holm puts them at 0.600 precisely because eight
dimensions were read. A confirmatory series with `verification` declared as the
primary is what these lines are for.

## What the two arms actually did

| | control | nr |
|---|---|---|
| tool calls | 4 / 5 / 5 | 27 / 33 / 117 |
| input tokens | 97.7k / 99.1k / 122.4k | 904.2k / 1.37M / 7.75M |
| agent cost | 0.02 / 0.03 / 0.03 | 0.14 / 0.25 / 1.12 |

Read the control column first. **Four to five tool calls on a TYPO3 major-version
upgrade**, around 100k input tokens, two to three cents. The unaided agent barely
engages with the task, and its `outcome_quality` of 0.44 to 0.50 is what an
answer written from general knowledge scores. Its 2/3 on `unsupported_claims` —
the one dimension where it leads — is easier to earn when little is claimed.

The equipped arm spends between ten and seventy times the tokens and separates
completely on cost in the other direction (delta +1.00, p 0.100), with one trial
at 117 tool calls and $1.12. It does not finish either. What it buys, on these
numbers, is verification and prioritisation of an upgrade it did not complete.

Whether that is worth $0.25 instead of $0.03 is a question about the task, not
about the benchmark — and it is the opposite trade from the review case measured
the same week, where the equipped arm reached the same result for a third less.

## The skill was invoked

`typo3-extension-upgrade`, in three trials of three.

Third and last case in the sweep where routing fires, after documentation and
review. All three name a domain a skill covers. The five cases where nothing was
invoked — release preparation, both version-metadata cases, the restraint case
and the runtime bug — name a task instead.

## Reproducing

```
scripts/run-comparison OFR-TYPO3-UPGRADE-001 --arms control,nr \
    --primary outcome_quality --model claude-haiku-4-5-20251001 --seed 91
scripts/analyze experiments/OFR-TYPO3-UPGRADE-001-20260822-101714.json
```

---

# Confirmatory series: `verification` declared in advance

Two arms, three trials each, six of six valid. Measured 28 August 2026 on
**`claude-haiku-4-5-20251001`**, benchmark version 2.0.0.

`scripts/run-comparison OFR-TYPO3-UPGRADE-001 --arms control,nr --primary verification --model claude-haiku-4-5-20251001 --seed 171`

Experiment record: `experiments/OFR-TYPO3-UPGRADE-001-20260828-074950.json`.

## Why this run exists

The exploratory series of 22 August separated completely on `verification` and
`prioritization` — delta +1.00, permutation p 0.100, Holm 0.600 over eight
dimensions read at once. That is what the deepening rule calls a hypothesis:
it names the next experiment rather than settling anything. This is that
experiment, with `verification` declared before the first trial and read as the
only endpoint.

## It did not confirm

| | control | nr |
|---|---|---|
| `verification` met | 0/3 | 0/3 |
| criteria behind it | 0 met / 4 partial / 20 not met | **8 met / 3 partial / 13 not met** |
| Cliff's delta | — | +0.33 |
| permutation p | — | 0.600 |

The count is flat and the criteria are not: eight criteria met against zero is
the largest shift this case has produced on any dimension. But the dimension
crosses its threshold in no trial of either arm, so what moved is the middle of
the distribution and not the outcome — and the earlier +1.00 does not survive
its own confirmation.

Two things follow. The first is about this case: the equipped arm does more
verifying and still never verifies enough to meet the dimension, which is a
statement about how far the fleet gets rather than whether it helps. The second
is about the rule that produced the hypothesis. A completely separated
exploratory line at three trials per arm was, here, noise dressed as a finding
— exactly what the one-in-ten figure in
[docs/open-forward-review.md](../../../docs/open-forward-review.md) section 11
predicts will happen roughly one time in ten.

## The rest of the table

| dimension | control | nr | Holm |
|---|---|---|---|
| `context_discovery` | 3/3 | 0/3 | 0.600 |
| `prioritization` | 0/3 | 1/3 | 1.000 |
| `unsupported_claims` | 2/3 | 0/3 | 1.000 |
| `authority` | 0/3 | 0/3 | 1.000 |
| `evidence` | 1/3 | 1/3 | 1.000 |
| `outcome_quality` | 0/3 | 0/3 | 1.000 |

`context_discovery` separates completely in the *other* direction this time —
3/3 against 0/3, delta −1.00, the same p 0.100 and Holm 0.600 that
`verification` carried in August. It is exploratory, it is one of seven lines
read at once, and it is recorded here without a claim attached for the same
reason the August lines should have been.

**And the calibration since has given it a second reason.** Four of those six
trials score within one judge step of the 0.75 threshold, so their met/not-met
answers are the ones measured to flip on identical input — 7 of 12 such
measurements did, against 1 of 20 further from the line (instrument failure
24). `scripts/analyze` now marks the row, and this one is marked. A 3/3
against 0/3 built from boundary scores is a statement about the instrument.

`typo3-extension-upgrade` was invoked in three trials of three, as before.

## Cost

| | control | nr |
|---|---|---|
| agent cost | 0.05 / 0.06 / 0.11 | 0.07 / 0.09 / **1.23** |

One equipped trial cost $1.23, twenty times the control median and ten times
its own arm's next-highest. The interval spans −0.04 to +1.18 and the median
difference is three cents. A mean over this arm would be a number about one
trial.
