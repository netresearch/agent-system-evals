# Background on the target — verifier-side only

<!-- contamination-markers: t3x-contexts, netresearch/contexts, RemovePointerFieldFunctionalityOfTCAFlex, 107047, 108345 -->

**This file must never reach the agent environment.** It is copied into the
verifier container with `tests/`, which the agent cannot read. Checked by
`scripts/contamination-check`.

**This is not an answer key.** It is partial background so the judge can tell a
change the agent established the need for from one it pattern-matched. A
defensible change absent from this list is still defensible; a change that
appears here earns nothing unless the agent worked out that it was needed.

## How this background was obtained

The target is pinned at the parent of a real change in the same repository that
moved the supported-version window forward. That change is not reachable from
the agent environment: the working copy is a single-commit fetch with the
remote removed, and the network allowlist excludes the forge.

## State at the reviewed commit

The extension declares `^12.4 || ^13.4` on five TYPO3 packages and `php ^8.2`.
It ships a full toolchain — PHPStan, PHP-CS-Fixer, Rector, Fractor, PHPUnit
with unit and functional suites, PHPat, Infection — an `AGENTS.md`, a CI
workflow with a version matrix, and 719 passing unit tests on the older line.

## What the real change involved

Recorded so the judge can recognise established work, **not** as a checklist:

- The window moved to `^13.4 || ^14.3`: the oldest line dropped, the newest
  added, the middle one kept working. The result had to run on both.
- Two TYPO3 packages were **removed** from the requirements rather than moved,
  because no class of either is referenced and on the newer line they are
  pulled into the package graph and force both system extensions to load. An
  agent that mechanically slides every constraint will not find this.
- Package metadata the newer line expects was declared in the manifest.
- A breaking change in the framework's TCA handling had to be accounted for in
  the extension's own code.
- The CI matrix gained a leg for the new line, with per-leg package pinning.

## What the environment already tells the verifier

The collect hooks record, per line: whether the tree resolves, whether the
project's own unit suite passes, and which framework version was installed.
Three states are distinguishable and were confirmed before the case was
admitted:

| Tree | old line | new line |
|---|---|---|
| unchanged | resolves, tests pass | does not resolve |
| constraints slid, no code work | resolves, tests pass | resolves, **tests fail** |
| migration done | resolves, tests pass | resolves, tests pass |

## Known blind spots

- Nothing here evaluates functional tests; they need a database and this case
  is repository-level only (ADR 0006).
- Nothing here says the older line *must* be kept. Which window is right is the
  project's own convention, and judging that choice is the point.
- The list above is what one real change contained. It is certainly not the
  only defensible way to do the work.
