# Scoring

## Why not one number

Harbor needs an aggregate reward, and RewardKit will produce one. That number is
a technical summary and is not the result. The result is the vector, because the
failure modes it separates are the ones worth acting on:

- an agent that investigates impeccably and reports nothing useful
- an agent that names a real problem it never actually verified
- an agent that finds thirty trivia items and misses the compatibility break

A single score maps all three onto the same middle band and tells you to look
into it. The vector tells you which one happened.

## Where a dimension is defined

In [`dimensions.toml`](../dimensions.toml), and nowhere else. The list used to
live in four places — the validator, the comparator, the dataset metric and this
document — and they drifted in the direction that hides errors: the metric kept
aggregating `skill_routing` for weeks after the rename, and `consistency` graded
two cases while neither the comparator nor the metric had heard of it. Adding a
dimension anywhere but the registry is how that happens again;
`scripts/validate-rubric` fails when a consumer's copy diverges.

## The eight dimensions

Each is a directory under a case's `tests/`, which is how RewardKit derives
separate rewards. Within a dimension, mechanical checks (`*.py`) and judge
criteria (`*.toml`) coexist and their scores average into that dimension's
reward.

| Dimension | Asks |
|---|---|
| `context_discovery` | Did it establish what this project *is* before judging it? |
| `capability_selection` | Did it choose sensibly among the capabilities it was offered — including choosing none? |
| `authority` | Did each claim come from the source that owns that fact? |
| `evidence` | Is each finding anchored to a location, a version, and an observation? |
| `verification` | Did it run the checks that were available to it? |
| `prioritization` | Is the ordering one an experienced engineer would accept? |
| `unsupported_claims` | Penalises assertions no observation backs |
| `outcome_quality` | Would a competent developer actually use this output? |

`outcome_quality` exists to close an obvious gaming route. Without it, a run
that performs the process perfectly and produces nothing of value scores well on
seven dimensions.

## Case dimensions beside the eight

The eight exist for an open review. A low-level maintenance task does not have
eight things worth judging, and forcing them prices a cheap case out of being
one — so a case may declare a narrower set in `metadata.dimensions`, and the
registry marks such a dimension `applies_to = "case"`.

| Dimension | Asks | Used by |
|---|---|---|
| `consistency` | Do the statements that have to agree agree, and against something established rather than assumed? | the version-metadata pair |
| `contract` | Mechanical: is the known answer present and are the known non-answers absent? | contract evals (ADR 0002) |

Declared rather than inferred from the directory listing, because two cases
graded on different subsets can otherwise be compared by mistake.

## Mechanical first, judge second

Every dimension is grounded mechanically as far as the evidence allows, and only
the residual judgement goes to an LLM. This is not purity, it is variance
control: mechanical checks are deterministic and regradeable, judges are neither.

The pattern per dimension:

```
mechanical                              judge
✓ composer.lock was read                Was the reading sufficient and
✓ ext_emconf.php was read               relevant for this request?
✗ Documentation/ never opened
```

A judge that is handed the mechanical findings alongside the trajectory
disagrees with itself far less than one asked to determine both facts and
adequacy from raw logs.

## Scores

Each criterion resolves to `MET` (1.0), `PARTIAL` (0.5) or `NOT_MET` (0.0).
`PARTIAL` is meaningful and must be reachable — most of the interesting
behaviour in an open review is partial. A rubric whose criteria are effectively
binary is measuring something narrower than it claims.

Worked example, `verification`:

| Observed | Score |
|---|---|
| Tests present, run, results reported | MET |
| Tests present, mentioned, not run | PARTIAL |
| PHPStan finding claimed, PHPStan available, never run | NOT_MET |
| Documentation rule asserted from memory, canonical source never consulted | NOT_MET |
| Tests present but genuinely unrunnable, agent says so and says why | MET |

The last row matters. Correctly establishing that a check cannot run is
verification, and a rubric that scores it as failure teaches agents to fake it.

## Reporting

Per case, per variant:

```
OFR-TYPO3-EXT-001            main fleet

reliability            3/3

context_discovery      3/3
capability_selection   2/3
authority              3/3
evidence               3/3
verification           2/3
prioritization         3/3
unsupported_claims     3/3
outcome_quality        2/3
```

Counts, not means. Where a dimension splits (2/3), the disagreement is the
finding — a system that routes correctly two times in three has a routing
problem that an average of 0.83 would have made look like a rounding detail.

## Aggregation

`datasets/*/metric.py` aggregates across a dataset and emits per-dimension means
alongside cost signals (median tool calls, duration, tokens). The means are for
trend lines on the dashboard. They are not the unit of decision; the per-case
counts are.

## capability_selection, and why it is not `skill_routing`

The dimension used to be called `skill_routing`, and its mechanical half asked
whether a skill had been invoked at all. That makes not using one automatically
worse — and the runtime case refuted the premise. Every arm solved it; in eight
of nine trials without an MCP the agent booted the framework itself and queried
the database directly; no skill was invoked anywhere. A benchmark that scores
invocation teaches the agent to invoke, which is Goodharting its own metric.

So the question became: did the agent choose sensibly among what it was
offered, including the legitimate choice of taking nothing? Whether anything
was reached is recorded at weight zero — telemetry, in the capability ledger —
and the judgement is the judge's.

**An arm offered nothing scores N/A, not zero.** There was no decision to get
right, and a control arm that scores badly on a dimension it cannot act on
inflates every comparison against it.
