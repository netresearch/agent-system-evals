#!/usr/bin/env bash
# The command-line toolchain that belongs to the Netresearch engineering setup.
#
# Installed into /opt/nr-toolchain/bin, which is deliberately NOT on the default
# PATH. A fleet that claims this toolchain prepends the directory through
# `--agent-env PATH=…`; every other arm sees an image where these commands do
# not resolve. That is the point: a stack is its skills *and* its tools, and
# three of the skills in question — file-search, data-tools, cli-tools — are
# instructions for using exactly these binaries. Installing them everywhere
# would measure what the skills add when the tools are already there, which is
# a different question from the one this benchmark asks.
#
# Same arrangement as the companion's server binary: present in the image,
# reachable only by the arm that is given the way to it.
#
# Versions are pinned. An unpinned toolchain would change what a recorded
# result means without anything in the repository moving.
set -euo pipefail

BIN=/opt/nr-toolchain/bin
mkdir -p "$BIN"

RG_VERSION=15.2.0
FD_VERSION=v10.4.2
BAT_VERSION=v0.26.1
JQ_VERSION=jq-1.8.2
YQ_VERSION=v4.53.3
DASEL_VERSION=v3.11.2
AST_GREP_VERSION=0.45.1
SCC_VERSION=v3.7.0

# Everything is a static release binary placed inside $BIN. Nothing comes from
# apt, and that is the whole isolation: Debian's packages install into
# /usr/bin, which is on every arm's PATH, so `apt-get install ripgrep jq` would
# hand the tools to the control arm as well and dissolve the comparison. The
# first version of this script did exactly that; the assertion at the end of
# the Dockerfile layer is what refuses to let it happen again.
apt-get update
apt-get install -y --no-install-recommends unzip
rm -rf /var/lib/apt/lists/*

fetch_tar() {
    # $1 url, $2 path of the wanted file inside the archive
    curl -fsSL "$1" -o /tmp/tool.tar.gz
    tar -xzf /tmp/tool.tar.gz -C /tmp
    mv "/tmp/$2" "$BIN/"
    rm -f /tmp/tool.tar.gz
}

fetch_tar "https://github.com/BurntSushi/ripgrep/releases/download/${RG_VERSION}/ripgrep-${RG_VERSION}-x86_64-unknown-linux-musl.tar.gz" \
    "ripgrep-${RG_VERSION}-x86_64-unknown-linux-musl/rg"
fetch_tar "https://github.com/sharkdp/fd/releases/download/${FD_VERSION}/fd-${FD_VERSION}-x86_64-unknown-linux-musl.tar.gz" \
    "fd-${FD_VERSION}-x86_64-unknown-linux-musl/fd"
fetch_tar "https://github.com/sharkdp/bat/releases/download/${BAT_VERSION}/bat-${BAT_VERSION}-x86_64-unknown-linux-musl.tar.gz" \
    "bat-${BAT_VERSION}-x86_64-unknown-linux-musl/bat"

curl -fsSL "https://github.com/jqlang/jq/releases/download/${JQ_VERSION}/jq-linux-amd64" -o "$BIN/jq"
curl -fsSL "https://github.com/mikefarah/yq/releases/download/${YQ_VERSION}/yq_linux_amd64" -o "$BIN/yq"
curl -fsSL "https://github.com/TomWright/dasel/releases/download/${DASEL_VERSION}/dasel_linux_amd64" -o "$BIN/dasel"
chmod +x "$BIN/jq" "$BIN/yq" "$BIN/dasel"

curl -fsSL "https://github.com/ast-grep/ast-grep/releases/download/${AST_GREP_VERSION}/app-x86_64-unknown-linux-gnu.zip" \
    -o /tmp/ast-grep.zip
unzip -q -o /tmp/ast-grep.zip -d "$BIN"
rm /tmp/ast-grep.zip
chmod +x "$BIN"/ast-grep "$BIN"/sg 2>/dev/null || true

curl -fsSL "https://github.com/boyter/scc/releases/download/${SCC_VERSION}/scc_Linux_x86_64.tar.gz" \
    | tar -xz -C "$BIN" scc
chmod +x "$BIN"/rg "$BIN"/fd "$BIN"/bat "$BIN/scc"

# Not installed, and stated rather than left to be discovered: `mlr` (CSV) and
# `rga` (PDF and archive search) are named by these skills but have nothing to
# act on in a PHP extension with a database. `tokei` is named too and ships no
# release binaries at all — every one of its tags carries zero assets, so it
# would have to be built from source; `scc` answers the same question and is
# installed instead. If a case ever needs them, add
# them here — do not let a skill install them at run time, where the network
# allowlist would block it and the failure would be scored as agent behaviour.

# Every binary answers before the image is accepted. A toolchain that is
# present but broken is worse than one that is absent: the arm would look like
# a stack that does not help, when it is a stack that did not run.
# `dasel` v3 dropped `--version` in favour of a subcommand, which this check
# found on its first run — the kind of thing that would otherwise have shipped
# as a binary the agent cannot invoke.
for tool in rg fd bat jq yq ast-grep scc; do
    "$BIN/$tool" --version > /dev/null || {
        echo "toolchain: $tool does not run" >&2
        exit 1
    }
done
"$BIN/dasel" version > /dev/null || {
    echo "toolchain: dasel does not run" >&2
    exit 1
}

echo "toolchain installed: $(find "$BIN" -maxdepth 1 -type f -o -maxdepth 1 -type l | sort | xargs -n1 basename | tr '\n' ' ')"
