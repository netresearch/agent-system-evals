# OFR-GO-LDAP-001 — recorded results

## One trial, discarded by construction

Job `OFR-GO-LDAP-001-nr-go-20260826-104500`, 26 August 2026, `claude-haiku-4-5-20251001`. Valid by every
check the validity gate makes, and not a result.

The environment that trial ran in had been built with `git clone` followed by
`git checkout <sha>`, which left every later commit in `.git` — the upstream
fix this case exists to see written, its tests, its commit messages — and a
remote pointing at the forge. Instrument failure 21 in
[docs/instrument-failures.md](../../../docs/instrument-failures.md).

The trial itself did not look: its only git command was `git diff /app/auth.go`.
It scored 0.875 — parity established against the directory, a fix that binds the
raw DN rather than the escaped helper, no test left behind. None of that is
evidence, because the image it ran in offered the answer, and a trial cannot be
credited for declining an offer it did not know it had.

The build script now fetches the one commit at depth 1 without tags and removes
the remote, as the TYPO3 cases' script always did, and proves it at build time.
`tests/test_environment.py` asserts the same of every build script against its
source. The job directory stays on disk under its name so the discard can be
checked; it is excluded from every figure, and the first result this case
records will come from the rebuilt environment.


## First valid trial — `OFR-GO-LDAP-001-nr-go-20260826-115702`

One trial, `claude-haiku-4-5-20251001`, fleet `nr-go`, on the rebuilt environment
(one commit, no remote — proved at build time). Valid; no git history was read
because there was none to read.

| | |
|---|---|
| `timing_parity` | 0.81 |
| mechanical | 5/5 — parity established against the running directory, own suite passes, `auth.go` read and changed |
| judge | `established_before_changing` 3, `mirrored_the_sibling_path` 2, `left_a_guard` **1**, `changed_what_was_asked` 3 |
| tool calls | 15 |
| skills invoked | none — `go-development` was on offer |

The fix works: the regression check that fails on the parent passes on this
tree. What the judge marks down is exactly what the expectations file lists as
the half-fixes: the dummy bind takes the raw DN rather than the escaping
helper the sibling path uses, and no test was left behind at all. `go.sum`
changed alongside `auth.go`, which the scope criterion let pass.

`go-development` present and not selected: a routing result, recorded as one.

This is a smoke run — one trial, no comparison, no claim. A series against
`control` is what would make it one.


---

# First series: control against nr-go

Two arms, three trials each, six of six valid. Measured 26 August 2026 on
**`claude-haiku-4-5-20251001`**, benchmark version 2.0.0.

`scripts/run-comparison OFR-GO-LDAP-001 --arms control,nr-go --primary timing_parity --model claude-haiku-4-5-20251001 --seed 141`

Experiment record: `experiments/OFR-GO-LDAP-001-20260826-142832.json`.

## Everyone fixed it, nobody guarded it

| | control | nr-go |
|---|---|---|
| mechanical — parity established, own suite passes | 3/3 | 3/3 |
| `timing_parity` met | 3/3 | 2/3 |
| criteria | 20 met / 4 partial / 3 not met | 17 met / 6 partial / 4 not met |
| permutation p | — | 0.300 |
| agent cost | 0.19 / 0.24 / 0.32 | 0.16 / 0.17 / 0.45 |
| skills invoked | — | none, in three trials; `go-development` on offer |

Six trials of six closed the timing side channel: the regression check that
fails on the parent commit passes on every tree, and the project's own build,
vet and unit suite pass beside it. The unaided agent does this as reliably as
the equipped one, which puts the Go case beside the contract eval as the second
in this repository where the mechanical floor is not where the arms differ.

Where they differ is above the floor, and it is the same everywhere:

| judge criterion | control | nr-go |
|---|---|---|
| `established_before_changing` | 2 / 3 / — | 2 / 2 / 3 |
| `mirrored_the_sibling_path` | 2 / 2 / — | 1 / 2 / 2 |
| `left_a_guard` | **1 / 1 / 1** | **1 / 1 / 1** |
| `changed_what_was_asked` | 3 / 3 / — | 2 / 3 / 2 |

**No trial in either arm left a test.** Six fixes to a security defect, none
with a guard, on a library whose upstream fix came with one. And no trial used
the escaping helper the sibling path uses for its dummy bind; every one bound
the raw DN. The half-fixes the expectations file names before the case had
ever run are the half-fixes every trial made.

`go.sum` changed in all six diffs: the agent's own `go test` touches it. Not
scope creep, and the judge treated it as such twice.

## Composition, not routing — read the arm's contents first

`go-development` was in the fleet and was invoked in no trial. That is a
routing result: the capability was on offer and not selected, on a request
that names no domain a skill title matches (see issue #24). Whether the skill
would have helped is not something this series can say; what it can say is
that on this task and this model, an agent with a Go skill on offer and an
agent with nothing on offer produce the same fix, the same omissions, and the
same bill.
