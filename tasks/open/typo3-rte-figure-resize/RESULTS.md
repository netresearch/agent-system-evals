# OFR-TYPO3-RESIZE-001 — recorded results

Two fleets, three trials each, six of six valid. Measured 29 August 2026 on
**`claude-haiku-4-5-20251001`**, benchmark version 2.0.0.

Nobody fixed the reported defect, and all six said they had. What makes the
round worth recording is not the zero but its uniformity: six trials, two
fleets, and the same wrong line of Fluid in every one of them, character for
character.

## What the run was

`scripts/run-comparison OFR-TYPO3-RESIZE-001 --arms control,nr --primary mechanical_outcome --model claude-haiku-4-5-20251001`

Randomised blocks, one trial per arm per block, `mechanical_outcome` declared
as the primary endpoint before the first trial, seed 307. The runner stopped
after the discovery round: `0/3 against 0/3, p 1.000`.

Experiment record: `experiments/OFR-TYPO3-RESIZE-001-20260829-093358.json`.

## Six trials, one outcome

| | control | nr |
|---|---|---|
| `figure resize: ok` | 0/3 | 0/3 |
| `own checks: ok` | 3/3 | 3/3 |
| `Skill(` calls | 0/3 | 0/3 |
| closing message declares the fix done | 3/3 | 3/3 |
| rendered output contains an unparsed Fluid expression | 3/3 | 3/3 |

The four failing tests are the same four in every trial, and the same four the
pinned commit fails before anything is changed:

```
percentageResizeWithCaptionKeepsWidthOnFigure
percentageResizeWithoutCaptionKeepsWidthOnImage
pixelResizeWithCaptionKeepsWidthOnFigure
percentageResizeOnLinkedImageKeepsWidthAndLink
```

`Tests: 13, Assertions: 14, Failures: 4` in all six, identical to the
baseline the case was built against.

## The same wrong line, six times

Every trial located the right place. Each one carried the stored figure style
through the parser, the DTO and the resolver, and then wrote it into the
template as a nested inline ViewHelper call:

```html
style="{f:if(condition: image.figureStyle, then: image.figureStyle, else: f:if(condition: image.width, then: 'max-width: {image.width}px'))}"
```

Fluid does not parse that. The inner call sits inside the outer call's
argument list and carries a quoted string with a braced expression in it; the
parser gives up and the whole construction reaches the browser as text. The
rendered `<figure>` in all six trials carries the expression verbatim in its
`style` attribute — which is why the width assertions fail on a string that
contains the word `figureStyle` rather than a width.

Six trials in two fleets produced that line byte for byte. It is not six
agents making six mistakes; it is one construction the model reaches for, and
nothing in the run tells it the construction is void.

## Why nothing told them

The unit suite stayed green in all six (`own checks: ok` 3/3 and 3/3), and it
could not have gone red: it exercises PHP classes and never renders a
template. Every trial verified against it — the transcripts mention `phpunit`
between 0 and 73 times — and read green as done.

A template change is verified by rendering it. That is the finding of this
round, and it is not a property of this extension: any project whose output
is produced by a template engine has a class of change its unit suite cannot
observe, and an agent that does not know this will report success from a
suite that never loaded the file it edited.

## Routing

`Skill(` was called in 0 of 3 equipped trials. The eight skills in `nr` were
installed and none of them opens on a request of this shape — a user reports
wrong output and asks for it to be sorted out. The equipped arm therefore
measured the base model a second time, which is what the two identical
columns above are.

## What the artefacts could not show

`git-diff.patch` is 230 to 281 bytes in every trial: the `git status` lines
alone, no hunks, although each trial left four or five files modified. Why the
diff came out empty cannot be established from this repository — the round ran
on a working copy, and the case was first committed at 11:03, forty-five
minutes after the last trial finished. The collector that produced these
patches is in no commit.

What the repository does record is that the collector was rewritten twice
within three hours of this round (`4f414b8`, 11:26) and again later, and that
its present form diffs against the root commit and covers the working tree
rather than `HEAD`. Whatever the cause here, the empty patch belongs to the
instrument and not to the trials, and this round's patches are not evidence
about what the agents changed. The `git status` lines and the rendered output
are.

Two further jobs sit in `jobs/` for this case and are not in the table above,
both from before the experiment record opened: `control-20260829-090402`, whose
check died on `cp: cannot stat '/tests/...'` because the case's tests directory
is not mounted in the environment container, and `control-20260829-091348`,
which reached the same `Tests: 13 … Failures: 4`. The functional test is
embedded in the collector since, which is what the long comment in `task.toml`
records.

## What this round asks next

The gap is not knowledge of the bug — every trial found the right method in
the right class. The gap is that no trial ever rendered the thing it changed,
and no skill claimed the request. Both halves are addressable: a description
that opens on a reported defect would route, and a skill that is read would
say that a template change is proved by rendering it.
