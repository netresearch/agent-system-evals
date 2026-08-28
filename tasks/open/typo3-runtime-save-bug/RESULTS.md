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

---

# The out-of-sample test — 28 August 2026

This case is the benchmark's largest silent block: 46 equipped trials on record,
zero skill invocations. On 28 August four routing experiments produced a rule —
*a skill is reached when the words the request itself uses appear in the opening
clause of its description* — derived from five measurements after the fact,
which is the weakest way to hold a rule.

This run tests it on a case it had not seen, with the prediction written down
first.

## The prediction, recorded before launching

From `docs/composition-sweep.md` and `fleets/nr-instance.yaml`, both committed
before the first trial:

> **Prediction: 0 of N.** `typo3-ddev` opens *"Use whenever a running TYPO3
> instance is wanted, started or reached"*; the request says *"saving a
> translation in the TextDb backend module does nothing — the dialog closes,
> but the old value is still there"*. Instance, started, reached, DDEV: none of
> those words is in the request. By the rule this is the "covers the work under
> other words" row, and it should not route.

An invocation would have refuted the rule outright.

## What the run was

`scripts/run-comparison OFR-TYPO3-RUNTIME-001 --arms nr,nr-instance --primary skill_invoked --model claude-haiku-4-5-20251001 --seed 269`

`nr-instance` is `nr` plus `netresearch/typo3-ddev-skill@v1.22.2` and nothing
else. Six trials, three per arm, six of six valid; the runner stopped after the
discovery round because the declared endpoint did not move. All three
`nr-instance` locks carry the skill. Experiment record:
`experiments/OFR-TYPO3-RUNTIME-001-20260828-175340.json`.

## The prediction held

| | nr | nr-instance |
|---|---|---|
| `skill_invoked` | 0/3 | 0/3 |
| Wilson interval | [0.00, 0.56] | [0.00, 0.56] |
| Fisher exact p | — | 1.000 |

**What this is worth, stated plainly.** Three trials, and the interval reaches
0.56 — this run could not have distinguished "never" from "sometimes". What it
could have done, and did not, is produce the single invocation that would have
falsified the rule. That is the whole of its value: a prediction that could have
failed, on a case the rule was not built from, did not fail.

It is the second capability measured to be present and unreached, after
`go-development` naming "LDAP/AD clients" for a request that only says
*library*. Both fit the same half of the rule.

## What it means for this case's 46 silent trials

They stop being unexplained. Nothing in the fleet — before or after adding the
one skill that names anything the case touches — opens by naming what this
request says. The equipped arm here is the unaided agent carrying luggage, and
that is a statement about the catalogue rather than about the agent's judgement.

Fixing it is not a fleet change. It would need a skill whose first sentence
names diagnosing a backend module that saves nothing, and the organisation
publishes none.

## The rest of the report

`context_discovery` went 0/3 to 1/3, four of six trials within one judge step of
the threshold; every other dimension is identical on both arms. Exploratory, and
at this size not readable even as a hint. Only `skill_invoked` was declared.

## Reproducing

```
scripts/run-comparison OFR-TYPO3-RUNTIME-001 --arms nr,nr-instance \
    --primary skill_invoked --model claude-haiku-4-5-20251001 --seed 269
scripts/analyze experiments/OFR-TYPO3-RUNTIME-001-20260828-175340.json
```
