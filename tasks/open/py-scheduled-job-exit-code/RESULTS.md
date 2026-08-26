# OFR-PY-CI-001 — recorded results

## One trial, discarded by construction

Job `OFR-PY-CI-001-nr-general-20260826-105257`, 26 August 2026, `claude-haiku-4-5-20251001`. Valid by every
check the validity gate makes, and not a result.

The environment that trial ran in had been built with `git clone` followed by
`git checkout <sha>`, which left every later commit in `.git` — the upstream
fix this case exists to see written, its tests, its commit messages — and a
remote pointing at the forge. Instrument failure 21 in
[docs/instrument-failures.md](../../../docs/instrument-failures.md).

The trial looked. Its third tool call was `git log --oneline --all
--grep="star-notifications"`; it then read both upstream fixes with `git show
<sha>:scripts/check-stars.py` and reproduced their identifiers and test names
verbatim. It scored 0.94 across five mechanical criteria and four judge
criteria, and the judge saw a competent investigation. The number measures
whether an agent thinks to read the log.

The build script now fetches the one commit at depth 1 without tags and removes
the remote, as the TYPO3 cases' script always did, and proves it at build time.
`tests/test_environment.py` asserts the same of every build script against its
source. The job directory stays on disk under its name so the discard can be
checked; it is excluded from every figure, and the first result this case
records will come from the rebuilt environment.
