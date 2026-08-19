#!/usr/bin/env bash
# What the arm was actually given, measured before the agent is admitted.
#
# Two states that look identical in a result and are not the same thing at all:
#
#   the server was never registered, or its binary is missing → void run
#   the server answered and the agent did not call it        → measurement
#
# The second is one of the more interesting findings this benchmark has
# produced — fifteen trials in which no skill and no toolchain command was used
# although both were reachable. Reporting it as "possibly broken, do not use"
# would have thrown away the result.
#
# So provisioning is established here, deterministically, and usage is counted
# separately from the trajectory. This writes what was *provided*; nothing in
# it says anything about what the agent did with it.
#
# Output: /logs/artifacts/capability-inventory.json
set -euo pipefail

OUT="${1:-/logs/artifacts/capability-inventory.json}"
mkdir -p "$(dirname "$OUT")"

json_escape() { printf '%s' "$1" | sed 's/\\/\\\\/g; s/"/\\"/g'; }

# --- command-line tools -------------------------------------------------------
cli_entries=""
for tool in rg fd jq yq dasel ast-grep scc bat; do
    if path="$(command -v "$tool" 2>/dev/null)"; then
        version="$("$tool" --version 2>/dev/null | head -1 || true)"
        [ -n "$version" ] || version="$("$tool" version 2>/dev/null | head -1 || true)"
        entry="{\"present\":true,\"path\":\"$(json_escape "$path")\",\"version\":\"$(json_escape "$version")\"}"
    else
        entry='{"present":false}'
    fi
    cli_entries="$cli_entries,\"$tool\":$entry"
done
cli_entries="${cli_entries#,}"

# --- skills -------------------------------------------------------------------
# Harbor copies them into the agent's config directory. Counted and digested
# rather than listed in full: the point is whether they arrived intact.
skill_dir="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/skills"
skill_count=0
skill_digest=""
if [ -d "$skill_dir" ]; then
    skill_count="$(find "$skill_dir" -mindepth 1 -maxdepth 1 -type d | wc -l | tr -d ' ')"
    skill_digest="$(find "$skill_dir" -name 'SKILL.md' -exec sha256sum {} + 2>/dev/null \
        | awk '{print $1}' | sort | sha256sum | cut -c1-16)"
fi

# --- MCP servers --------------------------------------------------------------
# Asked to describe themselves over the protocol rather than assumed from the
# config: a config entry pointing at a missing binary looks identical to a
# working one until something calls it.
mcp_entries=""
for config in "${MCP_CONFIG:-}" /tmp/mcp.json; do
    [ -n "$config" ] && [ -f "$config" ] || continue
    # shellcheck disable=SC2086  # args is a pre-split argument list from the
    # MCP config and must word-split; quoting it would pass "devmcp:serve" and
    # any further argument as one.
    while IFS=$'\t' read -r name command args; do
        [ -n "$name" ] || continue
        reachable=false
        tool_count=0
        if [ -n "$command" ] && command -v "${command%% *}" > /dev/null 2>&1; then
            # initialize + tools/list over stdio, with a short deadline: a
            # server that does not answer promptly is not provisioned for
            # practical purposes either.
            response="$(printf '%s\n%s\n' \
                '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"probe","version":"1"}}}' \
                '{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}' \
                | timeout 60 "$command" ${args:+$args} 2>/dev/null || true)"
            if printf '%s' "$response" | grep -q '"result"'; then
                reachable=true
                tool_count="$(printf '%s' "$response" | grep -o '"name"' | wc -l | tr -d ' ')"
            fi
        fi
        mcp_entries="$mcp_entries,\"$(json_escape "$name")\":{\"configured\":true,\"reachable\":$reachable,\"tool_count\":$tool_count}"
    done < <(python3 - "$config" <<'PY' 2>/dev/null || true
import json, sys
try:
    servers = json.load(open(sys.argv[1])).get("mcpServers", {})
except Exception:
    servers = {}
for name, spec in servers.items():
    print(f"{name}\t{spec.get('command','')}\t{' '.join(spec.get('args') or [])}")
PY
)
done
mcp_entries="${mcp_entries#,}"

cat > "$OUT" <<JSON
{
  "cli": {$cli_entries},
  "skills": {"count": $skill_count, "digest": "$skill_digest"},
  "mcp": {${mcp_entries}}
}
JSON

echo "capability inventory written to $OUT"
