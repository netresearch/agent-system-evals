#!/usr/bin/env bash
# Materialise the target at its pinned commit and prove the environment can
# produce the asked-for result before the agent arrives (ADR 0007): the module
# resolves, builds, vets and passes its own unit suite. A failure here is a
# broken case, never a trial.
set -euo pipefail

LOCK="${1:?target.lock}"
# shellcheck disable=SC1090
. "$LOCK"

# The commit and nothing else — no history past it, no tags, no remote. The
# first version of this script cloned the whole repository and checked the
# commit out, which left every later commit in .git: the fix this case exists
# to see written, its tests, its commit messages. The first recorded trial ran
# `git log --all --grep=…`, found both upstream fixes, and copied them. Same
# arrangement as the TYPO3 cases' build-instance.sh, for the same reason.
mkdir -p /app && cd /app
git init -q
git remote add origin "$TARGET_REPOSITORY"
git fetch -q --depth 1 --no-tags origin "$TARGET_COMMIT"
git checkout -q FETCH_HEAD
# Detach from the forge: the fix for the defect under investigation lives in
# this repository's future.
git remote remove origin
# A branch, so `git status` and `git diff HEAD` describe the agent's work
# against the pinned commit rather than a detached head.
git checkout -q -b work
test "$(git rev-parse HEAD)" = "$TARGET_COMMIT"
# Proved rather than assumed, because the failure is silent and the evidence
# it hands over is the answer.
test "$(git rev-list --all --count)" = "1"
test "$(git remote | wc -l)" = "0"

cd /app
# Every module the tests need, fetched now while the build has the network.
# At run time the proxy is allowlisted for anything the agent adds, and
# GOPROXY=off in the collectors makes a missing module fail loudly rather than
# hang against the egress policy.
go mod download all
go build ./...
go vet ./...
go test -short -count=1 -timeout 120s ./... > /opt/case/build-unit-tests.txt 2>&1
