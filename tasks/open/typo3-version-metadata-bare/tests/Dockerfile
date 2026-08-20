# Verifier image.
#
# Harbor uses the tests/ directory itself as this image's build context and
# expects the verifier to find its files at /tests. Setting
# `[verifier.environment] docker_image` instead skips the build entirely, so
# nothing is ever copied in and the run fails with
# `bash: /tests/test.sh: No such file or directory` — which describes the
# symptom and not the cause. Measured, not assumed.
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim@sha256:e5b65587bce7de595f299855d7385fe7fca39b8a74baa261ba1b7147afa78e58

RUN apt-get update && apt-get install -y --no-install-recommends \
        curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# The judge runs through the Claude Code CLI rather than through direct API
# calls. A subscription token is scoped for the CLI session, and LiteLLM's
# direct calls with it are rate-limited hard enough that judging is not
# possible: eight dimensions failed at concurrency 8, and one still failed at
# concurrency 1. The CLI is the authenticated path that subscription actually
# grants.
#
# Installed at build time on purpose. The verifier's run-time allowlist does
# not include claude.ai, so an install during the run would fail — and it
# should not be reaching out mid-verification anyway.
#
# The versioned binary, fetched directly and checked against the SHA-256 the
# release manifest publishes for it. `curl -fsSL https://claude.ai/install.sh |
# bash` — what stood here — always installs whatever is newest, so the judge's
# own binary was the one part of a recorded result that could not be
# reconstructed, in a repository whose lock file says a version change
# invalidates comparison with earlier runs. Two jobs a week apart could have
# been judged by different software with nothing recording it.
#
# (The installer was never as unverified as it looks: it checks the binary
# against the same manifest. What it does not do is let you choose which
# version you get.)
ARG CLAUDE_CODE_VERSION=2.1.237
ARG CLAUDE_CODE_SHA256=73975167f0108693cf6fd6614994781657ebb8456ebef5d247458734abfb3916
# `mkdir` first: the installer used to create this directory as a side effect,
# and without it curl fails with exit 23 — "failed writing body", which reads
# like a network problem and is a missing directory.
RUN mkdir -p /root/.local/bin \
    && curl -fsSL \
        "https://downloads.claude.ai/claude-code-releases/${CLAUDE_CODE_VERSION}/linux-x64/claude" \
        -o /root/.local/bin/claude-real \
    && echo "${CLAUDE_CODE_SHA256}  /root/.local/bin/claude-real" | sha256sum -c - \
    && chmod +x /root/.local/bin/claude-real \
    && test "$(/root/.local/bin/claude-real --version | cut -d" " -f1)" = "${CLAUDE_CODE_VERSION}"

# A wrapper around the CLI rather than the CLI itself, so a failing judge
# leaves a readable error behind: RewardKit truncates the CLI's error envelope
# at 200 characters, which stops before the field naming what went wrong.
#
# It has to take the place of the real binary in /root/.local/bin. test.sh puts
# that directory at the front of PATH, so a wrapper installed anywhere else is
# shadowed and silently never runs — which is how the first version of this
# failed: the image built, the judges ran, and no log appeared.
COPY judge-cli.sh /root/.local/bin/claude
RUN chmod +x /root/.local/bin/claude \
    && ln -sf /root/.local/bin/claude /usr/local/bin/claude \
    && claude --version

# uv resolves and caches RewardKit at run time; test.sh pins the version.
COPY . /tests
WORKDIR /tests
