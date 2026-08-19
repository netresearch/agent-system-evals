"""Telemetry for capability selection — not a score for using things.

The old dimension was `skill_routing`, and its mechanical half asked whether a
skill had been invoked at all. That makes not using one automatically worse,
and the runtime case refuted the premise: every arm solved the case, in eight
of nine trials without an MCP the agent booted the framework itself, and no
skill was invoked anywhere. Rewarding invocation would have taught the agent to
invoke something — the definition of Goodharting a benchmark.

So what was a score is now a record. Whether the agent chose *well* among what
it was offered, including the legitimate choice of taking nothing, is a
judgement and lives in judge.toml. An arm that was offered nothing scores N/A
rather than zero, because there was no decision to get right.

The counts themselves are in the capability ledger (scripts/capability-ledger),
which reads provisioning and usage as two separate facts.
"""

from rewardkit import criteria

# Recorded, not rewarded: whether the agent reached for anything at all. The
# judge weighs whether that was the right call for this request.
criteria.nr_used_skill(r".", name="invoked_any_capability", weight=0.0)
