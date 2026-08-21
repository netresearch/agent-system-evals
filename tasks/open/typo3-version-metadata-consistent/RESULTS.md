# OFR-TYPO3-CONSISTENT-001 — recorded results

Two fleets, three trials each, six of six valid. Measured 21 August 2026 on
**`claude-haiku-4-5-20251001`**, benchmark version 0.7.0.

This is the restraint case: the two version declarations in the target already
agree, and the defensible answer is to establish that and change nothing. It
exists because every other case rewards doing something, and a benchmark made
only of those measures eagerness as competence.

## What the run was

`scripts/run-comparison OFR-TYPO3-CONSISTENT-001 --arms control,nr --primary consistency --model claude-haiku-4-5-20251001 --seed 41`

Randomised blocks, `consistency` declared as the primary endpoint before the
first trial. The runner stopped after the discovery round.

Experiment record: `experiments/OFR-TYPO3-CONSISTENT-001-20260821-134032.json`.

## Nothing separated

| | control | nr |
|---|---|---|
| `consistency` met | 1/3 | 1/3 |
| criteria behind it | 15 met / 2 partial / 10 not met | 16 met / 4 partial / 7 not met |
| Cliff's delta | — | +0.33 |
| permutation p | — | 0.800 |

## What the case was built to catch, it caught

The per-trial numbers say more than the counts:

| trial | tool calls | `consistency` |
|---|---|---|
| control 1 | 0 | 0.42 |
| control 2 | 0 | 0.50 |
| control 3 | 11 | 0.75 |
| nr 1 | 20 | 0.50 |
| nr 2 | 14 | 0.75 |
| nr 3 | 9 | 0.58 |

**Two control trials answered without making a single tool call**, on 22.8k
input tokens each. They reached the right conclusion — nothing needs changing —
and scored 0.42 and 0.50, the two lowest results in the series. The only trials
to clear the 0.75 threshold are ones that looked.

That is the distinction the case exists to draw, and it is the one a
pass/fail-on-the-diff rubric cannot draw at all: an empty diff is produced both
by an agent that checked and correctly did nothing, and by an agent that did
nothing. Grading the outcome alone scores them identically and rewards the
second. Here the mechanical criteria ask what was established, so an unexamined
correct answer is scored as what it is.

The reverse error shows up too. `nr 1` made twenty tool calls and scored 0.50 —
the joint-lowest of the equipped arm. Working hard is not the criterion either.

## Nothing was invoked

Zero `Skill(` calls in all three equipped trials. That is now the third case in
a row on this model, and the pattern across the four is consistent with the
documentation case being the exception rather than these being the surprise:
the documentation request names documentation, and a documentation skill is on
offer. "Check whether these two declarations agree" names nothing that any
skill title matches.

## Cost

| | control | nr |
|---|---|---|
| agent cost per trial | 0.00 / 0.01 / 0.06 | 0.04 / 0.08 / 0.09 |
| input tokens | 22.8k / 22.8k / 307.7k | 259.2k / 438.0k / 502.0k |
| tool calls | 0 / 0 / 11 | 9 / 14 / 20 |

Read carefully. The equipped arm costs about eight times the control median,
and the control median is dragged down by the two trials that did no work at
all. Against the one control trial that actually investigated — 307.7k tokens,
11 calls, $0.06 — the equipped arm is not obviously more expensive. A median
across a sample containing non-attempts is not a measurement of what the work
costs. All three lines are exploratory.

## Reproducing

```
scripts/run-comparison OFR-TYPO3-CONSISTENT-001 --arms control,nr \
    --primary consistency --model claude-haiku-4-5-20251001 --seed 41
scripts/analyze experiments/OFR-TYPO3-CONSISTENT-001-20260821-134032.json
```
