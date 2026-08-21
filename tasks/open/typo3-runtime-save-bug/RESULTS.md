# OFR-TYPO3-RUNTIME-001 — recorded results (Haiku)

Two fleets, three trials each, six of six valid. Measured 21 August 2026 on
**`claude-haiku-4-5-20251001`**, benchmark version 0.8.0.

This case has an earlier series on `claude-opus-5`, recorded 19 August. The two
are not compared here: the rubric has changed since, and a comparison across
models needs both sides graded alike (`scripts/compare --variable model`).

## What the run was

`scripts/run-comparison OFR-TYPO3-RUNTIME-001 --arms control,nr --primary outcome_quality --model claude-haiku-4-5-20251001 --seed 61`

`outcome_quality` declared as the primary endpoint before the first trial —
this is a diagnosis case, and whether the agent worked out what was wrong is the
question it asks. Randomised blocks; the runner stopped after the discovery
round.

Experiment record: `experiments/OFR-TYPO3-RUNTIME-001-20260821-142708.json`.

## Nobody diagnosed it

| trial | tool calls | `outcome_quality` |
|---|---|---|
| control 1 | 34 | 0.38 |
| control 2 | 20 | 0.25 |
| control 3 | 67 | 0.38 |
| nr 1 | 31 | 0.38 |
| nr 2 | 45 | 0.25 |
| nr 3 | 56 | 0.25 |

`outcome_quality` met 0/3 in both arms, and no trial came within half the
threshold. These are not non-attempts — every trial made between twenty and
sixty-seven tool calls. The agents worked, at length, and did not arrive.

`verification` is the other flat line: 0/3 either side, and the criteria behind
it are 9 met / 1 partial / 14 not met in **both** arms, digit for digit. On a
case whose whole subject is a runtime behaviour that can be reproduced in the
provisioned instance, neither arm establishes that its account is right.

## The full dimension table

| dimension | control | nr | Holm p |
|---|---|---|---|
| `outcome_quality` (primary) | 0/3 | 0/3 | 1.000 |
| `context_discovery` | 0/3 | 1/3 | 1.000 |
| `authority` | 1/3 | 0/3 | 1.000 |
| `evidence` | 2/3 | 3/3 | 1.000 |
| `verification` | 0/3 | 0/3 | 1.000 |
| `prioritization` | 0/3 | 1/3 | 1.000 |
| `unsupported_claims` | 1/3 | 1/3 | 1.000 |
| `capability_selection` | n/a | — | — |

Every secondary line is exploratory and Holm-adjusted to 1.000. `analyze`
reports `capability_selection` as not applicable rather than as a zero, because
the control arm was offered nothing to choose among — a dimension that cannot
apply is not a dimension the arm failed.

Zero `Skill(` calls in all three equipped trials. Five cases in a row on this
model.

## Cost

| | control | nr |
|---|---|---|
| agent cost per trial | 0.01 / 0.01 / 0.23 | 0.01 / 0.01 / 0.30 |
| tool calls | 20 / 34 / 67 | 31 / 45 / 56 |

The spread inside each arm is twenty-fold and covers everything between them.
Cliff's delta +0.11, p 1.000. Exploratory, and at this spread a median would be
a number rather than a measurement.

## Reproducing

```
scripts/run-comparison OFR-TYPO3-RUNTIME-001 --arms control,nr \
    --primary outcome_quality --model claude-haiku-4-5-20251001 --seed 61
scripts/analyze experiments/OFR-TYPO3-RUNTIME-001-20260821-142708.json
```
