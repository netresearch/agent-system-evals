#!/usr/bin/env bash
# Fetch the pinned target and make its toolchain usable offline.
#
# Runs at image build time, where the network is available. At run time the
# agent works from what this produced, under the restricted allowlist in
# task.toml.
set -euo pipefail

LOCK="${1:?path to target.lock required}"
DEST="${2:-/app}"
LOCK_DIR="$(cd "$(dirname "$LOCK")" && pwd)"

# shellcheck source=/dev/null
. "$LOCK"

: "${TARGET_REPOSITORY:?TARGET_REPOSITORY missing from $LOCK}"
: "${TARGET_COMMIT:?TARGET_COMMIT missing from $LOCK}"

mkdir -p "$DEST"
cd "$DEST"

# Fetch exactly one commit. A full clone would carry the target's later
# history, which is the verifier's ground truth.
git init -q .
git remote add origin "$TARGET_REPOSITORY"
git fetch -q --depth 1 origin "$TARGET_COMMIT"
git checkout -q FETCH_HEAD

# Detach from the forge. The agent still sees a normal working tree with a
# normal git history; it cannot fetch the target's future.
git remote remove origin
git checkout -q -b main

head="$(git rev-parse HEAD)"
if [ "$head" != "$TARGET_COMMIT" ]; then
    echo "checked out $head, expected $TARGET_COMMIT" >&2
    exit 1
fi

# Install the project's own toolchain so the checks it ships with can actually
# be run. An environment where the obvious command fails would measure the
# environment, not the agent.
#
# The target is a library and ships no composer.lock, so an unpinned install
# would resolve differently on every build — and would fail outright today,
# because advisories published since the target commit block the versions it
# would otherwise select. The lock is generated once by
# scripts/refresh-target-lock, reviewed, and committed to the case.
#
# It is copied in for the install and removed again below, so the agent sees
# the target exactly as its authors left it.
test -f "$LOCK_DIR/target-composer.lock" || {
    echo "missing target-composer.lock; run scripts/refresh-target-lock" >&2
    exit 1
}
cp "$LOCK_DIR/target-composer.lock" "$DEST/composer.lock"
composer config policy.advisories.block false
# `--no-audit` is an `update` option only; blocking is already off via the
# policy set above.
composer install --no-interaction --no-progress --no-ansi
rm -f "$DEST/composer.lock"

# composer config wrote to composer.json. Restore it so the tree the agent
# reviews is the committed one, not one this script edited.
git checkout -q -- composer.json

# Leave the tree clean: a dirty baseline would make the verifier's git evidence
# meaningless. Captured into a variable rather than piped into `grep -q` — a
# pipe lets grep exit on the first match, and the SIGPIPE that kills the writer
# is propagated by `pipefail`, so the check would report clean precisely when
# the tree is dirty.
dirty="$(git status --porcelain)"
if [ -n "$dirty" ]; then
    echo "working tree not clean after preparation:" >&2
    echo "$dirty" >&2
    exit 1
fi

echo "target prepared at $TARGET_COMMIT"
