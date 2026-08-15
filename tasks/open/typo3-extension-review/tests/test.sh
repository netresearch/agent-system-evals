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
# Judge concurrency is capped at 2. Eight dimensions firing at once tripped an
# Anthropic rate limit on the first real run, and RewardKit retries only on a
# schema mismatch — a rate-limited judge raises, and one raised reward aborts
# the whole run. Seven dimensions had already scored and were discarded with
# it, leaving no reward.json at all. Slower here is the correct trade: the
# alternative is losing an entire agent trial to one throttled call.
uvx --from 'harbor-rewardkit==0.1.*' rewardkit /tests --max-concurrent-llm 2
