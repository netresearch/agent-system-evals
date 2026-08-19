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

# No agent CLI and no judge: a contract eval is graded mechanically, which is
# what makes it cheap enough to gate a merge. See ADR 0002.

# uv resolves and caches RewardKit at run time; test.sh pins the version.
COPY . /tests
WORKDIR /tests
