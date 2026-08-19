#!/usr/bin/env bash
# Verifier entrypoint for a contract eval.
#
# No judge. The condition is known, so grading is mechanical and
# deterministic — which is the whole point of this tree: it runs in seconds
# and can gate a merge, which an Open Forward Review cannot. See ADR 0002.
set -euo pipefail

export PATH="/root/.local/bin:$PATH"

python3 - <<'PY'
import shutil
import sys

sys.path.insert(0, "/tests")
import nreval

source = nreval.resolve_trajectory_path()
shutil.copy(source, "/logs/verifier/trajectory.json")
print(f"trajectory: {source} -> /logs/verifier/trajectory.json")
print("wrote", nreval.write_evidence_manifest("/logs/verifier/evidence-manifest.json"))
print("wrote", nreval.write_transcript("/logs/verifier/transcript.txt"))
PY

uvx --from 'harbor-rewardkit==0.1.*' rewardkit /tests
