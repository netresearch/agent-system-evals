"""The environment hands the agent a commit, not a repository with a future.

Every case pins a commit before a real fix, and the fix has to stay in the
verifier's hands. A build script that clones the repository and checks the
commit out leaves the fix in `.git` — every later commit, its tests, its
messages — and a remote pointing at the forge. Instrument failure 21: the
first Python trial ran `git log --all --grep`, found both upstream fixes, and
copied them.

Asserted against the source of every build script, because the failure is
silent at run time: the trajectory validates, the collectors run, the check
passes, and the number looks like a result.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
BUILD_SCRIPTS = sorted(ROOT.glob("tasks/*/*/environment/build-*.sh"))


def offences(text: str) -> list[str]:
    found = []
    if re.search(r"^\s*git\s+clone\b", text, re.M):
        found.append("clones the repository — the whole history arrives with it")
    if not re.search(r"git\s+fetch\b[^\n]*--depth\s+1", text):
        found.append("does not fetch with --depth 1")
    if not re.search(r"git\s+fetch\b[^\n]*--no-tags", text):
        found.append("does not fetch with --no-tags — a release tag is an answer")
    if not re.search(r"git\s+remote\s+remove\s+origin", text):
        found.append("leaves the remote in place, pointing at the forge")
    return found


@pytest.mark.parametrize("script", BUILD_SCRIPTS, ids=lambda p: str(p.relative_to(ROOT)))
def test_build_script_fetches_one_commit_and_forgets_the_forge(script):
    assert BUILD_SCRIPTS, "no build scripts found; the glob is wrong, not the repository"
    found = offences(script.read_text())
    assert found == [], f"{script.relative_to(ROOT)}: " + "; ".join(found)


def test_the_check_catches_a_clone():
    """The counter-probe: the shape that leaked has to fail this test."""
    leaked = 'git clone -q "$TARGET_REPOSITORY" /app\ngit -C /app checkout -q "$TARGET_COMMIT"\n'
    assert offences(leaked)
    sound = (
        'git init -q\ngit remote add origin "$TARGET_REPOSITORY"\n'
        'git fetch -q --depth 1 --no-tags origin "$TARGET_COMMIT"\n'
        "git checkout -q FETCH_HEAD\ngit remote remove origin\n"
    )
    assert offences(sound) == []
