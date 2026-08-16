"""Which capability the agent reached, and by what route.

Whether the routing was *right* is the judge's question. A mechanical check
demanding one named skill would encode today's stack into the benchmark, and
the benchmark would then resist the improvements it exists to detect.
"""

from rewardkit import criteria

criteria.nr_used_skill(r".", name="invoked_any_skill")

# An upgrade capability, by any name. Broad on purpose: the question is whether
# the agent found the systematic route for this kind of work, not whether it
# picked a particular skill.
criteria.nr_used_skill(
    r"upgrade|migrat|conformance|assessment", name="reached_upgrade_capability"
)
