"""Where the agent got its facts.

This case exists because both fleets failed this dimension identically on the
review case: no external canonical source consulted, the resolved dependency
state never read, every version claim resting on recollection.

Here that is not merely sloppy, it is disqualifying. Which line is current,
what the newest one removed, and which packages it pulls into the dependency
graph are not derivable from the checkout. They are in the framework's own
changelog and release data, and the network allowlist deliberately permits
exactly those hosts.
"""

from rewardkit import criteria

# Did the agent go to a canonical upstream source at all?
criteria.nr_ran_command(
    r"curl|wget|typo3\.org", name="consulted_upstream_source"
)

# Release data over recollection: which line is current is a fact with an
# owner, and get.typo3.org is that owner.
criteria.nr_ran_command(
    r"get\.typo3\.org|api\.typo3\.org|packagist", name="looked_up_release_data"
)

# The changelog is where breaking changes and deprecations live. An upgrade
# performed without opening it is an upgrade performed from memory.
criteria.nr_ran_command(
    r"docs\.typo3\.org|Changelog", name="consulted_changelog"
)

# What is actually installed, as opposed to what the manifest permits. A
# constraint states what is allowed; the lock and the vendor tree state what is
# there, and only one of those can be tested against.
criteria.nr_read_path(
    r"composer\.lock|vendor/typo3", name="inspected_resolved_dependencies"
)
