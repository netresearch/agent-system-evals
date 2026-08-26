# OFR-GO-LDAP-001 — recorded results

## One trial, discarded by construction

Job `OFR-GO-LDAP-001-nr-go-20260826-104500`, 26 August 2026, `claude-haiku-4-5-20251001`. Valid by every
check the validity gate makes, and not a result.

The environment that trial ran in had been built with `git clone` followed by
`git checkout <sha>`, which left every later commit in `.git` — the upstream
fix this case exists to see written, its tests, its commit messages — and a
remote pointing at the forge. Instrument failure 21 in
[docs/instrument-failures.md](../../../docs/instrument-failures.md).

The trial itself did not look: its only git command was `git diff /app/auth.go`.
It scored 0.875 — parity established against the directory, a fix that binds the
raw DN rather than the escaped helper, no test left behind. None of that is
evidence, because the image it ran in offered the answer, and a trial cannot be
credited for declining an offer it did not know it had.

The build script now fetches the one commit at depth 1 without tags and removes
the remote, as the TYPO3 cases' script always did, and proves it at build time.
`tests/test_environment.py` asserts the same of every build script against its
source. The job directory stays on disk under its name so the discard can be
checked; it is excluded from every figure, and the first result this case
records will come from the rebuilt environment.
