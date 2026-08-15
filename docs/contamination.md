# Contamination

A benchmark is only evidence while the system under test has not been told the
answers. Contamination here is quiet: skills are updated continuously from real
work, and a well-meant update can encode a case's expected finding without
anyone intending a benchmark change.

## What is forbidden

Case-specific knowledge in anything the agent can reach:

```
When reviewing netresearch/t3x-sync, check DumpFileTrait.php for
string-concatenated WHERE clauses.
```

This is forbidden wherever it appears — skill body, reference file, checkpoint,
harness rule, AGENTS.md template, canonical source. It converts an open review
into a lookup.

## What is required

The same observation, generalised past its origin:

```
Determine installed dependency versions from the lockfile before reading
the constraints; a constraint states what is allowed, not what is present.
```

This is the entire point of the loop. A case exists to produce learnings like
this one, and a learning that cannot survive the removal of its case's name was
never a learning.

## The test

Would this text help an agent on a repository it has never seen? If yes, it is a
learning. If it only helps on the target, it is contamination.

## Automated guard

`scripts/contamination-check` scans the installed skill fleet and the harness
for:

- case identifiers (`OFR-*`)
- target repository names and owners
- target commit SHAs (full and abbreviated)
- verbatim sentences from any case instruction
- verifier-side known-concern strings

It runs in CI on every pull request and before every recorded evaluation. It
scans the *resolved* fleet — the commits Harbor actually injected, read back
from the job lock — because scanning a manifest proves only what was intended.

## Holdout

The public dataset is developed against and will drift toward being solved. A
holdout dataset of cases whose targets and instructions are not published exists
to detect that drift. When public performance rises and holdout performance does
not, the difference is the overfit.

Holdout results are reported as aggregates only. Publishing a holdout case's
detail retires it.
