"""Mechanical floor: is the release actually complete, and was it derived?

A TYPO3 extension states its version in four places, and a release that updates
three of them ships metadata that disagrees with itself — the extension manager,
the rendered documentation and the changelog then say different things about
what is installed. Whether four strings match is a fact, so it is checked here
and `release-check.txt` carries the verdict.

The rest is about where the content came from. A changelog entry can be written
without reading anything, and one that says "various fixes" passes any check
that only counts sections. So the history has to have been opened.
"""

from rewardkit import criteria

# The verdict the framework computed, not a judgement. See the collector in
# task.toml: it reads all four places and prints one line.
criteria.nr_artifact_matches(
    "release-check.txt", r"release: ok", name="all_four_places_agree"
)

# The two that are easy to miss. Named separately from the verdict so a
# partial release says *which* half was missed rather than only that it was.
criteria.nr_read_path(r"ext_emconf\.php", name="read_ext_emconf")
criteria.nr_read_path(r"guides\.xml", name="read_guides_xml")
criteria.nr_read_path(r"CHANGELOG\.md", name="read_changelog")

# The history was consulted. A changelog entry for a release nobody looked into
# is a guess with a version number on it, and this case exists in a repository
# whose one change since the last release is specific enough to describe.
criteria.nr_ran_command(r"git (log|show|diff)", name="read_the_history")

# The tree changed. A release that reports what should happen has not prepared
# one.
criteria.nr_workspace_modified(name="changed_the_tree")

# The version appears in the answer. A report on a release that never names the
# version being released leaves the reader to check.
criteria.nr_final_answer_matches(r"2\.4\.2", name="named_the_version")
