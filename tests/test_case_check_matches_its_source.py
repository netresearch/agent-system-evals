"""The embedded behavioural check and the file it is read from must agree.

`OFR-TYPO3-RESIZE-001` grades on a functional test that cannot live in the
agent's tree — there it would hand over the expected output as a fixture — and
cannot be copied from the task's `tests/` directory either, because a collector
runs in the environment container where that directory is not mounted. So the
source is embedded in the collector.

That leaves two copies of the same 265 lines. The one in `tests/` is what a
reader reads and what the case's README points at; the one in `task.toml` is
what actually runs. A change to either alone is invisible: the case keeps
grading, on a test nobody reviewed.
"""

from __future__ import annotations

import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CASE = ROOT / "tasks" / "open" / "typo3-rte-figure-resize"
MARKER = "NREVAL_FIGURE_TEST"


def embedded_check() -> str:
    task = tomllib.loads((CASE / "task.toml").read_text())
    commands = [c["command"] for c in task["verifier"]["collect"] if MARKER in c["command"]]
    assert len(commands) == 1, f"expected one embedded check, found {len(commands)}"
    body = commands[0].split(f"<<'{MARKER}'\n", 1)[1]
    return body.split(f"\n{MARKER}", 1)[0]


def test_the_running_check_is_the_file_that_was_reviewed():
    source = (CASE / "tests" / "FigureResizeWidthRenderingTest.php").read_text()
    assert embedded_check().strip() == source.strip()


def test_the_check_asserts_through_the_public_rendering_entry_point():
    """Why this candidate was adopted, pinned so a rewrite cannot quietly undo it.

    Four other mined candidates were rejected because their test reflected into
    a method the fix introduced, so an agent repairing the same defect
    elsewhere would fail a test expecting an implementation it had no reason to
    write. This one drives `renderFigure`, public at the pinned commit.
    """
    source = (CASE / "tests" / "FigureResizeWidthRenderingTest.php").read_text()
    assert "->renderFigure(" in source
    assert "invokeMethod" not in source, "reflection into a private method couples the check to one fix"


def test_the_check_is_not_in_the_agents_tree():
    """The build asserts it, and this asserts the build still asserts it."""
    build = (CASE / "environment" / "build-target.sh").read_text()
    assert "test ! -e /app/Tests/Functional/Controller/FigureResizeWidthRenderingTest.php" in build
