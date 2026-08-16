#!/usr/bin/env bash
# Run the tree the agent left against one TYPO3 line.
#
# The outcome of a writing task is not in the trajectory, it is in the tree the
# agent left. This pins a copy of that tree to one line of the matrix, installs
# it, runs the project's own unit suite, and prints a machine-readable verdict
# the rubric reads.
#
# Runs in a scratch copy. Testing in /app would mutate the very state the rubric
# inspects — the diff would then include this script's installs, and scope
# discipline, which is one of the things most worth measuring in a writing task,
# would be unmeasurable.
#
# Never exits non-zero for a failing leg. A failed leg is a finding; a collect
# hook that fails takes the evidence down with it.
set -uo pipefail

LINE="${1:?usage: run-matrix-leg <typo3-line>}"
# shellcheck source=/dev/null
. /usr/local/lib/matrix-lib.sh

SCRATCH="$(mktemp -d)"
trap 'rm -rf "$SCRATCH"' EXIT

cp -a /app/. "$SCRATCH/" 2>/dev/null
cd "$SCRATCH" || { echo "LEG=$LINE RESOLVE=error TESTS=skipped INSTALLED=?"; exit 0; }

echo "--- declared TYPO3 packages: $(typo3_packages composer.json)"
echo "--- pinning to ^${LINE}"

if pin_and_update "$LINE" >"$SCRATCH/update.log" 2>&1; then
    resolve=ok
else
    resolve=failed
fi
echo "--- resolve: $resolve"
tail -30 "$SCRATCH/update.log" 2>/dev/null

if [ "$resolve" != "ok" ]; then
    echo "LEG=$LINE RESOLVE=failed TESTS=skipped INSTALLED=none"
    exit 0
fi

installed="$(installed_version typo3/cms-core)"
echo "--- installed typo3/cms-core: $installed"

echo "--- unit tests"
if composer ci:test:php:unit >"$SCRATCH/tests.log" 2>&1; then
    tests=passed
else
    tests=failed
fi
tail -40 "$SCRATCH/tests.log" 2>/dev/null

# One line the rubric parses. Everything above it is context for a human.
echo "LEG=$LINE RESOLVE=$resolve TESTS=$tests INSTALLED=$installed"
