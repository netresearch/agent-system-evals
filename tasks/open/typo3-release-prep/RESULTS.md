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

Held against the documentation case, measured the same day on the same model,
this stops being a repetition of "skills go unused" and becomes something more
specific. There, `typo3-docs` was invoked in three trials of three. The request
was "This extension has no documentation on docs.typo3.org. Please give it
some." Here the request is a release, and two of the four version locations
happen to be documentation files — but nothing in the request says so.

**Routing keys on the vocabulary of the request, not on where the work turns
out to live.** That is a property of the whole system rather than of any skill
in it, which is what an Open Forward Review is for.

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
