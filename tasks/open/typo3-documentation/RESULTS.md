# OFR-TYPO3-DOCS-001 — recorded results

Two fleets, three trials each, six of six valid. Measured 21 August 2026 on
**`claude-haiku-4-5-20251001`**, benchmark version 0.6.2.

The first case in this repository where the equipped arm moves a dimension, and
the first where a skill is invoked at all. Both halves matter, and the second is
the interesting one: the skill was reached for, and the work still came out
wrong.

## What the run was

`scripts/run-comparison OFR-TYPO3-DOCS-001 --arms control,nr --primary documentation --model claude-haiku-4-5-20251001 --seed 21`

Randomised blocks, one trial per arm per block, `documentation` declared as the
primary endpoint before the first trial. The runner stopped after the discovery
round: the endpoint moved but did not separate completely, which is the rule.

Experiment record: `experiments/OFR-TYPO3-DOCS-001-20260821-100943.json`.

## Nobody passed the mechanical bar

| | control | nr |
|---|---|---|
| `docs: ok` | 0/3 | 0/3 |
| `documentation` met | 0/3 | 2/3 |
| criteria behind it | 13 met / 3 partial / 14 not met | 18 met / 8 partial / 4 not met |
| Cliff's delta | — | +0.78 |
| permutation p | — | 0.200 |

The mechanical outcome is flat at zero. The rubric is not, and the gap between
those two lines is the whole result.

## The arms fail differently, and that is the finding

The per-trial mechanical output says more than any score:

| trial | outcome |
|---|---|
| control 1 | `Index.rst has no toctree; nothing is reachable from it` |
| control 2 | `no Documentation/ directory` |
| control 3 | `no Documentation/ directory` |
| nr 1 | 7 toctree entries; `guides.xml <project>` has no title, no release |
| nr 2 | 6 toctree entries; `guides.xml does not parse: not well-formed, line 47` |
| nr 3 | 9 toctree entries; `guides.xml <project>` has no title, no release |

Two of three control trials did not create a `Documentation/` directory at all.
All three equipped trials built a documentation tree with six to nine reachable
documents — and all three produced a `guides.xml` that will never render.

So the difference the fleet makes here is **whether the work happens**, not
whether the artifact is correct. Those are separate claims and the numbers
support only the first.

## The skill was invoked. That is new.

| trial | `Skill(` calls |
|---|---|
| nr 1, 2, 3 | `typo3-docs`, once each |
| control 1, 2, 3 | none |

Every earlier case in this repository recorded the same thing: skills delivered,
zero invoked. The version-metadata case had nine present and none reached for,
on this same model. Here the routing worked in three trials of three — the
request names documentation, and a documentation skill is on offer.

Which makes the wrong output a different kind of evidence. It is not a routing
failure and it is not the absence of a capability. The capability was reached
for, and what came back was a `guides.xml` in an invented namespace
(`https://guides.typo3.org/xmlschema/guides-1.1`, with `<guide>`, `<title>` and
a `<project>` carrying the extension key as text). The real format, measured
against four independent projects that render on docs.typo3.org — georgringer/news,
FriendsOfTYPO3/extension_builder, TYPO3-Documentation/TYPO3CMS-Reference-TCA and
helhum/typo3-console — is `xmlns="https://www.phpdoc.org/guides"` with
`<project title= release= version= copyright=/>`.

The skill carries that skeleton, correctly, at `references/guides-xml.md`. No
trial read it. `SKILL.md` mentions the file once, in a reference table, as
"build config, interlinks" — which is not what an agent writing documentation
from nothing is looking for, and there is no skeleton in `assets/` to copy.
Recorded for the retro loop rather than patched here; see
[docs/open-forward-review.md](../../../docs/open-forward-review.md) section 10.

## Cost

| | control | nr |
|---|---|---|
| agent cost per trial | 0.02 / 0.12 / 0.14 | 0.21 / 0.23 / 0.25 |
| input tokens | 97.2k / 262.5k / 577.3k | 833.7k / 978.5k / 1.04M |
| tool calls | 5 / 17 / 28 | 27 / 32 / 33 |

Cost and input tokens separate completely, in the direction of the equipped arm
costing more: Cliff's delta +1.00, permutation p 0.100 — the smallest p three
trials per arm can produce. Both lines are **exploratory**. Only `documentation`
was declared in advance, and reading a completely separated exploratory line as
a finding is exactly what the declaration exists to prevent.

What can be said without a p-value is the ratio: the equipped arm spent roughly
four times the input tokens and about twice the money, and in two of three
trials the control arm produced no documentation directory to show for its
cheaper run.

## Reproducing

```
scripts/run-comparison OFR-TYPO3-DOCS-001 --arms control,nr \
    --primary documentation --model claude-haiku-4-5-20251001 --seed 21
scripts/analyze experiments/OFR-TYPO3-DOCS-001-20260821-100943.json
```

## One instrument failure came out of this case

The first trial ever run against it was discarded as `INVALID_INFRASTRUCTURE`.
The agent wrote no `guides.xml`, the collector's `cp` therefore left no
`guides.after.xml`, and the criterion reading it raised rather than returning
False — so a plain agent shortcoming erased the measurement of itself, and only
ever when the agent did badly. Recorded as instrument failure 19 in
[docs/instrument-failures.md](../../../docs/instrument-failures.md).
