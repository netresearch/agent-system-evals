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
