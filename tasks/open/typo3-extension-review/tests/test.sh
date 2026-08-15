#!/usr/bin/env bash
# Verifier entrypoint. Runs in a separate container seeded from the recorded
# artifacts, never in the agent's environment (ADR 0004).
set -euo pipefail

export PATH="/root/.local/bin:$PATH"

# Normalised view over Harbor's artifacts, written before grading so the judge
# reads the same facts the mechanical criteria do. Without it, each judge
# re-derives the facts from raw logs and disagrees with itself between runs.
python3 - <<'PY'
import sys

sys.path.insert(0, "/tests")
import nreval

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
uvx --from 'harbor-rewardkit==0.1.*' rewardkit /tests
