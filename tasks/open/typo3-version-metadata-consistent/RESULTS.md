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

---

# The description experiment — 28 August 2026

Eight of the eleven cases measure nothing about the skills, because no skill is
ever loaded. Before spending anything on rubric work, the question worth asking
is whether that is fixable at all by the one lever a fleet can pull without a
release: the words in a skill's `description`, which are what the agent reads
when deciding whether to invoke it.

`fleets/candidate.yaml` is the only fleet allowed to point at a branch, so the
change could be measured without releasing it.

## What the run was

`scripts/run-comparison OFR-TYPO3-CONSISTENT-001 --arms nr,candidate --primary skill_invoked --model claude-haiku-4-5-20251001 --seed 191`

Twelve trials, six per arm, twelve of twelve valid. Benchmark version 2.0.0,
`claude-haiku-4-5-20251001`, judge `claude-sonnet-4-6`.

Experiment record: `experiments/OFR-TYPO3-CONSISTENT-001-20260828-140721.json`.

The two arms differ in exactly one thing: `nr` carries
`netresearch/typo3-conformance-skill@v2.19.1`, `candidate` carries the same
skill at branch `experiment/version-declarations-in-description` (`55b0c46`),
whose only change is one added sentence in the `description` naming the
artefacts this case is about — version declarations that disagree,
`composer.json` against `ext_emconf.php`, supported TYPO3 versions. Purely
additive: no trigger was removed. It is nine words over the 500-word cap, so
the branch fails the skill repository's own validator deliberately and is not
releasable as it stands.

That the arm was real is checkable rather than assumed: all six `candidate`
lock files pin `typo3-conformance-skill` at `55b0c46`, so every trial ran with
the changed description installed.

## The declared endpoint did not move

| | nr | candidate |
|---|---|---|
| `skill_invoked` | 0/6 | 1/6 |
| Wilson interval | [0.00, 0.39] | [0.03, 0.56] |
| Fisher exact p | — | 1.000 two-sided, 0.500 one-sided |

One trial in twelve loaded the skill, and it was on the changed side. That is
one observation, and the interval around it contains the other arm. Naming the
artefacts in the description did not measurably change whether the skill is
invoked on this case.

## What moved instead, and why it is not a result

Everything else in the report separates, in the direction of the changed arm
doing less:

| | nr | candidate | delta | p |
|---|---|---|---|---|
| `consistency` met | 5/6 | 1/6 | −0.81 | 0.024 |
| criteria behind it | 44 met / 5 partial / 5 not met | 25 met / 10 partial / 19 not met | | |
| agent cost, median | $0.06 | $0.03 | −0.72 | 0.041 |
| input tokens, median | 248.3k | 144.9k | −0.72 | 0.041 |
| tool calls, median | 9.5 | 6.0 | −0.78 | 0.022 |

Every one of those lines is exploratory. Only `skill_invoked` was declared, and
the rest is what the pre-declaration exists to keep out of a conclusion — a
p of 0.024 on an undeclared dimension across a report of five is not a finding.

It is, however, the obvious next hypothesis, and it points the opposite way
from the intent: the arm with the more specific description investigated less
and scored worse. Three readings, in descending order of what the evidence
supports:

