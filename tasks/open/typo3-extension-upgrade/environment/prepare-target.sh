#!/usr/bin/env bash
# Fetch the pinned target and warm the dependency cache for both matrix legs.
#
# Runs at image build time, where the network is open. At run time the agent
# works under the allowlist in task.toml, which excludes the target's forge.
#
# Unlike the review case, this one cannot ship a pinned lock file: changing the
# version constraints *is* the task, so the agent has to be able to resolve
# dependencies it was not given. Blocking the forge would normally make that
# impossible, because Composer fetches package archives from it.
#
# So the cache is warmed here instead. Both legs are resolved once at build
# time, which leaves every archive the agent could need in the Composer cache;
# at run time it reads metadata from Packagist (allowed) and takes the archives
# from cache. The forge stays unreachable and the task stays solvable.
set -euo pipefail

LOCK="${1:?path to target.lock required}"
DEST="${2:-/app}"

# shellcheck source=/dev/null
. "$LOCK"

: "${TARGET_REPOSITORY:?missing from $LOCK}"
: "${TARGET_COMMIT:?missing from $LOCK}"
: "${MATRIX_OLD:?missing from $LOCK}"
: "${MATRIX_NEW:?missing from $LOCK}"

mkdir -p "$DEST"
cd "$DEST"

# One commit only. A full clone would carry the target's later history, which
# is this case's ground truth.
git init -q .
git remote add origin "$TARGET_REPOSITORY"
git fetch -q --depth 1 origin "$TARGET_COMMIT"
git checkout -q FETCH_HEAD
git remote remove origin
git checkout -q -b main

head="$(git rev-parse HEAD)"
if [ "$head" != "$TARGET_COMMIT" ]; then
    echo "checked out $head, expected $TARGET_COMMIT" >&2
    exit 1
fi

# Advisories published after the target commit must not decide whether a
# historical state can be built.
composer config policy.advisories.block false

# Warm the cache for both legs in a scratch copy, so /app is untouched.
#
# Uses the same pinning helper as the readiness check and the post-run outcome
# check. A separate implementation here would drift from them, and the first
# one did: it pinned a hard-coded subset of the TYPO3 packages, which resolves
# differently from pinning the set the manifest actually declares.
# shellcheck source=/dev/null
. /usr/local/lib/matrix-lib.sh

warm() {
    local line="$1"
    local scratch
    scratch="$(mktemp -d)"
    cp -a "$DEST/." "$scratch/"
    (
        cd "$scratch"
        echo "warming dependency cache for TYPO3 ${line}"
        # `|| true`: a leg that cannot resolve at build time is for the
        # readiness check to report, not a reason to abort the warm-up.
        env_can_install "$line" >/dev/null 2>&1 || true
    )
    rm -rf "$scratch"
}

warm "$MATRIX_OLD"
warm "$MATRIX_NEW"

# Install the target as it stands, so its own toolchain is runnable before the
# agent changes anything.
composer install --no-interaction --no-progress --no-ansi

# composer config wrote to composer.json. Restore it so the tree the agent
# starts from is the committed one.
git checkout -q -- composer.json

# Captured into a variable rather than piped into `grep -q`: a pipe lets grep
# exit on the first match, and the SIGPIPE that kills the writer is propagated
# by `pipefail`, so the check would report clean exactly when the tree is not.
dirty="$(git status --porcelain)"
if [ -n "$dirty" ]; then
    echo "working tree not clean after preparation:" >&2
    echo "$dirty" >&2
    exit 1
fi

echo "target prepared at $TARGET_COMMIT, cache warmed for $MATRIX_OLD and $MATRIX_NEW"
