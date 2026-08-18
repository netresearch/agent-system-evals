# Runtime case: a TYPO3 instance with the extension under test installed.
#
# Everything that does not need a database happens here — the project skeleton,
# the extension, the vendor tree. The installation itself runs at container
# start (see docker-compose.yaml), because it needs the database and the
# database only exists once Compose is up.
FROM php:8.3-cli

ENV DEBIAN_FRONTEND=noninteractive \
    COMPOSER_ALLOW_SUPERUSER=1 \
    COMPOSER_NO_INTERACTION=1 \
    COMPOSER_HOME=/composer

RUN apt-get update && apt-get install -y --no-install-recommends \
        git unzip libzip-dev libicu-dev libpng-dev libjpeg-dev libfreetype6-dev \
        default-mysql-client \
    && docker-php-ext-configure gd --with-jpeg --with-freetype \
    && docker-php-ext-install -j"$(nproc)" zip intl mysqli pdo_mysql gd \
    && rm -rf /var/lib/apt/lists/*

COPY --from=composer:2 /usr/bin/composer /usr/bin/composer

# TYPO3 needs mysqli for the connection this case configures, and intl and gd
# for a working installation. Verified at build time so a missing extension
# surfaces here rather than as an unexplained failure at run time.
RUN php -r 'exit((int) !(extension_loaded("mysqli") && extension_loaded("intl") && extension_loaded("gd")));'

# The client refuses to connect without TLS against this server, which the
# target's own DDEV setup does not do. Left alone it would cost an agent turns
# on an artefact of this environment rather than on the case.
RUN printf '[client]\nskip-ssl\n' > /etc/mysql/conf.d/benchmark.cnf 2>/dev/null \
    || { mkdir -p /etc/mysql/conf.d && printf '[client]\nskip-ssl\n' > /etc/mysql/conf.d/benchmark.cnf; }

COPY target.lock seed-reported-state.php /opt/case/
COPY install-instance.sh /usr/local/bin/install-instance
COPY build-instance.sh /usr/local/bin/build-instance
RUN chmod +x /usr/local/bin/install-instance /usr/local/bin/build-instance \
    && build-instance /opt/case/target.lock

# Environment readiness (ADR 0003): before the agent arrives, the instance must
# be one command away from running. A failure here is a broken case.
WORKDIR /instance
RUN test -x vendor/bin/typo3 \
    && vendor/bin/typo3 --version \
    && test -d vendor/netresearch/nr-textdb \
    && composer show netresearch/nr-textdb >/dev/null

# The TYPO3 Dev Companion's MCP server, for the fleets that use it. It is a PHP
# process the client launches over stdio, so it has to live inside the
# container; only the MCP config that points at it varies per fleet. The code
# therefore sits in the image for every fleet, including the ones that never
# reach it — the same small confound the review case states, kept identical here
# so the two cases are read the same way. Nothing registers it, no skill
# mentions it, and no path leads to it from the instance.
#
# Without this the companion fleets would receive their skills and an MCP config
# pointing at a file that does not exist: an arm that looks like "companion" and
# measures companion-skills-without-a-server. `scripts/run-evaluation` counts
# `typo3_` tool calls per trial for exactly that reason.
ARG COMPANION_REF=845c0c633ae921962387f38b8e941ede4d26d1a3
RUN git clone -q https://github.com/TYPO3/dev-companion.git /opt/typo3-dev-companion \
    && git -C /opt/typo3-dev-companion checkout -q "$COMPANION_REF" \
    && cd /opt/typo3-dev-companion \
    && composer install --no-interaction --no-progress --no-ansi --quiet \
    && php /opt/typo3-dev-companion/bin/typo3-dev-companion help >/dev/null

# balatD/typo3-dev-mcp, for the fleet that uses it. Unlike the companion this
# is a TYPO3 extension: it answers by querying the booted instance, so it has
# to be installed *into* the instance rather than beside it, and it is
# therefore present in the instance for every fleet — only the MCP config that
# registers its server varies. `extension:setup` at container start activates
# it along with everything else.
#
# What that costs in fidelity is bounded and worth stating: the package ships
# no TCA, no ext_tables.sql and no ext_localconf.php, so the data model, the
# schema and the request chain of the instance under diagnosis are unchanged.
# What every arm does see is one additional dev extension in the extension
# list. Keeping it out of the other arms would be worse — then the fleets would
# differ by the instance as well as by the tooling.
ARG DEV_MCP_VERSION=v0.1.0-alpha.8
RUN composer require --dev --no-interaction --no-progress --no-ansi \
        "balatd/typo3-dev-mcp:$DEV_MCP_VERSION" \
    && test -f /instance/vendor/balatd/typo3-dev-mcp/composer.json

# The Netresearch command-line toolchain, installed off the default PATH. Only
# a fleet that declares it in `env:` can reach it; see the script's header and
# fleets/nr-full.yaml. An arm without it sees an image where these commands do
# not resolve, which is the state the comparison needs.
COPY install-toolchain.sh /usr/local/bin/install-toolchain
RUN chmod +x /usr/local/bin/install-toolchain \
    && install-toolchain \
    && ! command -v rg > /dev/null

RUN mkdir -p /logs/artifacts

WORKDIR /instance
