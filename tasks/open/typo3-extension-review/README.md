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

## First A/B

Three trials per fleet, no errored trials. Case, agent (claude-code on
claude-opus-5), model, judge, rubric, environment and trial count identical;
only the fleet differs.

| Dimension | control | main | control mean | main mean | delta |
|---|---|---|---|---|---|
| context_discovery | 3/3 | 3/3 | 1.00 | 0.94 | −0.06 |
| skill_routing | 0/3 | 3/3 | 0.31 | 1.00 | **+0.69** |
| authority | 0/3 | 0/3 | 0.47 | 0.33 | −0.14 |
| evidence | 3/3 | 3/3 | 0.88 | 0.75 | −0.12 |
| verification | 3/3 | 2/3 | 0.85 | 0.81 | −0.04 |
| prioritization | 2/3 | 3/3 | 0.61 | 0.94 | **+0.33** |
| unsupported_claims | 1/3 | 0/3 | 0.50 | 0.44 | −0.06 |
| outcome_quality | 3/3 | 3/3 | 1.00 | 1.00 | 0.00 |

### What this shows

**Two dimensions move: routing and prioritization.** Routing is the larger
number and the weaker evidence — `control` has no injected skills, so part of
that gap is definitional rather than earned. It is not entirely definitional:
the judge counted Claude Code's own entry points as available and scored their
non-use as a routing failure. Prioritization is the more interesting move,
0.61 to 0.94, and nothing about it is definitional.

**Nothing else moves.** Five dimensions sit within noise at this sample size,
and `outcome_quality` is 1.00 on both sides — on this case both
configurations produce a review a developer could act on. The stack changes
the shape of the process; it does not, here, change whether the result is
usable.

**Authority fails on both sides.** 0/3 either way, and the mechanical evidence
is identical in all six trials: no external canonical source consulted, the
resolved dependency state never read. Every framework-currency claim in every
trial rests on recollection. That is the clearest actionable finding the case
has produced, and the stack does not currently address it.

### What this does not show

One case, one agent, one model, three trials per side. This is not a verdict
on the Netresearch stack; it is one measurement of it, on a repository-level
TYPO3 review. The negative deltas are small and within noise — reading them as
harm would be exactly the overreach the counting convention exists to prevent.

`scripts/export-retro` turns the repeated shortfalls into retro input. Most of
them scored 2 (partial), not 1, and should be read that way.

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
