#!/usr/bin/env bash
# Verifier entrypoint. Runs in a separate container seeded from the recorded
# artifacts, never in the agent's environment (ADR 0004).
set -euo pipefail

export PATH="/root/.local/bin:$PATH"

# Normalised view over Harbor's artifacts, written before grading so the judge
# reads the same facts the mechanical criteria do. Without it, each judge
# re-derives the facts from raw logs and disagrees with itself between runs.
python3 - <<'PY'
import shutil
import sys

sys.path.insert(0, "/tests")
import nreval

# Stage the trajectory at one fixed path. The judge configs need a literal
# path, and where Harbor actually delivers the trajectory depends on the
# artifact layout — so the resolution lives here, once, instead of being
# repeated as a guess in eight judge.toml files.
source = nreval.resolve_trajectory_path()
shutil.copy(source, "/logs/verifier/trajectory.json")
print(f"trajectory: {source} -> /logs/verifier/trajectory.json")

path = nreval.write_evidence_manifest("/logs/verifier/evidence-manifest.json")
print(f"wrote {path}")
PY

# One reward per subdirectory of /tests. Version-pinned: an unpinned judge
# harness would silently change what recorded results mean.
#
# `--from`, not `--with`: the executable lives in harbor-rewardkit, and the
# form shown in Harbor's documentation (`uvx --with harbor-rewardkit@0.1
# rewardkit`) makes uv look for a distribution called `rewardkit`, which does
# not exist. Measured, not assumed.
#
# Judging runs through the Claude Code CLI (see tests/Dockerfile), so the
# relevant cap is the agent one. Direct API judging was tried first and does
# not work on a subscription token: eight concurrent dimensions hit an
# Anthropic rate limit, and reducing concurrency to one did not help — the
# limit is on the credential, not on the parallelism.
#
# The cap still matters, because RewardKit retries only on a schema mismatch.
# A judge that raises aborts the whole run and discards every dimension that
# had already scored, so one throttled call can cost an entire agent trial.
uvx --from 'harbor-rewardkit==0.1.*' rewardkit /tests --max-concurrent-agent 2

# A judge that could not see the evidence scores everything not-met, and the
# result is a complete, well-formed, entirely wrong vector. That happened here:
# the agent judge inherited /app as its working directory, could not open the
# trajectory, and returned zeros for a review that was in fact strong. It said
# so in its reasoning; nothing downstream could tell that apart from a genuine
# zero.
#
# So the reasoning is checked for admissions of blindness. A verifier that
# cannot see must fail loudly, never score low — the same rule as raising on a
# missing trajectory rather than returning False.
python3 - <<'PY'
import json
import re
import sys
from pathlib import Path

details = Path("/logs/verifier/reward-details.json")
if not details.exists():
    sys.exit(0)  # nothing scored; the run already failed for another reason

BLIND = re.compile(
    r"unable to (access|read|open)|could not (access|read|open)|"
    r"restricted to|no evidence was observable|file not found",
    re.IGNORECASE,
)

def reasons(node):
    if isinstance(node, dict):
        if isinstance(node.get("reasoning"), str):
            yield node.get("name") or "?", node["reasoning"]
        for value in node.values():
            yield from reasons(value)
    elif isinstance(node, list):
        for item in node:
            yield from reasons(item)

blind = [
    (name, text)
    for name, text in reasons(json.loads(details.read_text()))
    if BLIND.search(text)
]
if blind:
    print("\nverifier is blind — scores would be meaningless:", file=sys.stderr)
    for name, text in blind[:5]:
        print(f"  {name}: {text[:200]}", file=sys.stderr)
    sys.exit(1)
PY
