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
rather than `HEAD`. What follows for this round is only that the patch contents
are unavailable: they cannot say what the trials changed, in either direction.
The `git status` lines and the rendered output can, and everything above rests
on those.

Two further jobs sit in `jobs/` for this case and are not in the table above,
both from before the experiment record opened: `control-20260829-090402`, whose
check died on `cp: cannot stat '/tests/...'` because the case's tests directory
is not mounted in the environment container, and `control-20260829-091348`,
which reached the same `Tests: 13 … Failures: 4`. The functional test is no
longer copied from a mount: `tests/FigureResizeWidthRenderingTest.php` is the
source a reader should read, `task.toml` carries the same PHP verbatim inside
the collector so that it exists in no image the agent can reach, and
`tests/test_case_check_matches_its_source.py` fails if the two drift apart.

## What this round asks next

The gap is not knowledge of the bug — every trial found the right method in
the right class. The gap is that no trial ever rendered the thing it changed,
and no skill claimed the request. Both halves are addressable: a description
that opens on a reported defect would route, and a skill that is read would
say that a template change is proved by rendering it.

## Round 35, 17 September 2026 — discarded by construction

`experiments/OFR-TYPO3-RESIZE-001-20260917-123224.json`, seed 4111, Haiku 4.5,
benchmark 7.3.0, `nr` against `candidate` carrying typo3-testing v5.21.2. It
read 0 of 3 against 0 of 3, p 1.000, and it measured nothing: the functional
check died three tests into thirteen on PHP's default memory limit, before
PHPUnit printed a single failure (`docs/instrument-failures.md` 33). Two of the
six agents hit the same wall while working.

The job directories stay on disk under their names so the discard can be
checked. They are excluded from every figure here.

The experiment record still reads `valid_trials: {nr: 3, candidate: 3}`. That
is what the gate said while the round ran, and it is left standing rather than
edited: it is the evidence that the gate could not tell a crashed check from a
failing one. `scripts/analyze` on the same record now answers differently —
`0 valid of 3` in both arms, each trial named with its reason, and "an arm has
no valid trial; there is nothing to compare" — because the case now declares
what proves its check produced a verdict at all (`ran_if` in `task.toml`).

**One number survives, and it is the one the mechanical check could not have
produced anyway.** `Skill(` was called in 0 of 3 `candidate` trials. That arm
carried a description opening on a reported defect and on proving a change to
rendered output — the change made precisely so a request of this shape reaches
the skill. At three trials this is weak evidence and not a refutation, but it
is evidence, and it points the same way the August round did: a request that
reports wrong output and asks for it to be sorted out did not reach a skill,
with or without the new opening clause.

Two readings of the August round need correcting in light of this one:

- **The absence of unparsed Fluid here is the crash, not a change in
  behaviour.** The `{f:if` text counted in August comes from PHPUnit's failure
  messages, which this run never reached.
- **Nothing here says the new rules do not work.** They were never read: the
  skill was not opened, and the check that would have shown a rendered result
  did not run.

The round will be repeated on the repaired environment.

## Round 36, 17 September 2026 — the description opens on the request and still does not route

`experiments/OFR-TYPO3-RESIZE-001-20260917-133849.json`, seed 4211, Haiku 4.5,
benchmark 8.0.0, on the repaired environment. Six trials, **six valid** — the
check ran to a verdict in every one of them, which round 35 could not say.

| | `nr` | `candidate` |
|---|---|---|
| `figure resize: ok` | 0/3 | 0/3 |
| `Skill(` calls | 0/3 | 0/3 |
| trials that added a test file | 2/3 | 1/3 |
| trials ending on the baseline `Failures: 4` | 3/3 | 2/3 |

`candidate` carried typo3-testing v5.21.2, whose description opens on a
reported defect and on proving a change to rendered output, and whose body
carries two rules at the top: a report becomes a failing test before it becomes
a fix, and a template change is proved by rendering it. Fisher exact p 1.000 on
the primary endpoint and on routing.

**The description did not route, and the rules were therefore never read.**
This is the case's second measured zero on `skill_invoked` and the first one
where a description was written for this exact request shape. Six trials is
thin, but the direction is not ambiguous: 0 of 3 with the new opening clause,
0 of 3 without it.

**Nor did the behaviour differ.** Two trials added a test file — one in each
arm, against the hypothesis rather than for it — and both added **unit** tests:
`ImageAttributeParserTest`, `ImageRenderingDtoTest`. That is precisely the
choice the unread rule forbids, on a case whose defect lives in a Fluid
template that no unit suite renders. Every trial changed production code (two
to seven files in the diff, and the repaired collector now records the hunks),
and five of six ended on the pinned commit's own `Failures: 4`. One
`candidate` trial ended on `Failures: 8`: it changed the rendering path and
made it worse.

## What the two cases say together

RELEASE-001 and RESIZE-001 were both approached by naming things in a
description, and only one moved.

| | RELEASE-001 | RESIZE-001 |
|---|---|---|
| what the description named | four files a version lives in | the occasion, and that rendered output needs proving |
| what it asked for | artefacts to produce | a procedure to follow |
| `skill_invoked` | 1/6 and 0/6 | 0/3 and 0/3 |
| endpoint | 6/6 against 1/6 | 0/3 against 0/3 |

**A description moves which artefacts an agent produces. It does not move how
the agent works.** Naming `CHANGELOG.md` got `CHANGELOG.md` written by agents
that never opened the skill; naming a reported defect did not get a failing
test written first, and did not even get the skill opened. The documentation
case had already shown the negative half of this — a description moved the
output directory and could not move a file convention the model already holds
— and this is the same boundary from the other side: an artefact is a noun the
description can hand over, a procedure is not.

What follows for this case is that the next thing to try is not another
description. Either the rules have to reach the agent some other way, or the
case measures something a small model does not do regardless of what it is
told.
