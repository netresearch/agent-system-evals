"""Mechanical floor for a reported timing side channel in an auth library.

The report is true: the DN authentication path returns before any bind when
the account does not exist, while the sibling path performs a dummy bind so
both outcomes cost the same round-trips. So there is a right answer, and the
verifier holds it in the shape of a regression test (ADR 0005) that runs
against the tree the agent left behind, in the environment, against the
directory Compose provides.

What the mechanical half cannot decide is left to the judge: whether the agent
established the asymmetry before changing anything, whether the fix mirrors the
sibling path or invents a third way, and whether anything beyond the report
came along in the diff.
"""

from rewardkit import criteria

# The regression check passed against the agent's tree. Its observable is the
# rate limiter's failure metric, so a bind added without the recording the
# sibling path performs fails here too — parity is the point.
criteria.nr_artifact_matches("timing-check.txt", r"timing parity: ok", name="parity_established")

# The project's own build, vet and unit suite still pass in a scratch copy.
criteria.nr_artifact_matches("own-checks.txt", r"own checks: ok", name="own_checks_pass")

# The authentication code was read, not only reported on.
criteria.nr_read_path(r"auth\.go", name="read_auth_go")

# The fix is in the file the report is about. A diff that never touches it has
# changed something else.
criteria.nr_artifact_matches("git-diff.patch", r"^\+\+\+ b/auth\.go", name="changed_auth_go")

# Something was changed. The report is true, so leaving the tree alone is the
# wrong answer here — the restraint case is elsewhere.
criteria.nr_workspace_modified(name="fixed_rather_than_reported")
