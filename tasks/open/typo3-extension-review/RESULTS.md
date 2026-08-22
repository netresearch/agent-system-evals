# OFR-TYPO3-EXT-001 — recorded results (Haiku)

Two fleets, three trials each, six of six valid. Measured 22 August 2026 on
**`claude-haiku-4-5-20251001`**, benchmark version 0.8.0.

## What the run was

`scripts/run-comparison OFR-TYPO3-EXT-001 --arms control,nr --primary outcome_quality --model claude-haiku-4-5-20251001 --seed 81`

Experiment record: `experiments/OFR-TYPO3-EXT-001-20260822-092852.json`.

An earlier attempt on 21 August, same seed, stopped in its third block:
`run-comparison` checks how much life the session token has left and refuses to
start a trial that would run past it, because a trial that dies on a 401 is
recorded as an errored trial rather than as a credential problem. Four trials
from that attempt are on disk under experiment
`OFR-TYPO3-EXT-001-20260821-153503` and are **not** pooled into the figures
below — an abandoned experiment's trials are not spare observations for the next
one.

## Both arms do the job

| | control | nr |
|---|---|---|
| `outcome_quality` met | 3/3 | 3/3 |
| criteria behind it | 10 met / 2 partial / 0 not met | 10 met / 2 partial / 0 not met |
| permutation p | — | 1.000 |

The primary endpoint is at the ceiling on both sides, so the runner stopped
after the discovery round. Every secondary dimension is Holm-adjusted to 1.000.

| dimension | control | nr |
|---|---|---|
| `context_discovery` | 3/3 | 3/3 |
| `prioritization` | 2/3 | 2/3 |
| `verification` | 1/3 | 0/3 |
| `authority` | 0/3 | 0/3 |
| `evidence` | 0/3 | 0/3 |
| `unsupported_claims` | 0/3 | 0/3 |

`unsupported_claims` is worth its own line: 0 met and 9 partial in control, 1 met
and 8 partial in the equipped arm, with nothing scored *not met* on either side.
A review that neither overclaims nor grounds its claims is the middle of that
dimension, and both arms sit there.

## The cost separates completely, in the equipped arm's favour

| | control | nr |
|---|---|---|
| agent cost per trial | 0.16 / 0.19 / 0.36 | 0.09 / 0.13 / 0.14 |
| input tokens | 603.6k / 1.04M / 1.64M | 320.9k / 564.3k / 703.5k |
| tool calls | 21 / 58 / 80 | 25 / 32 / 43 |

Every equipped trial costs less than every control trial: Cliff's delta −1.00,
permutation p 0.100 — the smallest p three trials per arm can produce, and the
strongest statement this sample size admits. The median falls by a third.

It is still **exploratory**. `outcome_quality` was the declared endpoint and it
did not move; reading a completely separated secondary line as the finding is
what the declaration exists to prevent. What it does is name the next
experiment: a series with cost declared as the primary endpoint would settle in
six trials what this one can only suggest.

## The skill was invoked

`typo3-conformance`, in three trials of three.

That is the second case in this sweep where routing fires — the other is the
documentation case — and both are cases whose request names a domain a skill
covers. "Review this TYPO3 extension and tell me what needs attention" reaches a
conformance skill; "prepare release 2.4.2" and "check whether these two
declarations agree" reach nothing, in six trials each.

Taken with the cost figures, this is the clearest shape in the sweep: where the
capability is selected, the equipped arm reaches the same result over a
noticeably shorter path.

## Reproducing

```
scripts/run-comparison OFR-TYPO3-EXT-001 --arms control,nr \
    --primary outcome_quality --model claude-haiku-4-5-20251001 --seed 81
scripts/analyze experiments/OFR-TYPO3-EXT-001-20260822-092852.json
```

---

# Ablation: `nr` without the conformance skill

