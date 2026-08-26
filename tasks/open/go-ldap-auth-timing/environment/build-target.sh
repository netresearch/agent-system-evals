#!/usr/bin/env bash
# Materialise the target at its pinned commit and prove the environment can
# produce the asked-for result before the agent arrives (ADR 0007): the module
# resolves, builds, vets and passes its own unit suite. A failure here is a
# broken case, never a trial.
set -euo pipefail

LOCK="${1:?target.lock}"
# shellcheck disable=SC1090
. "$LOCK"

git clone -q "$TARGET_REPOSITORY" /app
git -C /app checkout -q "$TARGET_COMMIT"
# A branch, so `git status` and `git diff HEAD` describe the agent's work
# against the pinned commit rather than a detached head.
git -C /app checkout -q -b work
test "$(git -C /app rev-parse HEAD)" = "$TARGET_COMMIT"

cd /app
# Every module the tests need, fetched now while the build has the network.
# At run time the proxy is allowlisted for anything the agent adds, and
# GOPROXY=off in the collectors makes a missing module fail loudly rather than
# hang against the egress policy.
go mod download all
go build ./...
go vet ./...
go test -short -count=1 -timeout 120s ./... > /opt/case/build-unit-tests.txt 2>&1
