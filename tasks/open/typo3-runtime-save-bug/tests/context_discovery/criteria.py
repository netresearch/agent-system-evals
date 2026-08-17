"""Mechanical floor for context discovery.

Establishes what the agent actually opened. Whether that was enough is the
judge's question, in judge.toml.

Deliberately not asserted here: that any *particular* file was read. A
repository may carry its authoritative entry point somewhere other than where
we expect, and a criterion that demands one filename would score a correct
route as a failure. What is asserted is that the agent established the project
identity and its dependency state at all, by whatever route.
"""

from rewardkit import criteria

# What kind of package is this, and for which framework version? Both live in
# composer.json for a Composer project, and in ext_emconf.php for a TYPO3
# extension specifically. Either establishes identity; the judge weighs whether
# the agent understood what it read.
criteria.nr_read_path(r"composer\.json|ext_emconf\.php", name="read_package_manifest")

# Did it look at the code at all, rather than reviewing the packaging alone?
criteria.nr_read_path(r"Classes/.*\.php", name="read_source")

# Project documentation is a declared source of intent. Not reading it is not
# fatal, but it is observable.
criteria.nr_read_path(
    r"README|Documentation/|CHANGELOG", name="read_project_documentation"
)

# Scope discipline — a review is read-only, so modifying the tree exceeds the
# request — is deliberately NOT checked here.
#
# It was, and scripts/verifier-selftest caught the consequence: an agent that
# did nothing at all satisfied it, and scored 0.25 on context discovery for
# having discovered nothing. Any criterion a no-op can satisfy is not measuring
# work, and averaging one into a dimension that is meant to measure work gives
# every idle run a floor above zero.
#
# The check itself remains in the library and is exercised by the verifier
# tests. Unrequested modification is weighed by the outcome_quality judge,
# which reads git.modified from the evidence manifest and cannot reward
# inaction, because its other criteria require substance.
