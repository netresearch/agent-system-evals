#!/usr/bin/env bash
# Prove both matrix legs are resolvable from the warmed cache.
#
# The case asks for a result that runs on two TYPO3 lines. If the environment
# cannot resolve one of them even in principle, the case is asking for
# something impossible and every trial would score it as the agent's failure.
# So this runs at build time and fails the image, loudly, instead.
set -euo pipefail

LOCK="${1:?path to target.lock required}"
# shellcheck source=/dev/null
. "$LOCK"
# shellcheck source=/dev/null
. /usr/local/lib/matrix-lib.sh

for line in "$MATRIX_OLD" "$MATRIX_NEW"; do
    scratch="$(mktemp -d)"
    cp -a /app/. "$scratch/"
    # env_can_install, not pin_and_update: this asks whether the environment
    # could support the line at all, which requires rewriting the constraint
    # the target deliberately excludes. pin_and_update asks the opposite
    # question and belongs after a run, not here.
    if (cd "$scratch" && env_can_install "$line" --dry-run >/dev/null 2>&1); then
        echo "matrix leg TYPO3 ${line}: resolvable"
    else
        echo "TYPO3 ${line} does not resolve in this environment." >&2
        echo "The case cannot ask for a result that runs on it." >&2
        (cd "$scratch" && env_can_install "$line" --dry-run 2>&1 | tail -25) >&2
        rm -rf "$scratch"
        exit 1
    fi
    rm -rf "$scratch"
done
