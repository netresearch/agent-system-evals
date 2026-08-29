# OFR-TYPO3-CALENDAR-001 — an event lost on the day the clocks change

The second case mined from the world, and the first on a target that belongs to
nobody here.

| | |
|---|---|
| request | [issue #1219](https://github.com/derhansen/sf_event_mgt/issues/1219), reported by an external user |
| environment | `derhansen/sf_event_mgt` at `9ae846a3`, the commit before the fix |
| ground truth | the functional test and fixture from `07a8ef7f` |
| endpoint | mechanical: 2 of 2 assertions, no judge |

## Why a third-party target

The netresearch extensions with real outside users are also the skill fleet's
worked examples. The sibling case's target is named in **47** installed files
and cost 38 recorded contamination judgements, which recur at every skill bump —
and it leaves an exposure that cannot be judged away: an equipped arm reads
documentation naming that repository far more often than any other.

This extension is named in **no** installed skill. Contamination check: zero
hits across all thirteen fleets.

## The timezone is part of the case

The defect happens on the day the clocks change. Under `TZ=UTC` there is no
such day, so it cannot occur:

| timezone | at `9ae846a3` | at `07a8ef7f` |
|---|---|---|
| UTC | 2 tests, 0 failures | 2 tests, 0 failures |
| Europe/Berlin | 2 tests, **1 failure** | 2 tests, 0 failures |

Shipped without the timezone pinned, this case would have graded every trial as
a pass — including an agent that changed nothing. The image pins it and a test
fails if that line is removed. `docs/case-lifecycle.md` criterion 8 records the
general form.

## First result — 29 August 2026

`scripts/run-comparison OFR-TYPO3-CALENDAR-001 --arms control,nr --primary mechanical_outcome --model claude-haiku-4-5-20251001 --seed 331`

Twelve trials, six per arm, twelve of twelve valid. Experiment record:
`experiments/OFR-TYPO3-CALENDAR-001-20260829-115437.json`.

| | control | nr |
|---|---|---|
| mechanical outcome | **2/6** | **1/6** |
| Fisher exact p | — | 1.000 |
| `skill_invoked` | 0/6 | 0/6 |
| agent cost, median | $0.64 | $0.49 |

**Three of twelve trials fixed a real, externally reported defect.** That is
the first time the declared endpoint has moved off zero in this benchmark, and
it moves in both arms — the difference between 2 and 1 is nothing at this size.

The equipped arm loaded no skill, so this case measured the base model twice,
like every other case whose request does not name a skill's opening clause.

## What the judge found, which is worth more than the counts

The rubric gained a criterion after the sibling case: **what would the run the
agent treats as proof have done, had the fix been wrong?** Across both arms:

| criterion | not met |
|---|---|
| the check it ran could have failed | **12 of 13** |
| established the defect before changing it | 11 of 13 |
| the change is narrow | 4 of 13 |
| claims match what was shown | 4 of 13 |

Nearly every trial, equipped or not, changed code before establishing what the
code did with the reported input, and then verified with something that could
not have come out wrong. That is one behaviour, not two, and it is the same one
the sibling case surfaced as *"Perfect! The fix is working correctly"* over a
check that says otherwise.

One difference between the arms is worth recording as a hypothesis rather than
a finding: `claims_match_what_was_shown` is met in 6 of 6 equipped trials
against 3 of 7 unaided ones. The equipped agents were more careful about what
they *claimed* — and equally unable to produce a check that could fail.
