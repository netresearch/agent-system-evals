"""Mechanical floor: does it render, and did the agent read the extension?

The verdict on shape is in `docs-check.txt` — a guides.xml naming the project,
an Index.rst, and a toctree whose every entry resolves. That check was written
against four recorded states before it was trusted, including the one that
matters most: an index listing pages nobody wrote, which looks complete in a
diff and fails at render.

What it cannot see is whether the prose is about *this* extension. A template
filled in with the extension's name passes every structural check ever written,
so the criteria below ask where the content came from.
"""

from rewardkit import criteria

# The framework's verdict on shape.
criteria.nr_artifact_matches("docs-check.txt", r"docs: ok", name="documentation_renders")

# The material was read. This extension ships a README and an architecture note;
# documentation written without opening either is documentation about a
# category of extension rather than about this one.
criteria.nr_read_path(r"README", name="read_the_readme")
criteria.nr_read_path(r"Classes/", name="read_the_code")

# The extension key appears in what was written. `guides.xml` needs it, and an
# agent that never established it has guessed at the one string docs.typo3.org
# indexes the extension under.
criteria.nr_artifact_matches(
    "guides.after.xml", r"[Ii]mage\s*[Ss]itemap", name="named_the_extension"
)

# The tree changed, and the answer says where. A report describing documentation
# that was never written is the failure this pairs against.
criteria.nr_workspace_modified(name="changed_the_tree")
criteria.nr_final_answer_matches(r"Documentation", name="named_the_directory")
