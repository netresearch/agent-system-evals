"""Mechanical floor for skill routing.

Records which capabilities were reached and by what route. Whether the routing
was *right* is the judge's question — a mechanical check that demanded one
named skill would encode today's stack into the benchmark, and the benchmark
would then resist exactly the improvements it exists to detect.

Note the asymmetry: reaching an assessment capability at all is checkable,
whether it was the correct one for this request is not.
"""

from rewardkit import criteria

# Was any skill reached at all? An agent that never routes is a distinct and
# interesting failure from one that routes badly.
criteria.nr_used_skill(r".", name="invoked_any_skill")

# Did an assessment or conformance capability get reached, by any name? The
# pattern is deliberately broad: it asks whether the agent found the systematic
# route, not whether it picked a particular skill.
criteria.nr_used_skill(
    r"assessment|conformance|audit|review", name="reached_assessment_capability"
)
