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

Known concerns for public cases are still verifier-side (see
[open-forward-review.md](../open-forward-review.md) section 4). Public means the
target and prompt are public, not that the expectations are.
