# OFR-TYPO3-METADATA-001 — recorded results

Two fleets, three trials each, no errored trials. Measured 20 August 2026 on
**`claude-haiku-4-5-20251001`**, benchmark version 0.6.2.

The first result this case has produced, and the first this repository has
recorded on any model other than Opus. It is not comparable with any figure
elsewhere in this repository: the model differs, and every earlier job predates
the blinded transcripts, the validity gate and the rubric changes of the same
day.

## What the run was

`scripts/run-comparison OFR-TYPO3-METADATA-001 --arms control,nr --primary consistency --model claude-haiku-4-5-20251001 --seed 11`

Randomised blocks — one trial per arm per block, order shuffled — with
`consistency` declared as the primary endpoint before the first trial. The
runner stopped after the discovery round because the endpoint did not move,
which is the rule and not a shortcut: three trials per arm cannot establish a
difference, and nothing here suggests one is there to establish.

Experiment record: `experiments/OFR-TYPO3-METADATA-001-20260820-204603.json`.

## Nothing separated

| | control | nr |
|---|---|---|
| `consistency` met | 3/3 | 3/3 |
| criteria behind it | 21 met / 3 partial / 0 not met | 20 met / 4 partial / 0 not met |
| Cliff's delta | — | −0.33 |
| permutation p | — | 1.000 |

Both arms reconciled the two declarations in every trial. The criteria
distribution is where the counts stop being flat, and it leans very slightly
*against* the equipped arm — one more partial. At this size that is noise, and
the number to quote is the p-value, not the direction.

## Cost

| | control | nr |
|---|---|---|
| agent cost per trial | 0.04 / 0.05 / 0.10 | 0.04 / 0.05 / 0.08 |
| input tokens | 199.9k / 253.6k / 554.3k | 214.4k / 239.9k / 399.1k |
| tool calls | 8 / 9 / 20 | 9 / 12 / 13 |

Medians are within a cent of each other and the intervals cross zero in both
directions. **The whole series, seven trials including the smoke run, cost
$0.41.**

That figure is worth stating plainly and reading carefully. It is not evidence
that Haiku is cheaper than Opus on this benchmark: this case has never run on
Opus, and the Opus figures elsewhere come from different cases. What it does
establish is that a full randomised series against this case costs less than a
euro, which puts the trial budget in a different place than the upgrade case's
$10-to-$38 trials did.

## The finding is what was not used

**Nine skills delivered, zero invoked, in every trial of the equipped arm.**
The capability probe confirms all nine were present; the trajectories show no
`Skill(` call at all.

That is the runtime case's result again on a different case and a different
model. A skill set is an offer, and this task — read two files, decide which is
right, edit one — does not meet any procedure on offer.

## What the smoke run showed, which the series then confirmed

The first trial ever run against this case scored `consistency` 0.83: five of
five mechanical criteria, and 0.5 on each of two judge criteria. It had pulled
`ext_emconf.php` up to composer's `^14.3` without establishing that the code
supports that line, and it had also edited the README's badges and requirements.

Both are behaviours this case's README predicted before it had ever run — "an
agent that simply copies one constraint into the other satisfies the letter of
the request and leaves the extension declaring something nobody checked". The
rubric scored them apart from a fix that establishes the line first. The case
discriminates.

## Reproducing

```
scripts/run-comparison OFR-TYPO3-METADATA-001 --arms control,nr \
    --primary consistency --model claude-haiku-4-5-20251001 --seed 11
scripts/analyze experiments/OFR-TYPO3-METADATA-001-20260820-204603.json
```

## Round 38, 17 September 2026 — the routing fix transfers, and changes nothing here

`experiments/OFR-TYPO3-METADATA-001-20260917-150915.json`, seed 4411, Haiku
4.5, benchmark 8.0.1, `control` against `nr`. Six trials, six valid.
`consistency` was declared as the primary endpoint before the first trial.

| | `control` | `nr` |
|---|---|---|
| `consistency` | 3/3 | 3/3 |
| `skill_invoked` | 0/3 | **3/3** |

The round was run on a prediction rather than a hunch. `scripts/routing-overlap`
shows this case sharing almost the same words with `typo3-conformance` as
OFR-TYPO3-CONSISTENT-001 does — and on that case, moving those words into the
description's opening clause took routing from 0 of 27 to 11 of 12. Every
recorded `nr` trial here predates that change: the last one resolved
`typo3-conformance-skill@v2.19.1`, and `nr` has pinned v2.19.4 since
16 September. The prediction was that the same description would route here.

**It does.** 3 of 3 against 0 of 3, Fisher exact 0.100 two-sided and 0.050
one-sided, on a case that had recorded 0 of 7 with the old wording. A
description written for one case moved a second one that nobody had touched —
which is worth more than the number, because it is the first evidence that
these description repairs generalise rather than fitting the case they were
measured on.

**And it changes nothing about the outcome.** `consistency` is 3 of 3 in both
arms. The case is passed by the base model, the skills are now reached, and
being reached makes no difference to a result that was already at the ceiling.
Cost and tool calls move by less than their intervals.

That is not a disappointment, it is the shape of the finding: routing is
necessary for a skill to matter and is not sufficient for it to. The two halves
have to be measured separately, and a case at the ceiling can only show the
first one.
