# OFR-PY-CI-001 — recorded results

## One trial, discarded by construction

Job `OFR-PY-CI-001-nr-general-20260826-105257`, 26 August 2026, `claude-haiku-4-5-20251001`. Valid by every
check the validity gate makes, and not a result.

The environment that trial ran in had been built with `git clone` followed by
`git checkout <sha>`, which left every later commit in `.git` — the upstream
fix this case exists to see written, its tests, its commit messages — and a
remote pointing at the forge. Instrument failure 21 in
[docs/instrument-failures.md](../../../docs/instrument-failures.md).

The trial looked. Its third tool call was `git log --oneline --all
--grep="star-notifications"`; it then read both upstream fixes with `git show
<sha>:scripts/check-stars.py` and reproduced their identifiers and test names
verbatim. It scored 0.94 across five mechanical criteria and four judge
criteria, and the judge saw a competent investigation. The number measures
whether an agent thinks to read the log.

The build script now fetches the one commit at depth 1 without tags and removes
the remote, as the TYPO3 cases' script always did, and proves it at build time.
`tests/test_environment.py` asserts the same of every build script against its
source. The job directory stays on disk under its name so the discard can be
checked; it is excluded from every figure, and the first result this case
records will come from the rebuilt environment.


## First valid trial — `OFR-PY-CI-001-nr-general-20260826-120212`

One trial, `claude-haiku-4-5-20251001`, fleet `nr-general`, on the rebuilt
environment. Valid; no git history was read because there was none to read.

| | |
|---|---|
| `exit_semantics` | 0.68 |
| mechanical | 3/5 — **`exit semantics: not established`**, **own checks failed** |
| judge | `established_that_the_exit_was_designed` 3, `kept_the_red_that_matters` **3**, `starvation_stays_visible` 1, `changed_what_was_asked` 3 |
| tool calls | 13 |
| skills invoked | none — nothing applicable was on offer |

The case discriminated the way it was built to. The agent introduced a
`BudgetExceededError`, raised it at the budget give-up, and exited 0 with a
`::notice::` — for **every** budget give-up. The secondary-limit case, abuse
detection with no promised reset, now ends green too (check B), and one of the
repository's own tests fails because it expects a `RateLimitError` there. That
is the "made it green" shape the expectations file describes, and the
mechanical check caught it.

The judge did not. `kept_the_red_that_matters` scored 3 on a diff whose
secondary path exits 0. The mechanical check and the judge disagree, and the
check is right — which is the reason writing cases have one (ADR 0007).

One instrument correction came out of this trial. Check A originally required
the literal `::warning::`; the agent printed `::notice::`, which is an
annotation that keeps the hand-over visible just as well, and the check refused
it for the word rather than the behaviour. A now accepts either level. Against
this trial's diff the widened check reads A ok, B not, C ok — the overall
verdict is unchanged, and it is the right one.

Smoke run: one trial, no comparison, no claim.


---

# First series: control against nr-general

Two arms, three trials each, six of six valid. Measured 26 August 2026 on
**`claude-haiku-4-5-20251001`**, benchmark version 2.0.0.

`scripts/run-comparison OFR-PY-CI-001 --arms control,nr-general --primary exit_semantics --model claude-haiku-4-5-20251001 --seed 151`

Experiment record: `experiments/OFR-PY-CI-001-20260826-151248.json`.

## Nobody got all three answers right

| | control | nr-general |
|---|---|---|
| mechanical — hand-over green, secondary red, bad token red | 0/3 | 0/3 |
| `exit_semantics` met | 0/3 | 1/3 |
| criteria | 15 met / 4 partial / 8 not met | 16 met / 3 partial / 8 not met |
| permutation p | — | 1.000 |
| agent cost | 0.05 / 0.07 / 0.11 | 0.05 / 0.05 / 0.11 |
| skills invoked | — | none; nothing applicable on offer |

The trials fall into two shapes, and each arm has both:

| shape | control | nr-general | what the check saw |
|---|---|---|---|
| made every give-up green | 2 | 2 | A ok, **B not**, C ok |
| changed nothing | 1 | 1 | **A not**, B ok, C ok — 3 and 4 tool calls |

Four of six did what the expectations file predicted before the case had run:
caught the exception and exited 0, for the designed hand-over *and* for the
secondary limit that has no promised reset. Two of six read the script,
concluded red was fine, and touched nothing — on a request that says "sort it
out" and a log that says every later run succeeded. Nobody drew the line where
the script's own comments draw it.

## The judge could not see what it was asked to grade

`kept_the_red_that_matters` scored 3 on `nr-general-151737`, whose secondary
path exits 0. That is the second time on this case, and the reason is now
known and is not the judge's: an agent judge reads the transcript, the
transcript renders tool calls and observations, and the collected diff is an
artifact that reaches the judge only if the agent printed it. The criterion
says "read the diff"; there was no diff to read. Instrument failure 23 in
[docs/instrument-failures.md](../../../docs/instrument-failures.md). The
mechanical check, which does read the tree, is what this case's number rests
on — and it caught all four.

## Composition by construction

No fleet in this repository carries a Python skill, because the organisation
publishes none; `nr-general` is the three skills of `nr` that are not TYPO3 or
PHP. A zero invocation count here is a composition result and was declared as
one before the run (issue #24). The arms produced the same two shapes at the
same cost, which is what identical capability on offer predicts.
