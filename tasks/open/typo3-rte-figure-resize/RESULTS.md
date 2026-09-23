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

## Round 39, 17 September 2026 — the instrument answers, and the answer is the same one

`scripts/run-comparison OFR-TYPO3-RESIZE-001 --arms control,nr --primary
mechanical_outcome --model claude-haiku-4-5-20251001 --seed 4311`, benchmark
version 10.0.0. Experiment record:
`experiments/OFR-TYPO3-RESIZE-001-20260917-211545.json`.

**Six of six valid.** That is the whole reason this round exists. Rounds 35
and 36 read `0 valid of 3` on both sides because the functional check died
of a memory wall before PHPUnit printed a line (instrument failure 33), and
a run that produces no verdict cannot be distinguished from a run whose
agents all failed. With `memory_limit=1G` in the image and the target
installed from a committed lock, every trial's artefact now carries `Tests:
13, Assertions: 14, Failures: 4` — the same figures the pinned commit
produces before anything is changed.

**And the result is August's, digit for digit.**

| | control | nr |
|---|---|---|
| `figure resize: ok` | 0/3 | 0/3 |
| `Skill(` calls | 0/3 | 0/3 |
| `Tests: 13 … Failures: 4` | 3/3 | 3/3 |
| the nested `f:if` in the added lines | 3/3 | 3/3 |

The construction is the one round one named, and finding it again is the
point. In August every trial wrote it straight into the `style` attribute.
Here every trial wraps it in an `f:variable` first:

```html
<f:variable name="figureStyle" value="{f:if(condition: image.figureStyle, then: image.figureStyle, else: f:if(condition: image.width, then: 'max-width: {image.width}px'))}
```

The `value` expression is byte-identical in all six; four trials name the
variable `figureStyle` and two `figureStyleAttr`, which is the whole of the
variation between them.

Same nesting, new packaging, and Fluid parses it no better: the rendered
`<figure>` carries the expression verbatim in `style`, which is what the
four assertions compare against a width. Between the two rounds the image
moved from PHP 8.3 to 8.5 and the target from TYPO3 13.4 to 14.3.7, and the
model still reaches for this construction six times out of six. It is a
property of the model, not of a toolchain.

**One thing the August round could not report, this one can.**
`git-diff.patch` was 230 to 281 bytes then — the `git status` lines and no
hunks — and the section above says the reason cannot be established. Here
the patches are 8.6 to 17.7 kB and carry every hunk, which is how the
`f:variable` line above is quoted rather than inferred. The collector was
rewritten twice after that round; this round is the first to show it working
on this case.

**A separation nobody declared, and it is not the endpoint.** `nr` ran the
case at roughly half the cost of `control` on all three measures, with no
overlap between the arms:

| | control | nr |
|---|---|---|
| tool calls | 75, 83, 90 | 43, 44, 49 |
| input tokens | 4.21M, 5.84M, 7.51M | 2.06M, 2.87M, 3.44M |
| agent cost (USD) | 0.63, 0.94, 1.05 | 0.36, 0.48, 0.57 |

Cliff's delta is −1.00 on each, and at three trials per arm the smallest
attainable permutation p is 0.100, so complete separation is the strongest
signal this size can produce and it is not a finding. What makes it worth
recording is that it happens with `Skill(` at 0/3: no skill was loaded in
either arm, so whatever produced the difference is not a skill being read.
The two arms end alike — both name the right classes, both declare the fix
done, both fail the same four tests, and the judge scores 6 met / 0 partial
/ 6 not met on either side — so this is not an arm that gives up sooner. The
cause is not established here, and the next round is on a different
question.

**What `nr` is on this case.** It pins `typo3-testing-skill` v5.20.3 and
loads nothing, so this column measures the base model a second time, exactly
as the August round says. The comparison that asks whether the skill helps
is `nr` against `candidate`, which carries v5.21.2 and the two rules this
case is about; rounds 35 and 36 were that comparison and the instrument took
both.

## Round 40, 17 September 2026 — the same pair again, at a second seed

`scripts/run-comparison OFR-TYPO3-RESIZE-001 --arms nr,candidate --primary
mechanical_outcome --model claude-haiku-4-5-20251001 --seed 4411`, benchmark
version 10.0.0. Experiment record:
`experiments/OFR-TYPO3-RESIZE-001-20260917-215131.json`. Six of six valid.

This is round 36's pair at a second seed — a replication, not a first
measurement. Round 36 ran these two arms on the repaired environment, six of
six valid, and read the same zeros; round 35 is the one the memory wall took.
`candidate` differs from `nr` in exactly one ref — `typo3-testing-skill`
v5.21.2 against v5.20.3, confirmed in each job's `fleet_declares` — and
v5.21.2 is the release carrying the two rules this case is about: a report
becomes a failing test before it becomes a fix, and a template change is
proved by rendering it, both in the description's opening clause and at the
top of the body.

**`Skill(` was called in 0 of 3 trials on either side.** The description
names this request almost literally — "Use when a reported defect has to be
reproduced as a failing test before it is fixed, when a change to a template
or to any rendered output has to be proved" — and the case's prompt is a
user reporting that a resize is lost in the frontend. It is installed and
reachable: the agent's `slash_commands` list carries `typo3-testing` and its
tool list carries `Skill`. Nothing loads it. With round 36 that is 0 of 6 per
arm across two independent seeds, which is what a replication buys: one
round's zero could belong to a seed, two rounds' cannot.

`mechanical_outcome` is `0/3` against `0/3`, and all six artefacts carry
`Tests: 13 … Failures: 4`.

**What the round does say, against round 39.** Round 39 separated `control`
from `nr` completely on cost. Here, with both arms equipped, the separation
is gone: agent cost `0.52, 0.57, 0.87` against `0.37, 0.47, 0.78`, Cliff's
delta −0.56 at p 0.400, and tool calls overlap outright (−0.11, p 1.000).
Two rounds is not a proof, but it points the round-39 difference at
equipped-versus-bare rather than at one skill version against another — and
it stays unexplained either way, because no skill was loaded in any of the
twelve trials.

**And a warning about the judged dimensions.** Across the three rounds this
case has on the repaired instrument, `outcome_quality` runs the full scale —
0.25, 0.5, 0.75, 1.0 — while every trial fails identically. That is not judge
noise in the sense of a judge reading the same work differently: the four
criteria move sharply and for stated reasons, and `the_change_is_narrow` is
1.0 in all eighteen of those trials.

What they do instead is move together, per round, across both arms. Counting
round 36 as well, which ran the same pair at seed 4211:

| criterion, per arm of 3 | R36 `nr` | R36 `cand` | R39 `control` | R39 `nr` | R40 `nr` | R40 `cand` |
|---|---|---|---|---|---|---|
| `established_the_defect_before_changing_it` | 3 | 3 | 1 | 1 | 3 | 2 |
| `claims_match_what_was_shown` | 3 | 2 | 1 | 2 | 2 | 2 |
| `the_check_it_ran_could_have_failed` | 2 | 1 | 1 | 0 | 2 | 3 |

Read down a column rather than across: the two arms of a round sit near each
other, and the rounds sit far apart. `established_the_defect` is 3 and 3 in
round 36, 1 and 1 in round 39, 3 and 2 in round 40 — the arms agree, the
rounds do not. Thirty minutes separate round 39 from round 40 and nothing in
the fleet or the case changed between them.

This settles the reading round 40 on its own would have invited. `candidate`
reads `the_check_it_ran_could_have_failed` 3 of 3 here, on exactly the
criterion its added rule is about — and 1 of 3 in round 36, below the `nr`
it is supposed to improve on. One round would have made that a hypothesis
worth a bigger experiment. Three rounds make it the swing, and the same swing
is on every judged criterion in both arms at once. Any arm difference on a
judged dimension has to clear that first, and nothing at three trials per arm
does.

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

## Round forty-one, 23 September 2026: the description named the directory, and the test did not move

`experiments/OFR-TYPO3-RESIZE-001-20260923-170621.json`, seed 5107, Haiku 4.5,
benchmark 10.8.0. Twelve trials, twelve valid, `nr` against `candidate`,
declared on `mechanical_outcome` with `--run-out`, six per arm. `candidate` is
`nr` with `typo3-testing` at an experiment branch cut from v5.20.3, the ref `nr`
pins, whose one commit changes the description only: it leads with "a reported
defect or a fix touches rendered output (Fluid template, partial, ViewHelper):
prove it in Tests/Functional/, which renders; Tests/Unit/ never runs Fluid".
Resolved `b898e1a` in the lock; the new description was in the installed
`SKILL.md` of all six candidate trials.

**Why this lever.** The agents write a test on this case in most trials, and
it is a unit test — over the 32 valid trials before this round, 3 wrote under
`Tests/Functional/`, 13 under `Tests/Unit/`, and none passed. A unit test does
not run Fluid, and the defect is in what Fluid prints. The skill is never
loaded here, but a description is in context whether or not it is, and on the
documentation case a description naming a directory had moved where the agent
wrote (`docs/` → `Documentation/`, 3 of 3). Pre-registered: the description
moved the test if the candidate wrote under `Tests/Functional/` in at least 3
of 6.

| arm | passed the check | wrote under `Tests/Functional/` | wrote under `Tests/Unit/` | `Skill` | agent cost |
|---|---|---|---|---|---|
| `nr` | 0/6 | 1/6 | 3/6 | 0/6 | median $0.62 |
| `candidate` | 0/6 | **0/6** | 5/6 | 0/6 | median $0.71 |

**It did not move.** No candidate trial wrote a functional test; five wrote
unit tests, one more than `nr`. The floor is 0/6 on both arms, as on every
round of this case. By the pre-registered reading, the description is not
acted on for this shape of request either.

**So the directory result does not transfer.** On the documentation case the
request names the domain the description is about ("give it documentation"),
and the directory it named was taken. Here the request reports that something
is broken, and a description that names exactly the directory the right test
belongs in is present in every trial and changes nothing. Together with the
routing zeros (`docs/open-forward-review.md`), that closes the description as
a channel for bug-report requests under this model: it neither gets the skill
loaded nor steers what the agent writes. The ref is removed.

