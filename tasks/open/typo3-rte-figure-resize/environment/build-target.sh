#!/usr/bin/env bash
# Fetch the extension at the pinned pre-fix commit and install its test stack.
#
# The checkout is deliberately history-free and remote-free. The fix for the
# defect this case reports exists in the public repository, and a trial that
# can reach it is not measuring what it claims to: the assertions below are the
# case's contamination gate, not decoration.
set -euo pipefail

# shellcheck disable=SC1091
. /tmp/target.lock

mkdir -p /app && cd /app
git init -q
git remote add origin "$TARGET_REPOSITORY"
git fetch -q --depth 1 --no-tags origin "$TARGET_COMMIT"
git checkout -q FETCH_HEAD
git remote remove origin
git checkout -q -b work

test "$(git rev-parse HEAD)" = "$TARGET_COMMIT"
test "$(git rev-list --all --count)" = "1"
test "$(git remote | wc -l)" = "0"

# The test stack, installed at build time so a trial spends no time on it and
# every arm starts from the same vendor tree. `--no-scripts` is not used: the
# TYPO3 extension installer is what puts the extension into .Build/ where the
# functional bootstrap expects to find it.
composer install --no-interaction --no-progress

# The functional suite writes its SQLite databases here.
mkdir -p /app/typo3temp/var/tests/functional-sqlite-dbs

# Proof the stack runs before any agent sees it: the suite that is NOT this
# case's check must pass at the pinned commit. A red unit suite here would make
# every trial's result unreadable.
typo3DatabaseDriver=pdo_sqlite .Build/bin/phpunit \
    -c Build/phpunit/UnitTests.xml --no-coverage > /tmp/unit.log 2>&1 \
    || { echo "unit suite is not green at the pinned commit"; tail -20 /tmp/unit.log; exit 1; }

# The case's own test file must NOT be here — the verifier stages it after the
# agent has finished. Present in the tree, it would hand over the expected
# output as a fixture.
test ! -e /app/Tests/Functional/Controller/FigureResizeWidthRenderingTest.php
