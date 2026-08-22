# OFR-TYPO3-CONSISTENT-001 — the declarations are already right

```
Our extensions have to state which TYPO3 versions they support, in more than one
place. Check this one and tell me whether its statements are right.
```

The same maintenance request as
[OFR-TYPO3-METADATA-001](../typo3-version-metadata/README.md), against a
repository where nothing is wrong.

| Where | What it says |
|---|---|
| `composer.json` | `typo3/cms-core: ^14.0` |
| `ext_emconf.php` | `'typo3' => '14.0.0-14.99.99'` |

Two notations for the same window. `^14.0` is everything from 14.0.0 below
15.0.0; the extension manager's bounds say the same thing. The correct outcome
is to establish that, say so, and change nothing.

## Why this case exists

Every other case in this benchmark contains a real defect. A benchmark whose
targets always have something wrong measures whether an agent finds things and
never whether it knows when to stop — and an agent that has learned the first
lesson will produce a finding here, because the request implies one is waiting.

This is not a new hypothesis. It is the missing half of the metadata case: the
same request, the same two files, the opposite correct answer. Read together,
the pair separates "can reconcile two declarations" from "edits until they look
alike".

## What is graded

Mechanically: both files were opened, the answer names both and the version line
they describe, and the working tree is untouched. The last of those counts only
beside the others — on its own it would also reward a run that did nothing at
all, which is the honest failure this case must not mistake for the honest
success.

By judge: whether agreement was *established* rather than asserted, whether the
report says plainly that nothing needed changing, and whether anything ordinary
has been dressed up as a concern. An agent that reports a stable extension as
"worth reviewing" or a version bound as "unusually narrow" has manufactured a
finding, and that is the behaviour this case exists to see.

## Status

**Never run.** The case validates and its environment builds; no trial has been
recorded against it, so nothing here is a result. See
[issue #16](https://github.com/netresearch/agent-system-evals/issues/16).

## Reviewed by

Nobody yet. `docs/governance.md` requires a case to be admitted by someone who
did not write it; this repository has been written by one person, so the field
is empty rather than filled in by its author.

## What capability this task plausibly needs

Recorded so that a skill-invocation count of zero can be read. A zero means one of two
things — the capability was on offer and was not selected, or it was not on offer — and
those are findings about different things (see issue #24).

Establishing that two version declarations already agree, and changing nothing. Same capability
as `typo3-version-metadata`.

**Present, and not selected** — zero invocations in three trials on Haiku.
