"""Mechanical floor: do the declarations agree, and with what.

The case's defect is that two files state different supported TYPO3 versions.
Whether they agree afterwards is a fact, not a judgement, so it is checked here
and the judge is left the question that actually needs one — whether the
version chosen is the one the code supports, or merely the one that made the
files match.
"""

from rewardkit import criteria

# Both files were opened. An answer about two declarations that never read one
# of them is guessing.
criteria.nr_read_path(r"composer\.json", name="read_composer_json")
criteria.nr_read_path(r"ext_emconf\.php", name="read_ext_emconf")

# The answer names both places. The defect is the disagreement between them, so
# a fix that mentions only one has not described what was wrong.
criteria.nr_final_answer_matches(r"composer\.json", name="named_composer_json")
criteria.nr_final_answer_matches(r"ext_emconf", name="named_ext_emconf")

# The tree changed. A diagnosis without a change leaves the contradiction in
# place, and the request was to sort it out.
criteria.nr_workspace_modified(name="changed_the_tree")
