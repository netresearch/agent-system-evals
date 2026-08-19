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

## Built, 2026-08-19

`tasks/contracts/` stood empty for four days while the decision was cited in
three other documents. The first case is CON-TYPO3-EXTBASE-001: four Extbase
properties declared `private` in a minimal synthetic extension, two `protected`
ones beside them, and grading that is mechanical in both directions — the four
must be named, the two must not be called broken.

Cheap the way the decision requires: no judge, no instance, no network. The
verifier image carries no agent CLI at all.

The negative half earned its place immediately. Without it, an answer listing
every property in both files scores full marks, having found nothing. Getting
it right took a second attempt: the first version failed a *correct* answer,
because `Category::$name is private` contains the word `category` and the
predicate could not tell the class from the property of the same name.
