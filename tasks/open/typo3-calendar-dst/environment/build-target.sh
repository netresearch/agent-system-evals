#!/usr/bin/env bash
# Fetch the extension at the pinned pre-fix commit and install its test stack.
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

# This extension keeps its test stack in a SECOND composer tree under .Build/,
# which its own CI installs separately. Both need the TYPO3 installer plugins
# allowed: the repository declares no `allow-plugins`, so outside its usual
# environment composer refuses them and the install fails with a message that
# reads like a dependency conflict.
#
# `--no-security-blocking` because the pinned commit is from the TYPO3 v12
# line, and composer now refuses every `typo3/cms-core ^12.4` for published
# advisories. The image therefore ships known-vulnerable dependencies. That is
# acceptable here and nowhere else: the container has no network beyond the
# model endpoint, holds nothing but a public extension, and is destroyed with
# the trial. docs/case-lifecycle.md criterion 9 records the trade.
for tree in /app /app/.Build; do
  cd "$tree"
  composer config --no-plugins allow-plugins.typo3/cms-composer-installers true
  composer config --no-plugins allow-plugins.typo3/class-alias-loader true
  composer install --no-interaction --no-progress --no-security-blocking
done
cd /app

mkdir -p /app/typo3temp/var/tests/functional-sqlite-dbs

# The suite that is NOT this case's check must be green at the pinned commit,
# or a trial's result cannot be read.
typo3DatabaseDriver=pdo_sqlite .Build/vendor/bin/phpunit \
    -c .Build/phpunit/UnitTests.xml > /tmp/unit.log 2>&1 \
    || { echo "unit suite is not green at the pinned commit"; tail -20 /tmp/unit.log; exit 1; }

# The case's own test and its fixture must NOT be here — the verifier writes
# them after the agent has finished.
test ! -e /app/Tests/Functional/Service/CalendarServiceTest.php
test ! -e /app/Tests/Functional/Fixtures/events_calendarservice.csv
