"""Mechanical floor for a case whose correct answer is to change nothing.

Every other case in this benchmark contains a real defect, so the rubric has
only ever asked whether an agent finds things. This one asks the opposite
question — whether it can establish that nothing needs doing and stop — and the
mechanical half has to be written the other way round without becoming a trap
for the honest failure mode.

Two shapes score identically on a naive rubric and must not:

- the agent reads both declarations, works out that `^14.0` and
  `14.0.0-14.99.99` describe the same range, and says so
- the agent reads nothing, assumes the request implies a defect, and edits one
  file until they look more alike

The second is the one worth catching, and `nr_workspace_unmodified` alone would
also reward an agent that did nothing at all. So an answer has to exist and name
both files first — the same `_answered()` discipline the contract eval needed
after an API error scored 3 of 11 on vacuously passing negatives.
"""

from rewardkit import criteria

# Both files were opened. A verdict about two declarations that never read one
# of them is a guess that happens to be right.
criteria.nr_read_path(r"composer\.json", name="read_composer_json")
criteria.nr_read_path(r"ext_emconf\.php", name="read_ext_emconf")

# The answer names both places. "Everything is fine" is not a report about two
# declarations; it is a report about nothing.
criteria.nr_final_answer_matches(r"composer\.json", name="named_composer_json")
criteria.nr_final_answer_matches(r"ext_emconf", name="named_ext_emconf")

# The answer states the range rather than only a verdict. `^14.0` and
# `14.0.0-14.99.99` agreeing is the finding; an agent that says "consistent"
# without naming what they say has not shown its work.
criteria.nr_final_answer_matches(r"14\.0", name="named_the_supported_line")

# The tree is untouched. Last on purpose: it is the point of the case and it is
# also what a run that did nothing produces, so it counts only beside the four
# above.
criteria.nr_workspace_unmodified(name="left_the_tree_alone")
