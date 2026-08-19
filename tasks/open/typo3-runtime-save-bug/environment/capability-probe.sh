#!/usr/bin/env bash
# Inventory of the tools, skills and MCP servers available in this container.
#
# Written before anything reads it, so that "the tool was not there" and "the
# tool was there and unused" can be told apart afterwards. Nothing here records
# or judges what was done with any of it.
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
# Every place a harness puts them, not just Claude Code's. Harbor copies
# skills to wherever the agent under test reads them — ~/.config/opencode/skills
# for OpenCode, the Claude config directory for Claude Code — and a probe that
# knows one location reports "nothing provisioned" for every other agent. That
# is the failure this file exists to prevent, one level up.
skill_count=0
skill_digest=""
found_dir=""
for skill_dir in \
        "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/skills" \
        "$HOME/.config/opencode/skills" \
        "$HOME/.codex/skills" \
        "$HOME/.gemini/skills" \
        "$HOME/.copilot/skills"; do
    [ -d "$skill_dir" ] || continue
    count="$(find "$skill_dir" -mindepth 1 -maxdepth 1 -type d | wc -l | tr -d ' ')"
    [ "$count" -gt 0 ] || continue
    skill_count="$count"
    found_dir="$skill_dir"
    skill_digest="$(find "$skill_dir" -name 'SKILL.md' -exec sha256sum {} + 2>/dev/null \
        | awk '{print $1}' | sort | sha256sum | cut -c1-16)"
    break
done

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
  "skills": {"count": $skill_count, "digest": "$skill_digest", "location": "$found_dir"},
  "mcp": {${mcp_entries}}
}
JSON

echo "capability inventory written to $OUT"
