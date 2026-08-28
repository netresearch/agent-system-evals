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

---

# The composition experiment — 28 August 2026

`docs/composition-sweep.md` picked this case as the one silent case with a
capability to add: `netresearch/github-project-skill`, whose description names
*"CI fails, authoring or consuming reusable workflows, editing a repo's own
`.github/workflows`"*, and which the fleet did not carry. The release case's
identical setup had moved invocation from 0 of 6 to 6 of 6 at p 0.002.

## What the run was

`scripts/run-comparison OFR-PY-CI-001 --arms nr-general,nr-ci --primary skill_invoked --model claude-haiku-4-5-20251001 --seed 251`

`nr-ci` is `nr-general` plus `github-project-skill@v2.17.0` and nothing else.
Six trials, three per arm, six of six valid; the runner stopped after the
discovery round because the declared endpoint did not move. Experiment record:
`experiments/OFR-PY-CI-001-20260828-171752.json`.

## It did not move

| | nr-general | nr-ci |
|---|---|---|
| `skill_invoked` | 0/3 | 0/3 |
| Fisher exact p | — | 1.000 |

Carrying a skill is not sufficient. That is the first negative result for the
composition lever, and it arrived on the case chosen precisely because the
lever looked most likely to work.

## Why, on the evidence of the other three runs

Set the four routing measurements of 28 August side by side and they say one
thing rather than three:

| case | where the request's own words appear in the description | invoked |
|---|---|---|
| release | `Use when creating releases, version bumps, tagging…` — the request says *"prepare the 2.4.2 release"* | 6/6 |
| restraint, round two | `Use when checking which TYPO3 versions an extension declares it supports…` — the request asks which versions it supports | 6/6 |
| restraint, round one | the same words, 35 words in, inside `Also triggers on:` | 1/6 |
| **this case** | `…branch protection or rulesets, CI fails, authoring or consuming reusable workflows…` — ninth item, ~25 words in. And the request never says CI, workflow or Actions: it says *"the star-notifications job went red again last night"* | **0/3** |

Two conditions, and this case fails both. The matching phrase sits mid-list
where round one measured 1 of 6, and the request's own vocabulary — job, red,
log, rate limit, exit — appears nowhere in the description at all. The Go case
fails the second condition the same way: `go-development` names "LDAP/AD
clients" and the request only ever says *library*.

**So the rule the four runs support is narrower than "carry the right skill".**
A skill is reached when its opening clause names the words the request uses. A
skill that covers the work under different words, or names it late, is not
reached — being installed does not change that.

## What is deliberately not being done about it

The obvious next experiment is to branch `github-project` and put this case's
vocabulary in its opening clause. That would almost certainly work, and it
would be the benchmark writing a skill's description to suit the benchmark.
`github-project` serves branch protection, rulesets, merge queues and reviewers;
its opening clause is contested space and a scheduled job's exit status has no
better claim on it than the other eight subjects.

The finding stands as it is: no skill in this organisation's catalogue opens by
naming what this request asks about, and adding one that mentions it in passing
does not help.

## The rest of the report

`exit_semantics` went 3/3 to 1/3, delta −1.00 at p 0.100, and every one of the
six trials scores within one judge step of the threshold — the condition under
which a count of three says nothing at all (docs/instrument-failures.md 24).

The mechanical outcome went 1/3 to 0/3, and that line is unreadable for a
different reason: it is decided by the framework rather than by a judge, so
judge noise does not touch it. Three trials against three, one hit against
none, is Fisher p 1.000 — the sample, not the instrument.

Both are exploratory. Only `skill_invoked` was declared.

## Reproducing

```
scripts/run-comparison OFR-PY-CI-001 --arms nr-general,nr-ci \
    --primary skill_invoked --model claude-haiku-4-5-20251001 --seed 251
scripts/analyze experiments/OFR-PY-CI-001-20260828-171752.json
```
