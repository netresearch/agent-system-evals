# OFR-TYPO3-UPGRADE-001 — move an extension onto the current LTS

```
We need this extension to work with the current TYPO3 LTS. Can you take care of that?
```

Target: a real TYPO3 extension at the commit immediately before its supported
version window was moved forward. Unmodified. See `environment/target.lock`.

A **writing task**: the result is the tree the agent leaves, not a report. See
[ADR 0007](../../../docs/adr/0007-writing-cases.md) for why the prompt stays
open while the outcome is measured mechanically.

## Why this target

At the pinned commit the extension declares `^12.4 || ^13.4` on five TYPO3
packages. The real change that followed moved that window to
`^13.4 || ^14.3` — dropping the oldest line, adding the newest, keeping the
middle one working.

That shape is the point. A single-version bump can be done by applying the
newest idioms; a window slide cannot, because every change has to remain safe
on the line that stays. And almost none of it is answerable from memory: which
line is current, what the new one removed, which packages it pulls into the
dependency graph. Those live in the framework's changelog and release data, and
the network allowlist deliberately permits exactly those hosts.

This case exists because of a measured result. On
[OFR-TYPO3-EXT-001](../typo3-extension-review/README.md) both fleets failed
source authority identically — 0 of 3 either way, no canonical source
consulted, the resolved dependency state never read, every version claim
resting on recollection. This case puts that weakness where it cannot be
avoided.

Unlike the review case, this target ships an `AGENTS.md`. Context discovery is
deliberately easier here so the two cases do not measure the same thing.

## How the outcome is measured

The result of a writing task is not in the trajectory. Collect hooks run after
the agent stops, pin a copy of the tree it left to each version line, install
it and run the project's own unit suite. `outcome_quality` reads those verdicts
mechanically; the judge weighs the choices around them.

Three states are distinguishable, confirmed before the case was admitted:

| Tree | old line | new line |
|---|---|---|
| unchanged | resolves, 719 tests pass | does not resolve |
| constraints slid, no code work | resolves, tests pass | resolves, **tests fail** |
| migration done | resolves, tests pass | resolves, tests pass |

The old line is checked in every state, so a regression there shows up too.

Getting that instrument right took four attempts, each recorded in the code:
pinning only `typo3/cms-core` (its siblings then conflict), pinning with
`composer require` (which rewrites the manifest before testing it, and would
have scored an untouched tree as success), resolving and installing in one pass
(Composer replaces `typo3/class-alias-loader` under the running plugin and
dies), and parsing the manifest with `python3` (not present in a PHP image).

## Results

Not yet run. Nothing is recorded here until it is.

```
./scripts/run-evaluation OFR-TYPO3-UPGRADE-001 --fleet control
./scripts/run-evaluation OFR-TYPO3-UPGRADE-001 --fleet nr
./scripts/compare jobs/<control-job> jobs/<nr-job>
```

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

A TYPO3 major-version extension upgrade. `netresearch/typo3-extension-upgrade-skill` is in `nr`
and names exactly that.

**Present, and selected** — invoked in three trials of three on Haiku.