1. **Chance at six per arm.** This benchmark has now watched two complete
   separations fail their own confirmation at doubled sample
   ([the upgrade case's `verification`](../typo3-extension-upgrade/RESULTS.md),
   [the review case's cost](../typo3-extension-review/RESULTS.md)), and
   recorded control trials on this very case that ranged from zero tool calls
   to eleven. A four-trial swing on a six-trial arm is inside that.
2. **The description changed the agent's reading of the task**, not its choice
   of skill: a sentence that names the exact artefacts may read as a statement
   that the ground is already covered, and shorten the investigation. This
   would be a real effect and an unwelcome one, and it is testable — the same
   two arms on a case where the work is unambiguous.
3. **Something else about the branch build.** Least supported: the lock files
   pin the intended commit, the fleets differ in no other field, and
   `check_comparable` refused nothing.

Distinguishing 1 from 2 costs another twelve trials and is worth it only if the
description lever is being pursued further.

## What it means for the eight silent cases

The lever was the cheap one, and it did not work on this case. Counted over
every equipped trial on disk, invocation is decided by the request rather than
by the skill:

| case | trials that loaded any skill |
|---|---|
| `OFR-TYPO3-EXT-001` | 41/42 |
| `OFR-TYPO3-DOCS-001` | 15/17 |
| `OFR-TYPO3-UPGRADE-001` | 23/29 |
| `OFR-TYPO3-CONSISTENT-001` | 1/15 |
| `CON-TYPO3-EXTBASE-001` | 0/6 |
| `OFR-GO-LDAP-001` | 0/5 |
| `OFR-PY-CI-001` | 0/5 |
| `OFR-TYPO3-METADATA-001` | 0/7 |
| `OFR-TYPO3-METADATA-001-BARE` | 0/3 |
| `OFR-TYPO3-RELEASE-001` | 0/4 |
| `OFR-TYPO3-RUNTIME-001` | 0/46 |

Counted by `scripts/invocation-census` over every job on disk whose fleet
resolves to at least one skill, so the table moves when the jobs do rather than
when someone remembers to retype it.

The three version-declaration cases together stand at 1 of 25, and that one is
this experiment's single candidate trial. The split is not between skills that
exist and skills that do not — the same fleet is installed throughout. It is
between requests whose own words name the work a skill claims and requests that
describe an artefact instead, and changing the description to name those
artefacts did not cross it. The finding belongs where the harness can act
on it:
[agent-harness#61](https://github.com/netresearch/agent-harness-skill/issues/61).

The branch stays unreleased. Cutting nine words to make it releasable would be
work in service of a change with no measured effect.

## Reproducing

```
scripts/run-comparison OFR-TYPO3-CONSISTENT-001 --arms nr,candidate \
    --primary skill_invoked --model claude-haiku-4-5-20251001 --seed 191
scripts/analyze experiments/OFR-TYPO3-CONSISTENT-001-20260828-140721.json
```

`fleets/candidate.yaml` must point at the experiment branch; it is the only
fleet permitted to name one, enforced by
`tests/test_fleets.py::test_only_the_candidate_fleet_may_name_a_branch`.

---

# Round two: position, not vocabulary — 28 August 2026

Round one appended the artefacts to the description's trigger list and moved
nothing. What settled it was a comparison from the same day on a different
case: `github-release-skill`, invoked 6 of 6 on *"prepare the 2.4.2 release"*,
whose description names the request's noun in its **opening clause** rather
than in a list thirty-five words later.

So round two changes position and nothing else.

| | text |
|---|---|
| `nr` (v2.19.1) | `Use when assessing TYPO3 extension quality, conformance checking, standards compliance, … TER readiness, or best practices review. Also triggers on: extension audit, quality score, …` |
| `candidate` (`6174033`) | `Use when checking which TYPO3 versions an extension declares it supports, when composer.json and ext_emconf.php disagree, or when assessing TYPO3 extension quality, …` |

Same artefacts. Nothing removed. The trigger list is untouched.

## What the run was

`scripts/run-comparison OFR-TYPO3-CONSISTENT-001 --arms nr,candidate --primary skill_invoked --model claude-haiku-4-5-20251001 --seed 233`

Twelve trials, six per arm, twelve of twelve valid. All six `candidate` locks
pin `6174033`. Experiment record:
`experiments/OFR-TYPO3-CONSISTENT-001-20260828-162519.json`.

## Position decides it

| | nr | candidate |
|---|---|---|
| `skill_invoked` | 0/6 | **6/6** |
| Wilson interval | [0.00, 0.39] | [0.61, 1.00] |
| Fisher exact p | — | **0.002** two-sided, 0.001 one-sided |

Against round one, on the same case, the same model and the same skill:

| where the artefacts are named | invoked | p |
|---|---|---|
| appended to the `Also triggers on:` tail | 1/6 | 1.000 |
| in the opening `Use when` clause | **6/6** | **0.002** |

A description is not a bag of keywords. The same words, moved thirty-five words
earlier, take this case from never routing to always routing. That is the
second declared endpoint in this benchmark to separate completely at a p a
conventional threshold accepts, and both were found in one day: one by adding
the skill, one by moving its first sentence.

**And this one is releasable.** Round one's branch was nine words over the skill
repository's cap and failed its own validator. Round two is a rewrite rather
than an append and passes.

## Reached, and no better

| | nr | candidate |
|---|---|---|
| `consistency` met | 3/6 | 3/6 |
| Cliff's delta | — | +0.06, p 0.892 |
| criteria behind it | 37 met / 5 partial / 12 not met | 39 met / 6 partial / 9 not met |
| agent cost, median | $0.04 | $0.04 |
| tool calls, median | 7.0 | 7.5 |

Six trials loaded a conformance skill on a conformance question and scored what
six trials without it scored. The criteria move slightly in the equipped arm's
favour — three fewer *not met* — and four of the twelve trials sit within one
judge step of the threshold, so the counts carry nothing.

That is now the third case where routing was fixed and the outcome did not
follow: the release case (0/6 → 6/6, mechanical outcome 0/6 both), the
documentation and upgrade cases where the skill was always invoked, and this
one. **Getting the skill loaded is a solved problem with a known mechanism.
Getting the work to come out better is not.**

## Reproducing

```
scripts/run-comparison OFR-TYPO3-CONSISTENT-001 --arms nr,candidate \
    --primary skill_invoked --model claude-haiku-4-5-20251001 --seed 233
scripts/analyze experiments/OFR-TYPO3-CONSISTENT-001-20260828-162519.json
```
