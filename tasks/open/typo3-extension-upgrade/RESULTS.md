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
