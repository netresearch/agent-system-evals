# Python scripts case: an organisation-maintenance repository at its pinned
# commit, on the interpreter its CI uses, with its test dependencies installed
# from its own hash-pinned list.
#
# No service beside it: the script under review talks to the GitHub API, and
# the case is about what the script does when that API says no. The verifier
# stands in for the API; nothing here reaches it.
FROM python:3.14-slim-bookworm

ENV DEBIAN_FRONTEND=noninteractive \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

COPY capability-probe.sh /opt/probe/capability-probe
COPY target.lock /opt/case/
COPY build-target.sh /usr/local/bin/build-target
RUN chmod +x /opt/probe/capability-probe /usr/local/bin/build-target \
    && build-target /opt/case/target.lock

# The Netresearch command-line toolchain, installed off the default PATH. Only
# a fleet that declares it in `env:` can reach it; see the script's header and
# fleets/nr-full.yaml. An arm without it sees an image where these commands do
# not resolve, which is the state the comparison needs.
COPY install-toolchain.sh /usr/local/bin/install-toolchain
RUN chmod +x /usr/local/bin/install-toolchain \
    && install-toolchain \
    && ! command -v rg > /dev/null \
    && rm -f /usr/local/bin/install-toolchain

RUN mkdir -p /logs/artifacts

WORKDIR /app
