"""Did the work actually work?

For a writing task this is not a judgement. The collect hooks pinned the tree
the agent left to each supported line, installed it and ran the project's own
unit suite; these criteria read those verdicts.

The artifacts are required, not optional: a missing one means the hook did not
run, which is an infrastructure failure. nreval raises in that case rather than
returning False, so a broken harness is reported as an error instead of being
scored as the agent's failure.

Nothing here asserts *which* line the agent should target. The request said
"the current LTS" and did not say whether the older line is kept; that is the
project's own convention, and weighing the choice is the judge's job. What is
recorded mechanically is what the result does on each line.
"""

from rewardkit import criteria

# The line the request pointed at. If the result does not resolve here, the
# task was not done, whatever else happened.
criteria.nr_artifact_matches(
    "matrix-14.3.txt", r"^LEG=14\.3 RESOLVE=ok", name="resolves_on_current_lts"
)
criteria.nr_artifact_matches(
    "matrix-14.3.txt", r"TESTS=passed", name="tests_pass_on_current_lts"
)

# The line the extension already supported. Recorded, not demanded: dropping it
# may be defensible, and the judge weighs that against the project's own
# convention. Scored so the vector shows what happened either way.
criteria.nr_artifact_matches(
    "matrix-13.4.txt", r"^LEG=13\.4 RESOLVE=ok", name="resolves_on_previous_lts"
)
criteria.nr_artifact_matches(
    "matrix-13.4.txt", r"TESTS=passed", name="tests_pass_on_previous_lts"
)

# The manifest must still be a valid manifest. A migration that leaves
# composer.json malformed fails before any of the above becomes interesting.
criteria.nr_artifact_matches(
    "composer-validate.txt", r"is valid", name="manifest_still_valid"
)

# Doing nothing is not an answer to a writing request. Stated positively rather
# than as a negated criterion: a negated one inverts the raw score, and mixing
# polarity inside a dimension makes the reward unreadable.
criteria.nr_workspace_modified(name="made_changes")
