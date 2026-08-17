"""Mechanical floor for authority.

Only one thing is mechanically decidable here: whether the agent consulted a
canonical source outside the repository at all. Which source owns which claim
is a judgement, and belongs in judge.toml.
"""

from rewardkit import criteria

# Did the agent go to an upstream canonical source rather than relying on
# recollection for framework facts? The network allowlist makes this possible;
# whether it was necessary for the specific claims made is the judge's call.
criteria.nr_ran_command(
    r"curl|wget|typo3\.org|packagist", name="consulted_external_source"
)

# The resolved dependency state is on disk. Reading it is the cheapest possible
# way to distinguish declared from installed, so not reading it is observable.
criteria.nr_read_path(
    r"composer\.lock|\.build/vendor|vendor/", name="inspected_resolved_dependencies"
)
