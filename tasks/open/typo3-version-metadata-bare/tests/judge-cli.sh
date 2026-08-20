#!/usr/bin/env bash
# Transparent wrapper around the Claude Code CLI, installed as `claude` so that
# RewardKit picks it up from PATH.
#
# It exists because of how a failing judge is reported. RewardKit raises
# `Agent CLI 'claude' exited with code N: <stdout[:200]>`, and the CLI's error
# envelope puts `result` — the only field that says what actually went wrong —
# far past character 200. The visible part is `{"is_error":true,...}` plus
# timing fields, which names the failure without describing it. One judge
# failure aborts the whole reward run, so that truncated string is all the
# evidence left for a discarded trial.
#
# The wrapper changes nothing: same argv, same stdout, same stderr, same exit
# status. It only keeps a full copy on disk beside the other verifier
# artifacts, so the next failure can be read rather than reproduced.
#
# No pipes: `cmd | tee` would put the CLI's exit status behind tee's, and
# `grep -q` style early exits in a pipeline invert results under `pipefail`.
# Capture to files, replay, exit with the recorded status.

REAL_CLI=/root/.local/bin/claude-real
# Flat files directly in /logs/verifier, not a subdirectory: Harbor copies back
# the files it finds there and does not descend, so a tidy `judge-cli/` folder
# is written inside the container and then lost with it.
LOG_DIR=/logs/verifier

if [ ! -d "$LOG_DIR" ] || [ ! -w "$LOG_DIR" ]; then
    # No writable log directory is not a reason to fail a verification run.
    exec "$REAL_CLI" "$@"
fi

# Nanosecond stamp plus PID: judges run concurrently and two calls in the same
# second must not overwrite each other's evidence.
stamp="$(date +%s%N)-$$"
out="$LOG_DIR/judge-cli-$stamp.stdout"
err="$LOG_DIR/judge-cli-$stamp.stderr"

# argv, minus the prompt itself: it carries the criterion text and would bury
# the flags that decide whether the call was well-formed.
{
    printf 'argv:'
    for arg in "$@"; do
        case "$arg" in
            -*) printf ' %s' "$arg" ;;
            *)  printf ' <%s chars>' "${#arg}" ;;
        esac
    done
    printf '\ncwd: %s\n' "$PWD"
} > "$LOG_DIR/judge-cli-$stamp.argv"

"$REAL_CLI" "$@" > "$out" 2> "$err"
rc=$?

cat "$out"
cat "$err" >&2
exit "$rc"
