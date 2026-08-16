"""What the agent established before changing anything.

Unlike the review case, this target ships an AGENTS.md. Context discovery is
deliberately easier here — the two cases should not test the same thing — so
what matters is less "did it find the entry point" and more "did it read enough
to know what a version move implies for *this* repository".
"""

from rewardkit import criteria

criteria.nr_read_path(r"composer\.json|ext_emconf\.php", name="read_package_manifest")
criteria.nr_read_path(r"AGENTS\.md|README|CONTRIBUTING", name="read_project_instructions")

# Where the version window is enforced beyond the manifest: the CI matrix is
# the place a supported-version claim is actually exercised.
criteria.nr_read_path(
    r"\.github/workflows|Build/|Makefile", name="read_build_and_ci_configuration"
)

criteria.nr_read_path(r"Classes/.*\.php", name="read_source")
