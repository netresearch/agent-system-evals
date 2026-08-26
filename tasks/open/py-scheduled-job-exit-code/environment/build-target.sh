#!/usr/bin/env bash
# Materialise the target at its pinned commit and prove the environment can
# produce the asked-for result before the agent arrives (ADR 0007): the test
# dependencies install from the repository's own hash-pinned list, and its own
# suite passes. A failure here is a broken case, never a trial.
set -euo pipefail

LOCK="${1:?target.lock}"
# shellcheck disable=SC1090
. "$LOCK"

git clone -q "$TARGET_REPOSITORY" /app
git -C /app checkout -q "$TARGET_COMMIT"
git -C /app checkout -q -b work
test "$(git -C /app rev-parse HEAD)" = "$TARGET_COMMIT"

cd /app
# The repository's own CI installs exactly this way: hashes for the whole
# resolved tree, wheels only. Reproduced rather than approximated so the
# agent's `pytest` is the same `pytest` CI runs.
pip install --only-binary :all: --require-hashes -r requirements/tests.txt
MATRIX_WEBHOOK_URL=https://example.invalid/webhook pytest tests/ -q > /opt/case/build-tests.txt 2>&1
