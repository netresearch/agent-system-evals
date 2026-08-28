# OFR-TYPO3-RELEASE-001 — recorded results

Two fleets, three trials each, six of six valid. Measured 21 August 2026 on
**`claude-haiku-4-5-20251001`**, benchmark version 0.7.0.

The cleanest result this repository has produced, and it is a null one: seven
trials, two fleets, and a single outcome repeated without variation.

## What the run was

`scripts/run-comparison OFR-TYPO3-RELEASE-001 --arms control,nr --primary release --model claude-haiku-4-5-20251001 --seed 31`

Randomised blocks, one trial per arm per block, `release` declared as the
primary endpoint before the first trial. The runner stopped after the discovery
round.

Experiment record: `experiments/OFR-TYPO3-RELEASE-001-20260821-125821.json`.

## Seven trials, one outcome

Every trial of both arms, and the smoke run before them, produced the same
mechanical result byte for byte:

```
requested: 2.4.2
ext_emconf.php: 2.4.2
Documentation/guides.xml: 2.4.1
CHANGELOG.md mentions: 1
Documentation/Changelog/Index.rst mentions: 0
release: incomplete
```

| | control | nr |
|---|---|---|
| `release: ok` | 0/3 | 0/3 |
| `release` met | 0/3 | 0/3 |
| criteria behind it | 20 met / 1 partial / 12 not met | 19 met / 2 partial / 12 not met |
| Cliff's delta | — | −0.33 |
| permutation p | — | 1.000 |

This is worth more than the p-value next to it. "No difference detected" is the
weak claim three trials per arm can support; "the identical failure, seven times
out of seven, with no spread inside either arm" is a description of the
behaviour rather than a test of it.

And the two places nobody touches are both documentation files. A TYPO3
extension carries its version in four locations — `ext_emconf.php`,
`Documentation/guides.xml`, `CHANGELOG.md` and
`Documentation/Changelog/Index.rst`. Every trial found the two that live where
code review looks and missed the two that live under `Documentation/`.

## Nothing was invoked

| | `Skill(` calls |
|---|---|
| control 1, 2, 3 | none (the arm provisions nothing) |
| nr 1, 2, 3 | none |

Eight skills present in the equipped arm, none reached for — including
`typo3-docs`, which ships `scripts/check-guides-xml-version-sync.sh`, a script
whose entire purpose is the check every trial failed.

### Corrected 22 August: the first reading of this was wrong

This section originally concluded that *routing keys on the vocabulary of the
request rather than on where the work turns out to live* — the request says
"release", nothing in it says "documentation", so the documentation skill was
never considered.

That reading does not survive a look at what the fleet contains. The
organisation publishes 42 skill repositories. One of them is
`netresearch/github-release-skill`, whose description begins:

> Use when creating releases, version bumps, tagging, release health checks, or
> when user says 'release', 'tag', 'version bump'.

The instruction for this case is *"Please prepare the 2.4.2 release of this
extension"*. The vocabulary was there. **The capability was not: neither `nr`
(eight skills) nor `nr-full` (twelve) carries a release skill.**

So this case did not measure routing. It measured fleet composition, and the
answer is that the fleet has no release capability to select. That is a finding
about the arm under test rather than about the agent, and it is a different and
smaller claim than the one first written here.

What survives of the original observation is narrower and still worth keeping:
`typo3-docs` *is* in the fleet, it ships
`scripts/check-guides-xml-version-sync.sh` — a script whose only purpose is the
check every trial failed — and its description names `guides.xml` but never
mentions releases or version bumps. So a relevant capability was present,
described in a way that does not reach this task. That is a routing observation,
about one skill, and it is testable: change the description and re-run.

The documentation case remains the contrast that started this, and it still
holds there — `typo3-docs` was invoked in three trials of three when the request
named documentation.

## Cost

| | control | nr |
|---|---|---|
| agent cost per trial | 0.08 / 0.09 / 0.11 | 0.08 / 0.08 / 0.09 |
| input tokens | 466.6k / 542.1k / 635.1k | 356.9k / 494.0k / 505.5k |
| tool calls | 16 / 21 / 25 | 16 / 18 / 26 |

The equipped arm is marginally cheaper here, with intervals crossing zero in
both directions (p 0.200 on cost, 0.400 on tokens, 1.000 on tool calls). All
three lines are exploratory. The direction is the opposite of the documentation
case's, where the equipped arm cost about twice as much — which is consistent
with skills being loaded and read there, and neither loaded nor read here.

## What the case cannot say

That a fleet does not help on this task is not evidence that the fleet does not
help. The measurement is one task, one model, three trials per arm, and the
mechanism it exposes — routing that never fires — is upstream of anything the
skills could have contributed. A fleet whose capability is never selected is
being measured on its selection, not on its content.

## Reproducing

```
scripts/run-comparison OFR-TYPO3-RELEASE-001 --arms control,nr \
    --primary release --model claude-haiku-4-5-20251001 --seed 31
scripts/analyze experiments/OFR-TYPO3-RELEASE-001-20260821-125821.json
```

