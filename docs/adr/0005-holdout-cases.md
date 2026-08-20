# ADR 0005 — Public and holdout datasets

- Status: accepted
- Date: 2026-08-15

## Context

Skills are updated from real work, continuously, by people who also see the
benchmark. Over time the public cases drift toward being solved, and nothing in
the process announces when that stops being improvement and starts being
memorisation.

## Decision

Maintain two dataset classes.

**Public** (`datasets/open-forward-reviews/`) — cases, targets, prompts,
rubrics and results all visible. Used for development, transparency and
demonstration.

**Holdout** (`datasets/holdout/`) — targets and instructions not published.
Reported as aggregates only, never per finding.

The overfit signal is divergence: public rising while holdout is flat.

## Consequences

Holdout cases must be built from the same lifecycle, or the comparison measures
case difficulty rather than generalisation.

Publishing a holdout case's detail retires it. There is no way to un-publish,
so the holdout set needs replenishment planned as ordinary work, not as a
response to having burned one.

Known concerns for public cases are verifier-side (see
[open-forward-review.md](../open-forward-review.md) section 4): the agent's
container never holds them.

## Correction, 20 August 2026

The sentence that stood here — "public means the target and prompt are public,
not that the expectations are" — was false for this repository as published.
Every `tasks/*/tests/known-concerns.md` was committed and readable by anyone,
naming the findings a case expects and the mechanisms behind them. What the
files have is *verifier isolation*, which keeps them out of the agent's
container during a run. That is not secrecy, and describing it as secrecy
mattered in three directions: a skill author can read the expected findings, a
future model can absorb them from a public repository, and the lexical
contamination check cannot detect either.

The decision above stands. The claim about the public dataset did not.

**Resolved the same day.** Expectations now live encrypted in
`expectations/<case-id>.md.enc`, the plaintext is ignored by git, and
`scripts/validate-tasks` fails if one reappears inside a task directory. Moving
them cost nothing in grading: they were listed in each judge's `files`, and
RewardKit's agent path ignores `files` entirely, so no judge had ever read one.
They were public and unused.

What that does not repair: git history holds every plaintext version, and this
repository is public. The five cases that existed before 20 August 2026 are
burned — their expectations were readable for as long as they existed, and no
rewrite can un-publish what was already fetchable. Their scores stay useful for
development and are not evidence about any system that could have read them.
The mechanism protects the cases written from here on, and the holdout set
above remains the answer for cases that must stay unseen.