Two arms, three trials each, six of six valid. Measured 22 August 2026 on
**`claude-haiku-4-5-20251001`**, benchmark version 0.8.0.

`scripts/run-comparison OFR-TYPO3-EXT-001 --arms nr,nr-minus-conformance --primary outcome_quality --model claude-haiku-4-5-20251001 --seed 101`

Experiment record: `experiments/OFR-TYPO3-EXT-001-20260822-145242.json`.

## Why this case and not a factorial sweep

A fleet changes several things at once, so an ablation is only worth trials
where a component was demonstrably used. Across the nine-case Haiku sweep this
is the one place that holds: `typo3-conformance` was invoked in three trials of
three here, and the cost separated completely against control. Ablating a
component of a fleet whose effect is not established would measure a difference
of a difference at three trials per arm.

## Removing it moves five of eight dimensions

| dimension | `nr` | minus conformance | delta | p | Holm |
|---|---|---|---|---|---|
| `outcome_quality` (primary) | 3/3 | 2/3 | −0.78 | 0.300 | — |
| `capability_selection` | 0/3 | 0/3 | **−1.00** | 0.100 | 0.700 |
| `verification` | 1/3 | 0/3 | **−1.00** | 0.100 | 0.700 |
| `context_discovery` | 3/3 | 2/3 | −0.44 | 0.500 | 1.000 |
| `prioritization` | 2/3 | 0/3 | −0.56 | 0.400 | 1.000 |
| `authority` | 0/3 | 0/3 | −0.56 | 0.400 | 1.000 |
| `evidence` | 0/3 | 0/3 | −0.44 | 0.500 | 1.000 |
| `unsupported_claims` | 0/3 | 0/3 | −0.44 | 0.700 | 1.000 |

Every delta is negative. The counts hide most of it, and the criteria behind two
dimensions do not:

| | `nr` | minus conformance |
|---|---|---|
| `capability_selection` | **12 met / 0 partial / 0 not met** | 3 met / 7 partial / 2 not met |
| `verification` | 13 met / 4 partial / 7 not met | 3 met / 8 partial / 13 not met |
| `outcome_quality` | 10 met / 2 partial / 0 not met | 5 met / 7 partial / 0 not met |

Both separated dimensions sit at Cliff's delta −1.00 with p 0.100 — the strongest
statement three trials per arm admits. Holm puts them at 0.700 because eight
dimensions were read, and the primary did not move, so this remains
**exploratory**. What it does is name a confirmatory series: `verification` or
`capability_selection` declared as the primary, on this case, against this pair.

## The agent substituted, and the substitutes did worse

| trial | skills invoked |
|---|---|
| `nr` 1, 2, 3 | `typo3-conformance` |
| minus conformance 1 | `automated-assessment`, `typo3-extension-upgrade` |
| minus conformance 2 | `automated-assessment`, `security-audit` |
| minus conformance 3 | none |

This is the part worth keeping. The agent did not simply lose a capability and
carry on unaided: in two of three trials it reached for the routing skill and
then for a *different* domain skill — an upgrade skill on a review task, a
security skill on a review task — and `capability_selection` fell from twelve
criteria met to three. Once it reached for nothing at all.

So the finding is not "conformance helps" but something more specific: **no other
skill in this fleet substitutes for it, and the fleet's own router picks a poor
substitute rather than declining.** That is a lead about `automated-assessment`,
which is the skill whose job is exactly this choice.

## Cost

| | `nr` | minus conformance |
|---|---|---|
| agent cost | 0.11 / 0.14 / 0.15 | 0.08 / 0.10 / 0.16 |
| input tokens | 491.3k / 614.1k / 634.6k | 324.6k / 368.2k / 826.8k |
| tool calls | 19 / 42 / 48 | 22 / 25 / 41 |

Overlapping in both directions, p 0.700. Removing the skill does not
reliably save anything, and the arm that kept it still costs a third less than
the unequipped control measured on this case the same week.
