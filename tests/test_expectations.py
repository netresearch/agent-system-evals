"""Expectations stay out of the public repository, and the runner stays honest.

The first three tests are the regression guard for the thing that was wrong for
as long as this repository has existed: the files naming each case's expected
findings were committed in plaintext, in a public repository, while two
documents said they were not. A guard that only checks the working tree would
miss a file that is ignored locally and tracked anyway, so this asks git.
"""

from __future__ import annotations

import importlib.machinery
import importlib.util
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def tracked_files() -> list[str]:
    result = subprocess.run(
        ["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True
    )
    return result.stdout.splitlines()


def test_no_plaintext_known_concerns_is_tracked():
    stray = [p for p in tracked_files() if p.endswith("known-concerns.md")]
    assert stray == [], (
        f"{stray} are committed in plaintext. Expectations belong in "
        f"expectations/<case-id>.md.enc; see expectations/README.md."
    )


def test_only_ciphertext_and_the_readme_live_in_the_store():
    stored = [p for p in tracked_files() if p.startswith("expectations/")]
    unexpected = [
        p
        for p in stored
        if not p.endswith(".md.enc") and p != "expectations/README.md"
    ]
    assert unexpected == [], f"{unexpected} should not be committed"


def test_every_open_case_has_encrypted_expectations():
    stored = {
        p[len("expectations/") : -len(".md.enc")]
        for p in tracked_files()
        if p.startswith("expectations/") and p.endswith(".md.enc")
    }
    import tomllib

    missing = []
    for task in sorted(ROOT.glob("tasks/open/*/task.toml")):
        case_id = tomllib.loads(task.read_text()).get("metadata", {}).get("case_id")
        if case_id and case_id not in stored:
            missing.append(case_id)
    assert missing == [], f"no recorded expectations for {missing}"


def test_the_ciphertext_is_not_readable_as_text():
    """Cheap sanity check: a Fernet token is base64 and carries no prose."""
    for path in sorted((ROOT / "expectations").glob("*.md.enc")):
        body = path.read_bytes()
        assert body.startswith(b"gAAAAA"), f"{path.name} is not a Fernet token"
        assert b"TYPO3" not in body


# --- the comparison runner's job resolution ---------------------------------


def load(name: str):
    spec = importlib.util.spec_from_loader(
        name,
        importlib.machinery.SourceFileLoader(name, str(ROOT / "scripts" / name)),
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


runner = load("run-comparison")


def test_the_job_is_read_from_the_run_not_guessed_from_a_glob():
    """Globbing for the newest match is a race that returns a wrong answer.

    The previous version picked `jobs/<case>-<fleet>-*` by modification time,
    so anything else writing into `jobs/` at the same moment silently changed
    which directory an arm was credited with.
    """
    out = (
        "harbor: 1 trial\n"
        "snapshot written to /x/jobs/OFR-1-nr-20260820-101112/nr-snapshot.json\n"
    )
    assert runner.resolve_job(out) == Path("/x/jobs/OFR-1-nr-20260820-101112")


def test_a_run_that_reported_no_job_resolves_to_nothing():
    assert runner.resolve_job("harbor: failed to start\n") is None


def test_the_miner_refuses_to_call_a_candidate_admitted():
    """It finds raw material and cannot decide admission.

    The criterion that rejected five of seven candidates in August 2026 — the
    fix's test must fail at the commit before the fix — is only knowable by
    building the tree twice. A miner that printed a verdict would have admitted
    at least one case whose check could never fail (docs/case-lifecycle.md 7-9).
    """
    source = (ROOT / "scripts" / "mine-cases").read_text()
    assert "None of them is admitted until both commands above have been run." in source
    assert "must FAIL" in source and "must PASS" in source
    # And it must not silently treat a maintainer's own report as an outside
    # request when no insider list was given.
    assert "--insiders was empty" in source
