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

EXTENSION_DIR=/extension

echo "=== fetching the extension at ${TARGET_COMMIT}"
mkdir -p "$EXTENSION_DIR"
cd "$EXTENSION_DIR"
git init -q .
git remote add origin "$TARGET_REPOSITORY"
git fetch -q --depth 1 origin "$TARGET_COMMIT"
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

echo "=== creating the TYPO3 ${TYPO3_LINE} project"
composer create-project "typo3/cms-base-distribution:^${TYPO3_LINE}" "$INSTANCE_DIR" \
    --no-interaction --no-progress --no-ansi

cd "$INSTANCE_DIR"
composer config policy.advisories.block false
composer config minimum-stability dev
composer config prefer-stable true
composer config repositories.local path "$EXTENSION_DIR"

echo "=== installing the extension from the local checkout"
composer require "${TARGET_PACKAGE}:*" --no-interaction --no-progress --no-ansi

echo "=== instance built at ${INSTANCE_DIR}, extension from ${EXTENSION_DIR}"
