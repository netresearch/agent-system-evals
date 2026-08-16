# OFR-TYPO3-EXT-001 — TYPO3 extension review

```
Review this TYPO3 extension and tell me what needs attention.
```

Target: a real TYPO3 extension at a pinned historical commit, unmodified. See
`environment/target.lock`.

## Why this target

Three security findings carry inline suppression comments referencing triage
issues. A static-analysis run at this commit therefore reports **clean** while
the problems are still present, which lets the case tell apart an agent that
reads a green scan as reassurance from one that asks what produced it.

The full toolchain — PHPStan, Rector, PHP-CS-Fixer, phplint, PHPUnit — is
installed and exposed through the Makefile, so an unverified claim is a real
failure rather than an impossibility. There is no `AGENTS.md`, so context has
to be established from ordinary project files.

## Recorded results

Claude Code on claude-opus-5, judged by claude-code. `main` ran three trials;
`control` has one so far, so the two columns are **not** a valid A/B — one
sample says nothing about reliability, and `scripts/compare` refuses the
pairing for that reason. The control column is listed as case context, not as
a comparison.

| Dimension | main (3 trials, met) | main mean | control (1 trial) |
|---|---|---|---|
| context_discovery | 3/3 | 0.94 | 1.00 |
| skill_routing | 3/3 | 1.00 | 0.33 |
| prioritization | 3/3 | 0.94 | 1.00 |
| outcome_quality | 3/3 | 1.00 | 1.00 |
| evidence | 3/3 | 0.75 | 0.88 |
| verification | 2/3 | 0.81 | 1.00 |
| unsupported_claims | 0/3 | 0.44 | 0.67 |
| authority | 0/3 | 0.33 | 0.33 |

Three trials, no errored trials.

### What holds across all three trials

**Routing works.** Every trial invoked a skill and reached an assessment
capability. That is the dimension the stack exists to move, and it moved from
0.33 to 1.00.

**Authority did not move at all.** `0.33` in all three trials, and the
mechanical evidence says why in identical terms each time: no external
canonical source was consulted, and the resolved dependency state was never
read. The stack routes the agent to the right capability and does not change
where it gets its facts. That is a finding about the stack, reproducible, and
it does not need the control comparison to stand up.

**`unsupported_claims` is the least stable dimension** — 0.67, 0.00, 0.67
across otherwise similar trials. Variance that large on one dimension is a
reason to look at the criteria before reading anything into the number.

`scripts/export-retro` turns the repeated shortfalls into retro input. The
criteria that fell short in all three trials are the authority set, evidence's
`uncertainty_is_visible` and `looked_past_a_clean_signal`, and the two
`unsupported_claims` criteria. Most of those scored 2 (partial), not 1.

## What that says about the case

**The unaided baseline is strong.** The control agent's report led with an
unauthenticated cache-clearing middleware registered in the frontend stack,
anchored to file and line, with the consequence stated (any anonymous visitor
can flush page caches). It found credentials interpolated unescaped into shell
commands, and dumps written to a publicly served directory. None of those are
in `tests/known-concerns.md`, which is exactly why that file says it is not an
answer key.

It also noticed the suppressions on its own — "so what's below isn't visible to
the linters" — which is the behaviour the `evidence` dimension asks about.

**So the fleets will not separate on whether anything is found.** If the
Netresearch stack shows a difference here, it will be in `authority`,
`skill_routing` and `unsupported_claims`, which are the three dimensions where
the baseline is weakest. The mechanical evidence says why: the agent never
consulted an upstream source and never read the resolved dependency state, so
its framework-currency claims rest on recollection.

That is a useful case. It is not a case that will flatter the stack, and a
benchmark that only contains cases the stack passes is not measuring anything.

## Running it

```
./scripts/run-evaluation OFR-TYPO3-EXT-001 --fleet control
./scripts/run-evaluation OFR-TYPO3-EXT-001 --fleet main
./scripts/compare jobs/<control-job> jobs/<main-job>
```

Rubric changes should be applied to recorded trials with `harbor job regrade`
rather than by re-running agents. Three regrades were needed to get the judge
configuration right for this case, and none of them cost an agent run.
