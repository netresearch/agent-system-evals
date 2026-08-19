"""Pass/fail on the planted condition. No judge, by design.

A contract eval asks whether a specific check fires. That question has an
answer, so it is graded mechanically: the four properties that cannot be
hydrated must be named, and the two that can must not be reported as broken.

The false-positive half matters as much as the other. An agent that answers
"every property in both classes" has not found the defect, it has listed the
file — and without the negative criterion that answer would score full marks.
"""

from rewardkit import criteria

# The four private properties, each named with enough context to show it was
# located rather than guessed.
for prop in ("sku", "price", "name", "sorting"):
    criteria.nr_final_answer_matches(rf"\b{prop}\b", name=f"named_{prop}")

# Both classes identified.
criteria.nr_final_answer_matches(r"\bProduct\b", name="named_class_product")
criteria.nr_final_answer_matches(r"\bCategory\b", name="named_class_category")

# The mechanism, not just the symptom: `private` is what makes them
# unreachable from AbstractEntity's parent scope.
criteria.nr_final_answer_matches(
    r"private", name="named_the_visibility_as_the_cause"
)

# The agent looked at the source rather than answering from the prompt.
criteria.nr_read_path(r"Classes/Domain/Model", name="read_the_models")
