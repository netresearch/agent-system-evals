# ADR 0002 — Separate Open Forward Reviews from contract evals

- Status: accepted
- Date: 2026-08-15

## Context

Two questions look similar and are not:

1. Given a realistic, underspecified request, does the system work out what the
   job is?
2. Given a known failure mode, does the relevant check fire?

Both are worth asking. Answered in one case, neither is answered well: the known
failure mode becomes an expected-findings list, and the open prompt becomes
decoration over a checklist.

## Decision

Keep them in separate trees with separate rules.

| | `tasks/open/` | `tasks/contracts/` |
|---|---|---|
| Prompt | realistic, underspecified | may name the condition |
| Target | real, unmodified, pinned | may carry synthetic defects |
| Expected result | not fully known | known |
| Grading | eight system dimensions | pass/fail on the condition |

A case may not be moved between trees by editing its prompt. Moving it means
writing a new case.

## Consequences

Contract evals stay cheap and deterministic and can gate merges. Open reviews
are noisier, need repetition, and inform rather than gate — at least until the
variance is characterised.