---

# The composition experiment — 28 August 2026

Every earlier run of this case reported zero skill invocations and was read as a
routing result. That reading was never sound. The request is *"prepare the 2.4.2
release"*; the organisation publishes `netresearch/github-release-skill`, whose
description activates on "release", "tag" and "version bump"; and **no fleet
under test carried it**. The case was measuring what the fleet contains.

## What the run was

`scripts/run-comparison OFR-TYPO3-RELEASE-001 --arms nr,nr-release --primary skill_invoked --model claude-haiku-4-5-20251001 --seed 211`

Twelve trials, six per arm, twelve of twelve valid. `nr-release` is `nr` plus
`netresearch/github-release-skill@v0.11.0` and nothing else — the `add:` key in
`fleets/nr-release.yaml` inherits every other version from `nr` rather than
restating it, so the arms differ in exactly one skill.

Experiment record: `experiments/OFR-TYPO3-RELEASE-001-20260828-152051.json`.

## The clearest result this benchmark has produced

| | nr | nr-release |
|---|---|---|
| `skill_invoked` | 0/6 | **6/6** |
| Wilson interval | [0.00, 0.39] | [0.61, 1.00] |
| Fisher exact p | — | **0.002** two-sided, 0.001 one-sided |

Every trial with the skill present loaded it; no trial without it loaded
anything. This is the first declared endpoint in the benchmark to separate
completely at a p a conventional threshold accepts, and it settles the question
the case had been mis-answering: **the zero was composition, not routing.**

It also settles it in the direction that matters for reading every other case:
routing works. An agent offered a skill whose description names the noun in the
request reaches for it, six times out of six, with no prompting and no change to
the request.

## And loading it did not fix the task

| | nr | nr-release |
|---|---|---|
| mechanical outcome | 0/6 | 0/6 |
| `release` dimension met | 0/6 | 1/6 |
| Cliff's delta | — | −0.25, p 0.478 |
| criteria behind it | 39 met / 3 partial / 24 not met | 25 met / 7 partial / 34 not met |

The mechanical check — the one decided by the framework rather than by a judge —
is zero on both sides. Six trials loaded a release skill built for exactly this
work and not one of them produced a correct release preparation. The judged
dimension moved by one trial in the *worse* direction, and nine of the twelve
trials score within one judge step of the threshold, so that number carries
nothing either way.

Spend did not move (delta +0.00 on cost, −0.06 on tokens, both p ≈ 1), but the
dispersion inside `nr-release` is wide: three trials at $0.03–$0.04 with seven to
nine tool calls, three at $0.12–$0.18 with twenty-four to thirty-four. The same
fleet, the same request, two quite different behaviours. Exploratory.

## What the two experiments say together

Run against the description experiment on
[the restraint case](../typo3-version-metadata-consistent/RESULTS.md), the pair
separates two mechanisms that had been treated as one:

| lever | measured | result |
|---|---|---|
| the skill's own wording | 12 trials, 28 Aug | 0/6 → 1/6, p 1.000 — no effect |
| whether the skill is in the fleet | 12 trials, 28 Aug | 0/6 → **6/6**, p 0.002 |

A stack is reached for when it *contains* something the request names. Rewriting
what a skill says about itself did not do it; carrying the right skill did. The
practical consequence is that fleet composition is the lever worth spending on,
and that eight silent cases are a question about what the fleets carry before
they are a question about how skills describe themselves.

The second half is the harder finding: reaching the skill and doing the job are
different things, and this case now shows the gap directly. Six of six trials
loaded the release skill; zero of six prepared the release.
[agent-harness#61](https://github.com/netresearch/agent-harness-skill/issues/61)
carries that thread.

## One thing the reader should weigh

The added skill names this case's target extension. `github-release-skill`
carries two references that mention `t3x-nr-image-optimize` — a citation for
Packagist blocking a version rather than a package, evidenced by an observed
`v2.4.0`/`v1.3.0` pair, and one of three repository names attributing a
workflow pattern. The benchmark's contamination check caught both the moment
the fleet carried the skill, and both were judged learnings and recorded in
`tests/contamination-decisions.yaml` with the reasoning written out; the
decorative one is filed upstream as
[github-release-skill#92](https://github.com/netresearch/github-release-skill/issues/92).

Neither describes this release. They describe a retag that already happened and
a workflow pattern, on a repository whose current state the documents do not
give. And the outcome is the check on that judgement: the arm carrying them
prepared the release correctly zero times out of six, exactly as the arm
without them did. Target knowledge that helps nobody do the task is a weak
contaminant, but the reader is entitled to know it was there.

## Reproducing

```
scripts/run-comparison OFR-TYPO3-RELEASE-001 --arms nr,nr-release \
    --primary skill_invoked --model claude-haiku-4-5-20251001 --seed 211
scripts/analyze experiments/OFR-TYPO3-RELEASE-001-20260828-152051.json
```
