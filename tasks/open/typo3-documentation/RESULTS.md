# OFR-TYPO3-DOCS-001 — recorded results

Two fleets, three trials each, six of six valid. Measured 21 August 2026 on
**`claude-haiku-4-5-20251001`**, benchmark version 0.6.2.

That version matters here. The namespace check described below was added
*after* this series, which is why benchmark 0.7.0 exists: a run under 0.7.0
is not comparable with the numbers on this page, because the same files
would score differently.

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
for, and what came back was a `guides.xml` in a namespace that does not exist —
**a different invented one each time**:

| trial | namespace declared |
|---|---|
| smoke | `https://guides.typo3.org/xmlschema/guides-1.1` |
| nr 1 | `https://guides.typo3.org/2024` |
| nr 2 | (file does not parse) |
| nr 3 | `https://typo3.org/reST/GuideSchema/v1` |

Not one wrong recollection repeated, then, but a plausible-looking URL composed
afresh on each attempt. In all three parseable files `<project>` carries no
attributes at all — the extension key sits in the element text. The real format,
measured
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

---

# The skill fix, measured and disproven

Two arms, three trials each, six of six valid. Measured 22 August 2026 on
**`claude-haiku-4-5-20251001`**, benchmark version 0.9.0.

`scripts/run-comparison OFR-TYPO3-DOCS-001 --arms nr,candidate --primary documentation --model claude-haiku-4-5-20251001 --seed 111`

Experiment record: `experiments/OFR-TYPO3-DOCS-001-20260822-170352.json`.

`candidate` is `nr` with `netresearch/typo3-docs-skill` moved from v2.16.0 to
v2.18.0 — the release carrying the change this case's first series produced:
`assets/guides.xml.dist` to copy, and a step 0 in the Core Workflow reading
*"No `Documentation/` yet? Copy `assets/guides.xml.dist` to
`Documentation/guides.xml`; never write one from memory — the namespace is
phpDocumentor's, not TYPO3's."*

## It did not work

| | nr (v2.16.0) | candidate (v2.18.0) |
|---|---|---|
| mechanical `docs: ok` | 0/3 | 0/3 |
| `documentation` met | 0/3 | 0/3 |
| criteria | 12 met / 7 partial / 11 not met | 15 met / 9 partial / 6 not met |
| permutation p | — | 1.000 |

Every candidate trial produced a `guides.xml` that will not render:

| trial | outcome |
|---|---|
| candidate 1 | namespace `https://guides.typo3.org/xml-ns` |
| candidate 2 | does not parse — unbound prefix, line 8 |
| candidate 3 | `<project>` has no `title`, no `release` |

Three more invented namespaces, none of them one seen before. Across the two
series this case has now recorded **seven distinct fabricated namespaces** and
not one correct file.

## What was verified before concluding

The fix reached the container: `assets/guides.xml.dist` is in the provisioned
skill directory and `SKILL.md` carries step 0 verbatim. The skill was invoked in
three trials of three. And **no trial referenced `guides.xml.dist` or
`references/guides-xml.md` in a single tool call.**

So the instruction was present, loaded, and ignored. The earlier reading of this
case — *on a small model a pointer to a reference file is not the content* — was
too generous. The correction was not a pointer. It was a direct imperative in
the file the agent had just loaded, and it changed nothing.

## Why the skill's own gates did not catch it either

Both mechanical checks the skill ships give a false pass on exactly this defect:

- `scripts/validate_docs.sh` tests `[ -f "$DOC_DIR/guides.xml" ]` and prints
  `✅ guides.xml found (modern PHP-based rendering)`. It never parses the file.
  One trial of six ran it, on a file in an invented namespace, and was told the
  documentation was fine.
- Checkpoint `TD-05` is `contains "<project"` against `guides.xml`. A
  hallucinated `<project>nr-image-sitemap</project>` satisfies it.

That is the lever this series actually found, and it is not prose. A check that
parses the file, asserts the phpDocumentor namespace and requires `title` and
`release` as attributes would fail every one of the seven recorded files. Filed
upstream.

## The honest status of the earlier fix

`netresearch/typo3-docs-skill` v2.18.0 is a real improvement to a real gap — the
skeleton was genuinely unreachable — and it does not fix this case. Both are
true, and only the second was measured. It was shipped on the first.


---

# The second skill fix, measured against the expectation written before it ran

Two arms, three trials each, six of six valid. Measured 26 August 2026 on
**`claude-haiku-4-5-20251001`**, benchmark version 0.9.0.

`scripts/run-comparison OFR-TYPO3-DOCS-001 --arms nr,candidate --primary documentation --model claude-haiku-4-5-20251001 --seed 121`

Experiment record: `experiments/OFR-TYPO3-DOCS-001-20260826-100039.json`.

`candidate` is `nr` with `typo3-docs` at v2.19.0, where `validate_docs.sh` and
checkpoint `TD-05` parse `guides.xml` instead of looking at its name. Before
the run, `fleets/candidate.yaml` stated what to expect: **`documentation` would
not move**, because the change is a check and not a generator — it fails when
`guides.xml` is wrong and writes no correct one — and nothing in a trial
executes checkpoints, while the validator had been run in one recorded trial
of six.

## It did not move

| | nr (v2.16.0) | candidate (v2.19.0) |
|---|---|---|
| mechanical `docs: ok` | 0/3 | 0/3 |
| `documentation` met | 1/3 | 1/3 |
| criteria | 15 met / 5 partial / 10 not met | 17 met / 5 partial / 8 not met |
| permutation p | — | 1.000 |

**No candidate trial ran the validator.** Three of three invoked the skill,
none invoked `validate_docs.sh`, so the check that now refuses a fabricated
namespace was never reached. That is the result the expectation named, and it
says where the lever sits: not in the skill's checks, which are correct, but
in whatever makes an agent run them.

Four more namespaces were invented across the six trials, none seen before —
one of them `https://www.phpdoc.org/guide`, the singular of the real one, the
closest miss on record. Eleven distinct fabricated namespaces now stand across
three series of this case.

## What this run is evidence of

Not that v2.19.0's check is wrong: that was settled against ten recorded files
before the release, nine refused and the one correct file passed. This run
shows that a correct check an agent does not run has no effect on what the
agent produces — which is a statement about the second hop, and the same
statement v2.18.0's failure made about prose.

## One instrument note

CI flagged v2.19.0 for contamination as soon as the candidate fleet carried
it: a comment in the new check named this case's id. A skill written from a
measurement had carried the measurement's identifiers back into the arm under
test. Fixed upstream in v2.19.1, which the candidate now pins; the checks are
byte-identical apart from three comments.
