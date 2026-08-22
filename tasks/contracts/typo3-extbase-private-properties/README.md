# CON-TYPO3-EXTBASE-001 — a check that must fire

A contract eval, not an Open Forward Review: the prompt names the condition,
the target carries a synthetic defect, and the expected result is known. See
[ADR 0002](../../../docs/adr/0002-open-vs-contract-evals.md).

## The condition

Extbase hydrates and dirty-checks entities from `AbstractDomainObject`, the
parent class. A persisted property declared `private` in the subclass is not
reachable from there, so its value never round-trips. The defect class is real
— it is what OFR-TYPO3-RUNTIME-001 found in production code — and here it is
planted deliberately, in a minimal extension, with the answer known.

Four properties across two classes are `private` and must be found. Two more
are `protected` and must not be reported.

## Why this exists beside the open cases

An open review asks whether the system works out what the job is. This asks
whether a specific check fires, and that question deserves to be cheap: no
judge, no instance, mechanical grading, seconds rather than minutes. It can
gate a merge; an open review cannot.

That is also why it does not run against a served TYPO3 instance the way
`tasks/open/` does. A developer's situation is what an open case models. A
contract eval models a check.

## Reviewed by

Nobody yet. `docs/governance.md` requires a case to be admitted by someone who
did not write it; this repository has been written by one person, so the field
is empty rather than filled in by its author. What such a review checks is the
four questions in CONTRIBUTING.md — whether the agent can reach the answers,
whether the prompt is still open, whether the rubric grades behaviour rather
than wording, and whether a failure here would mean anything.

## What capability this task plausibly needs

Recorded so that a skill-invocation count of zero can be read. A zero means one of two
things — the capability was on offer and was not selected, or it was not on offer — and
those are findings about different things (see issue #24).

Naming Extbase properties that must not be `private`. `netresearch/typo3-conformance-skill` is
in `nr` and covers exactly this class of finding.

**Present, and not selected** — zero invocations in three trials on Haiku, on a task both arms
solved perfectly in three to seven tool calls. A capability is not needed here, which is a third
thing a zero can mean and the only case in the benchmark where it applies.
