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

## Results

Four fleets, three trials each: see [RESULTS.md](RESULTS.md).

## What that says about the case

**The unaided baseline is strong.** The control agent's report led with an
unauthenticated cache-clearing middleware registered in the frontend stack,
anchored to file and line, with the consequence stated (any anonymous visitor
can flush page caches). It found credentials interpolated unescaped into shell
commands, and dumps written to a publicly served directory. None of those are
in this case's recorded expectations, which is exactly why that file says it is
not an answer key.

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
./scripts/run-evaluation OFR-TYPO3-EXT-001 --fleet nr
./scripts/run-evaluation OFR-TYPO3-EXT-001 --fleet companion
./scripts/run-evaluation OFR-TYPO3-EXT-001 --fleet nr-companion
./scripts/compare jobs/<control-job> jobs/<nr-job>
```

Rubric changes should be applied to recorded trials with `harbor job regrade`
rather than by re-running agents. Three regrades were needed to get the judge
configuration right for this case, and none of them cost an agent run.

## Reviewed by

Nobody yet. `docs/governance.md` requires a case to be admitted by someone who
did not write it; this repository has been written by one person, so the field
is empty rather than filled in by its author. What such a review checks is the
four questions in CONTRIBUTING.md — whether the agent can reach the answers,
whether the prompt is still open, whether the rubric grades behaviour rather
than wording, and whether a failure here would mean anything.
