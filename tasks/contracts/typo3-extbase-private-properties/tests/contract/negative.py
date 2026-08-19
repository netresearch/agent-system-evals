"""The other half of pass/fail: what must NOT be reported.

`title`, `description` and `category` are `protected` and persist correctly.
An answer that calls them broken has listed the file rather than found the
defect, and would otherwise score full marks on the positive criteria alone.
"""

import re
import sys
from pathlib import Path

from rewardkit import criterion

# The shared library sits one directory up, whether that is /tests in the
# verifier container or the case directory when scripts/validate-rubric loads
# this file. Importing it by name alone works in the first and not the second.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import nreval  # noqa: E402


def _answered() -> bool:
    """Is there an answer at all?

    The negative criteria are the reason this matters. "Did not report `title`
    as broken" is trivially true of an empty answer, so a trial whose agent
    never ran scored 3 of 11 instead of 0 — a floor under failure, which is
    exactly the shape that gets read as a partial result. One such trial
    happened here: the agent answered
    `API Error: Unable to connect to API`, and the contract still gave it
    points for the things it had not said.
    """
    answer = nreval.final_answer().strip()
    if len(answer) < 40:
        return False
    return not re.match(r"^\s*API Error", answer)


def _claims_broken(prop: str) -> bool:
    """Is this property named in a sentence that calls something broken?

    Deliberately narrow. The word appearing anywhere is not a false positive —
    an answer may legitimately say "title and description are fine". Only a
    claim *against* it counts, so the sentence has to carry the defect
    vocabulary too.
    """
    answer = nreval.final_answer()
    for sentence in re.split(r"(?<=[.;:\n])", answer):
        # Case-sensitive, and never the class of the same name. `category` is a
        # property of Product; `Category` is a class, and a correct answer says
        # "Category::$name is private" in the very sentence that would
        # otherwise look like a claim against the property. The first version
        # of this check failed a correct answer for exactly that reason.
        without_classes = re.sub(r"\b[A-Z]\w*::", " ", sentence)
        if re.search(rf"(?<![\w$]){prop}\b", without_classes) and re.search(
            r"private|cannot be (persisted|hydrated)|never reach|broken|affected",
            sentence,
            re.IGNORECASE,
        ):
            if re.search(r"\b(not|correct|fine|unaffected|protected)\b", sentence, re.IGNORECASE):
                continue
            return True
    return False


@criterion(description="Did not report `title` as broken")
def title_not_reported(workspace) -> bool:
    return _answered() and not _claims_broken("title")


@criterion(description="Did not report `description` as broken")
def description_not_reported(workspace) -> bool:
    return _answered() and not _claims_broken("description")


@criterion(description="Did not report `category` as broken")
def category_not_reported(workspace) -> bool:
    return _answered() and not _claims_broken("category")
