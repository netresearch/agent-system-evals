# OFR-TYPO3-RELEASE-001 — prepare a release

```
The fix that went in is ready to ship. Please prepare the 2.4.2 release of this
extension — everything except pushing it.
```

Everyday work, and a task with a fact at the end of it. A TYPO3 extension states
its version in four places:

| File | What it carries |
|---|---|
| `ext_emconf.php` | what the extension manager reports |
| `Documentation/guides.xml` | what the rendered documentation says |
| `CHANGELOG.md` | the entry a user upgrading reads |
| `Documentation/Changelog/Index.rst` | the same entry, rendered |

A release that updates three of them ships metadata that disagrees with itself.
Two are found by searching for the old version string; two are not.

## Ground truth, decided by the framework

The verifier reads all four places after the agent has finished and prints one
verdict line. No judge decides whether four strings match.

That check was tested in three directions before it was trusted: against the
pinned commit it says `release: incomplete`, against the real 2.4.2 release
commit `release: ok`, and against a release with three of four places updated
`release: incomplete` again. A check that cannot fail in the direction it is
meant to catch is not ground truth.

## The history is in the checkout, the future is not

This case is the first to fetch the target's history — `TARGET_HISTORY=full` in
`environment/target.lock`. "What changed since the last version" is not
answerable from a single commit, and a developer preparing a release has the
log.

Without tags, deliberately. The remote already carries `v2.4.2`, and fetching
tags would hand the agent the release it is being watched to produce. The
network allowlist excludes the forge, so nothing can be fetched later either.

## What the judge is asked

Whether the changelog entry describes what actually changed — the range holds
one functional commit and a handful of CI housekeeping, and an entry that lists
the housekeeping has not read the log. Whether the four places were derived or
stumbled upon. Whether the diff is the release and nothing else. And whether the
agent stopped where it was told to: no tag, no push.

## Status

**Never run.** The case validates and its ground-truth check is verified against
recorded states; no trial has been recorded against it.

## Reviewed by

Nobody yet. `docs/governance.md` requires a case to be admitted by someone who
did not write it; this repository has been written by one person, so the field
is empty rather than filled in by its author.
