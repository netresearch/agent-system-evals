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
