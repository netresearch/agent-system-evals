# Go library case: the module at its pinned commit, with the toolchain its
# go.mod names and an OpenLDAP beside it (docker-compose.yaml) so the
# project's own integration suite is one command away — which is what a
# developer working on this library has (ADR 0006).
#
# go.mod declares `go 1.26.0` and `toolchain go1.27.0`. The image carries
# 1.27.0 and GOTOOLCHAIN=local, so nothing tries to download a toolchain at
# run time behind the egress allowlist and fails in a way that reads as a
# broken module.
FROM golang:1.27-bookworm

ENV DEBIAN_FRONTEND=noninteractive \
    GOTOOLCHAIN=local \
    CGO_ENABLED=0

# ldap-utils for the environment healthcheck: the directory has to answer a
# bind before the agent starts, and ldapsearch is the plain way to ask.
RUN apt-get update && apt-get install -y --no-install-recommends \
        git ca-certificates curl ldap-utils \
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
