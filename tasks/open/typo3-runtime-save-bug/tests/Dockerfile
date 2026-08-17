# Verifier image.
#
# Harbor uses the tests/ directory itself as this image's build context and
# expects the verifier to find its files at /tests. Setting
# `[verifier.environment] docker_image` instead skips the build entirely, so
# nothing is ever copied in and the run fails with
# `bash: /tests/test.sh: No such file or directory` — which describes the
# symptom and not the cause. Measured, not assumed.
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

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
RUN curl -fsSL https://claude.ai/install.sh | bash \
    && ln -sf /root/.local/bin/claude /usr/local/bin/claude \
    && claude --version

# uv resolves and caches RewardKit at run time; test.sh pins the version.
COPY . /tests
WORKDIR /tests
