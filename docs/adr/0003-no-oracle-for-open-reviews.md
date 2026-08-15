# ADR 0003 — No oracle solution for open cases

- Status: accepted
- Date: 2026-08-15

## Context

Harbor tasks may ship a `solution/`, and benchmark pipelines conventionally
validate a task by proving the oracle passes and a no-op fails.

"Review this extension and tell me what needs attention" has no single correct
answer. Writing an oracle would mean writing the findings list the review is
supposed to discover, and the case would then measure agreement with that list.

## Decision

Open cases ship no `solution/`. Harbor supports this (`--no-solution`).

Oracle validation is replaced by four checks:

1. **Environment readiness** — the commands a competent developer would reach
   for actually work in the image (composer install, test runner, static
   analyser).
2. **Verifier self-test** — the verifier distinguishes fixture-good from
   fixture-bad artifacts.
3. **Judge calibration** — each qualitative criterion scores its passing,
   partial and failing fixtures correctly.
4. **Human baseline** — an experienced reviewer works the case once; the record
   stays verifier-side.

## Consequences

Case validity rests on calibration fixtures, which must be maintained as
carefully as the rubric. A rubric change that breaks calibration is a rubric
regression and CI treats it as one.

The no-op check is kept and strengthened: an agent that inspects nothing and
answers "everything looks fine" must score near zero across all dimensions. If
it does not, the rubric is broken, and this is the cheapest way to find out.
