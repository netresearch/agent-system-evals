#!/usr/bin/env bash
# Build everything the instance needs that does not require a database.
#
# The recipe is the target's own `ddev install-v13`, minus DDEV: a base
# distribution, a path repository pointing at the extension checkout, and
# `composer require`. See docs/adr/0006-runtime-fidelity.md.
#
# Splitting it this way keeps the expensive half in the image. What remains for
# container start is `typo3 setup`, `extension:setup`, the site file and the
# seed — seconds, not minutes.
set -euo pipefail

LOCK="${1:?path to target.lock required}"
# shellcheck source=/dev/null
. "$LOCK"

: "${TARGET_REPOSITORY:?}" "${TARGET_COMMIT:?}" "${TARGET_PACKAGE:?}"
: "${TYPO3_LINE:?}" "${INSTANCE_DIR:?}"

# Where the agent's copy of the extension lives. A case that already checks it
# out for its own reasons — a review works in /app — points this at that
# directory instead of getting a second copy, which would leave the agent
# choosing between two trees.
EXTENSION_DIR="${EXTENSION_DIR:-/extension}"

if [ -d "$EXTENSION_DIR/.git" ] \
    && [ "$(git -C "$EXTENSION_DIR" rev-parse HEAD)" = "$TARGET_COMMIT" ]; then
    echo "=== extension already checked out at ${TARGET_COMMIT}"
else
    echo "=== fetching the extension at ${TARGET_COMMIT}"
    mkdir -p "$EXTENSION_DIR"
    cd "$EXTENSION_DIR"
    git init -q .
    git remote add origin "$TARGET_REPOSITORY"
    # Depth 1 by default: a review or a diagnosis needs the tree, not the past,
    # and a shallow fetch keeps the build quick.
    #
    # A case may ask for the history instead, with TARGET_HISTORY=full. A
    # release task genuinely needs it — "what changed since the last version"
    # is not answerable from a single commit — and a developer preparing a
    # release has it. Never with tags: the remote's tags include the release
    # this case exists to see the agent produce, and fetching them would hand
    # over the answer along with the history.
    if [ "${TARGET_HISTORY:-shallow}" = "full" ]; then
        git fetch -q --no-tags origin "$TARGET_COMMIT"
    else
        git fetch -q --depth 1 --no-tags origin "$TARGET_COMMIT"
    fi
    git checkout -q FETCH_HEAD
    # Detach from the forge: the fix for the defect under investigation lives in
    # this repository's future.
    git remote remove origin
    git checkout -q -b main

    head="$(git rev-parse HEAD)"
    if [ "$head" != "$TARGET_COMMIT" ]; then
        echo "checked out $head, expected $TARGET_COMMIT" >&2
        exit 1
    fi
fi

echo "=== creating the TYPO3 ${TYPO3_LINE} project"
# --no-install, then configure, then install. Advisories published after the
# pinned commit must not decide whether a historical state can be built, and
# create-project resolves dependencies before any config of ours exists: on the
# 12.4 line it aborts outright, listing every core release as blocked. The
# target's own ddev install command splits it the same way.
composer create-project "typo3/cms-base-distribution:^${TYPO3_LINE}" "$INSTANCE_DIR" \
    --no-install --no-interaction --no-progress --no-ansi

cd "$INSTANCE_DIR"
composer config policy.advisories.block false
composer config minimum-stability dev
composer config prefer-stable true
composer config repositories.local path "$EXTENSION_DIR"

echo "=== installing the extension from the local checkout"
composer require "${TARGET_PACKAGE}:*" --no-interaction --no-progress --no-ansi

echo "=== instance built at ${INSTANCE_DIR}, extension from ${EXTENSION_DIR}"
