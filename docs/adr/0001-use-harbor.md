# ADR 0001 — Build on Harbor rather than a bespoke eval framework

- Status: accepted
- Date: 2026-08-15

## Context

Evaluating whether the Netresearch agent stack improves agent behaviour needs
agent execution, environment isolation, skill injection with recorded
provenance, trajectory capture, artifact collection, verification, aggregation
and a result viewer. Building that is months of work that is not the thing we
know something about.

## Decision

Use [Harbor](https://harborframework.com) as the execution engine. This
repository contributes only the Netresearch-specific layer: methodology, cases,
rubric, fleets, and the conventions that make results comparable.

## Verification

Checked against Harbor 0.21.0, installed and inspected rather than read about:

| Requirement | Status |
|---|---|
| Skill injection from git sources | `harbor run --skill` accepts path or git source, repeatable |
| Resolved skill commits recorded | job lock records resolved commit per skill |
| Separate verifier environment | `[verifier] environment_mode = "separate"` |
| Regrade recorded runs | `harbor job regrade`, restricted to single-step separate-verifier tasks |
| Multi-dimensional reward | RewardKit derives one reward per `tests/` subdirectory |
| Custom dataset aggregation | `harbor init --dataset --with-metric` |
| Optional solution | `harbor init --task --no-solution` |
| Trajectory format | ATIF, messages / actions / observations |

## Consequences

We inherit Harbor's release cadence and its constraints. The regrade
restriction in particular propagates into our specification: `separate` becomes
a MUST, not a preference (see [ADR 0004](0004-separate-verifier.md)).

We do not build: an agent runner, agent adapters, a container orchestrator, a
trajectory format, a trial viewer, a judge framework, an artifact collector, or
a job persistence format.

## Note on the benchmark template

`harbor-framework/benchmark-template` carries an explicit warning that it is not
actively maintained, and points to `terminal-bench` instead. We therefore
scaffold with `harbor init` and take CI patterns from the template as reference
rather than adopting it as a base. See
[ADR 0003](0003-no-oracle-for-open-reviews.md) for why the template's oracle
pipeline would not have fitted regardless.
