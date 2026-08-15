# ADR 0006 — Repository-level cases first; runtime fidelity deferred to a spike

- Status: accepted
- Date: 2026-08-15

## Context

Part of the Netresearch TYPO3 workflow runs against a live instance under DDEV.
Evaluating that behaviour needs a running installation: database, web server,
TYPO3 boot, backend.

DDEV is itself a Docker orchestrator. Running it inside a Harbor sandbox means
nested containerisation, with consequences for reproducibility, CI, isolation
and runtime that are not knowable in advance.

There is a sharper risk than any of those: an approximation of the real runtime
measures the approximation. A case that reports a runtime behaviour the actual
workflow does not have is worse than no case, because it is believed.

## Decision

Version 1 covers repository-level cases only — source, dependencies, tests,
static analysis, documentation, CI configuration. These run in ordinary Harbor
Docker environments with no fidelity question.

Runtime cases are blocked on a spike that must answer, with measurements rather
than expectations:

- **Option A** — Harbor Compose provides web and database directly. Clean
  isolation, but the agent is not using DDEV, so the case tests TYPO3 runtime
  and not the workflow.
- **Option B** — nested Docker with DDEV inside the sandbox. Accepted only on
  demonstrated reproducibility, no host Docker leak, CI viability and tolerable
  runtime.
- **Option C** — a Netresearch environment provider on Harbor's
  `BaseEnvironment` interface, backing onto an ephemeral VM. Highest fidelity,
  highest cost.

The spike's own precondition: show that a runtime case would materially change
what we learn. If repository-level cases already discriminate between fleets,
the fidelity work buys resolution we are not using.

## Consequences

Version 1 cannot make claims about runtime behaviour, and must not imply
otherwise. Case categories carry `metadata.target_type` so a repository-level
result is never read as a runtime one.

DDEV does not block the project. That is the point of deferring it.
