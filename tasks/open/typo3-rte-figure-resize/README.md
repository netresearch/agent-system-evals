# OFR-TYPO3-RESIZE-001 — a reported rendering defect

The first case in this benchmark taken from the world rather than written for
it. The request is a user's bug report, quoted; the expected behaviour is the
one the maintainers' own fix established; and neither was chosen with a
benchmark in mind.

| | |
|---|---|
| request | [issue #863](https://github.com/netresearch/t3x-rte_ckeditor_image/issues/863), reported by an external user |
| environment | `netresearch/t3x-rte_ckeditor_image` at `31ea0898`, the commit before the fix |
| ground truth | the functional test from [PR #865](https://github.com/netresearch/t3x-rte_ckeditor_image/pull/865) |
| endpoint | mechanical: 13 of 13 assertions, no judge |

## Why this candidate and not the four others

Five issues with external reporters and a fix that shipped a test were found
across the TYPO3 extension repositories. Four were rejected, and the reason is
the same in each: **the fix's test asserts the fix's implementation.** The
nearest miss reflects into `calculateDisplayDimensions`, a private method the
fix introduces — an agent that repairs the same defect elsewhere in the same
file fails a test that expects a method it had no reason to write.

This one drives `ImageRenderingAdapter::renderFigure()`, a public method that
already exists at the pinned commit, with stored HTML in and rendered HTML out.
Nothing in the assertions names the fix's internals. A correct fix reached
another way passes.

## The ground truth was verified before the case was built

Same file, same command, same environment:

| commit | result |
|---|---|
| `31ea0898` — pinned here | 13 tests, **4 failures** |
| `4796899` — the real fix | 13 tests, **0 failures** |

The four failures are the report: the author's width (`width:26.43%`,
`width:320px`, `width:33%`) is absent from the rendered output. The nine that
pass at the pinned commit are pre-existing behaviour that a fix must not break,
which is why the check requires all thirteen.

## What this case carries that the others do not

Nobody here chose the answer. The other open cases were written by the people
measuring, several with the finding in mind; this one's expected behaviour was
settled by maintainers fixing a user's complaint, months before the benchmark
looked at it.

## And what it carries that is a problem

**This extension is the skill fleet's worked example.** Its name appears in 47
files across the installed skills — against 0 to 17 for every other target this
benchmark uses, and it is the highest by a factor of three.

Twenty-one contamination hits follow from that, all recorded in
`tests/contamination-decisions.yaml`. Six reference files account for all of
them and each uses the extension to show a tooling shape: an XLIFF header, a
runTests configuration, a docs URL, an RST directive, a JavaScript test layout.
None touches rendering, figures, resizing or the defect.

That judgement is about content. The exposure is a separate fact and survives
it: an equipped arm reads documentation that names this repository far more
often than it names any other target. **A win for the equipped arm here cannot
be read as skill quality without weighing that**, and the next case mined from
the world should be chosen for low exposure as well as for a clean endpoint.

## No running instance

Unlike the other open cases this one provisions no web server and no database
service. The reported behaviour is a pure rendering path — stored HTML in,
rendered HTML out — reachable through the extension's own functional stack on
SQLite, which is also where the check runs.

What that costs is stated rather than hidden: an agent that would have looked
at the rendered page cannot, and a tool that reads a running application has
nothing to read. If transcripts show arms failing for want of an instance
rather than for want of the fix, this is the first decision to revisit.

## First result — 29 August 2026

`scripts/run-comparison OFR-TYPO3-RESIZE-001 --arms control,nr --primary mechanical_outcome --model claude-haiku-4-5-20251001 --seed 307`

Six trials, three per arm, six of six valid. The runner stopped after the
discovery round because the declared endpoint did not move. Experiment record:
`experiments/OFR-TYPO3-RESIZE-001-20260829-093358.json`.

| | control | nr |
|---|---|---|
| mechanical outcome (13 of 13 assertions) | 0/3 | 0/3 |
| `skill_invoked` | 0/3 | 0/3 |
| agent cost, median | $0.72 | $0.45 |
| input tokens, median | 3.83M | 2.89M |
| tool calls, median | 75 | 53 |

**Nobody fixed it.** A real defect, reported by a real user, in a real
extension: zero of six trials produced a tree where the maintainers' own test
passes. That is the first case here where both arms fail a ground truth nobody
in this project chose.

**And the equipped arm loaded no skill**, so this case joins the silent
majority: it measured the base model twice. Read against
`docs/composition-sweep.md`, that is what the fleet's descriptions predict —
the request says a CKEditor resize is lost in frontend rendering, and no skill
opens by naming that work.

## What is worth more than the zero

Five of the six trials, and **three of three in the equipped arm**, closed by
declaring the fix successful:

> *"Perfect! The fix is working correctly."*
> *"I've successfully fixed the issue where CKEditor 5's image resize
> information was being lost during frontend rendering."*
> *"Perfect! I've successfully fixed the CKEditor 5 image resize issue."*

The mechanical check says otherwise, in every one of them. And these were not
agents that skipped verification: the transcripts mention `phpunit` between 4
and 73 times. They ran something, read it as confirmation, and were wrong.

That is a failure mode the judge did not catch. The `claims_match_what_was_shown`
criterion asks whether a claim of success appears where nothing was run after
the edit — which is not this. Here something *was* run. The rubric has no
criterion for **running the wrong check and believing it**, and it scored 7 of 9
and 8 of 9 criteria met across the two arms.

This case is also the most expensive in the benchmark: $0.42 to $0.93 a trial,
2.5 to 6.3 million input tokens, 42 to 77 tool calls. A real bug in a real
codebase costs an order of magnitude more than the cases written for this
benchmark, and still comes out wrong.

## A defect in this case's own instrument

The diff collector was changed before this run to diff against the pinned
commit rather than `HEAD`, because agents commit
(docs/instrument-failures.md 27). It is still half blind: `git diff <base> HEAD`
shows committed work only, and an agent that leaves its changes unstaged — as
one `nr` trial did, with six modified files — produces an empty patch again.
The artefact for that trial carries the appended `git status --porcelain` file
list and no patch at all.

The right expression is `git diff <base>` without `HEAD`, which compares the
base to the *working tree* and covers both. It was not changed mid-series: a
task edit changes the digest, and half the trials would then have been measured
with a different instrument. The declared endpoint is unaffected — only the
judge's diff input was degraded.
