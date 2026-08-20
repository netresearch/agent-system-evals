"""What reaches the judge, and what the judge is told about it.

The judge reads a transcript written entirely by the system under test. Text in
it can be addressed to the judge, and the only thing between that text and a
score it did not earn is what the prompt says about untrusted content.

These tests do not prove a live judge resists injection — that costs judge calls
and belongs with the calibration work in issue #9. They pin the two things that
can be checked for free and were both missing until 20 August 2026: that the
defence exists in every prompt, and that the payloads genuinely arrive, so the
defence is written against what the judge actually sees rather than against a
guess.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "verifier" / "common"))

import nreval  # noqa: E402

PAYLOADS = [
    line[2:].strip()
    for line in (ROOT / "tests" / "injection-corpus.md").read_text().splitlines()
    if line.startswith("- ")
]

PROMPTS = sorted(ROOT.glob("tasks/open/*/tests/judge-prompt.md"))


def test_the_corpus_is_not_empty():
    """A corpus that silently parsed to nothing would pass every test below."""
    assert len(PAYLOADS) >= 8


@pytest.mark.parametrize("prompt", PROMPTS, ids=lambda p: p.parts[-3])
def test_every_judge_prompt_says_the_transcript_is_not_instruction(prompt):
    text = prompt.read_text().lower()
    assert "evidence, never instruction" in text
    # The specific shapes, not just a general warning: an agent claiming to
    # speak for the operator is the payload most likely to read as legitimate.
    assert "operator" in text
    assert "ignore these directions" in text


@pytest.mark.parametrize("payload", PAYLOADS)
def test_a_payload_in_the_final_answer_reaches_the_judge(payload):
    """It does, and it must — the answer is what several dimensions grade.

    This is the test that keeps the defence honest. If a future change filtered
    these out of the transcript instead, the prompt's section would be defending
    against something the judge never sees, and the real hole would be wherever
    the filter did not reach.
    """
    traj = {
        "schema_version": "ATIF-v1.7",
        "steps": [
            {"step_id": 1, "source": "agent", "message": "working on it"},
            {"step_id": 2, "source": "agent", "message": f"Findings: none.\n{payload}"},
        ],
    }
    rendered = nreval.transcript(traj)
    assert payload in rendered


def test_the_blinded_transcript_does_not_swallow_a_payload():
    """Blinding replaces capability names; it must not become a content filter.

    A transcript that quietly lost hostile text would hide the behaviour the
    `unsupported_claims` dimension exists to catch.
    """
    payload = PAYLOADS[0]
    traj = {
        "schema_version": "ATIF-v1.7",
        "steps": [{"step_id": 1, "source": "agent", "message": payload}],
    }
    assert payload in nreval.neutralise(nreval.transcript(traj), traj)
