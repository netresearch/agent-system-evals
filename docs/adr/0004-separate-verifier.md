# ADR 0004 — Verifiers run in a separate environment

- Status: accepted
- Date: 2026-08-15

## Context

Harbor can run a verifier inside the agent's environment (`shared`) or in a
fresh one seeded from collected artifacts (`separate`).

Open reviews grade the workspace itself: git diff, command output, test results,
generated files. An agent with write access to the environment its grading reads
is an agent that can influence its grade, whether or not it means to.

The second reason is operational and was the deciding one. Harbor's regrade
path refuses anything else:

> Only single-step tasks whose verifier resolves to `environment_mode='separate'`
> can be regraded.

A case graded in place is frozen against the rubric it first ran under. Every
later rubric improvement would cost a full re-run of every trial.

## Decision

`[verifier] environment_mode = "separate"` is mandatory for all cases in this
repository, and cases stay single-step.

## Consequences

Everything a future rubric might need must be collected at run time; a regrade
sees only the artifacts. `artifacts` and `[verifier] collect` are therefore part
of case review, not an afterthought.

Judge credentials live in `[verifier.env]`, resolved host-side, and never enter
the agent environment or any image.
