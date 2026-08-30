# Metadata case: a TYPO3 instance with the extension under test installed,
# reachable over HTTP the way a developer's own instance is.
#
# Everything that does not need a database happens here — the project skeleton,
# the extension, the vendor tree. The installation itself runs at container
# start (see docker-compose.yaml), because it needs the database and the
# database only exists once Compose is up.
#
# Apache rather than the CLI image, because the case is about a backend module.
# Without a web server the reported behaviour cannot be triggered at all, only
# described: the earlier version of this environment had to seed the damaged
# rows because clicking Save was impossible. The target's own .ddev/config.yaml
# specifies apache-fpm, so this follows it.
FROM php:8.5-apache

ENV DEBIAN_FRONTEND=noninteractive \
    COMPOSER_ALLOW_SUPERUSER=1 \
    COMPOSER_NO_INTERACTION=1 \
    COMPOSER_HOME=/composer

RUN apt-get update && apt-get install -y --no-install-recommends \
        git unzip libzip-dev libicu-dev libpng-dev libjpeg-dev libfreetype6-dev \
        default-mysql-client curl ca-certificates \
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

# The DDEV-compatible surface. Not DDEV: DDEV drives Docker, and a trial is
# already inside a container — running it here would mean handing the agent the
# host's Docker socket. What a developer's DDEV gives the agent is a served
# instance under a known hostname and a `ddev` command for reaching into it,
# and that is what this reproduces. Stated as a compatible surface, never as
# the real thing; see README.md.
#
# The hostname is the target's own, from .ddev/config.yaml.
ENV DDEV_HOSTNAME=v14.nr-xliff-streaming.ddev.site \
    DDEV_PRIMARY_URL=http://v14.nr-xliff-streaming.ddev.site \
    IS_DDEV_PROJECT=true
# The hostname itself is set in docker-compose.yaml via extra_hosts, not here:
# Docker rewrites /etc/hosts at container start, so a build-time entry is
# silently discarded.
RUN printf '%s\n' \
        '<VirtualHost *:80>' \
        '    ServerName v14.nr-xliff-streaming.ddev.site' \
        '    ServerAlias localhost' \
        '    DocumentRoot /instance/public' \
        '    <Directory /instance/public>' \
        '        AllowOverride All' \
        '        Require all granted' \
        '    </Directory>' \
        '    ErrorLog /var/log/apache2/typo3-error.log' \
        '    CustomLog /var/log/apache2/typo3-access.log combined' \
        '</VirtualHost>' \

        > /etc/apache2/sites-available/000-default.conf \
    && a2enmod rewrite > /dev/null

COPY ddev-shim.sh /usr/local/bin/ddev
COPY capability-probe.sh /opt/probe/capability-probe
RUN chmod +x /usr/local/bin/ddev

ENV EXTENSION_DIR=/app
COPY target.lock /opt/case/
COPY install-instance.sh /usr/local/bin/install-instance
COPY build-instance.sh /usr/local/bin/build-instance
RUN chmod +x /usr/local/bin/install-instance /usr/local/bin/build-instance \
        /opt/probe/capability-probe \
    && build-instance /opt/case/target.lock

# Environment readiness (ADR 0003): before the agent arrives, the instance must
# be one command away from running. A failure here is a broken case.
WORKDIR /instance
RUN test -x vendor/bin/typo3 \
    && vendor/bin/typo3 --version \
    && test -d vendor/netresearch/nr-xliff-streaming \
    && composer show netresearch/nr-xliff-streaming >/dev/null

# The Netresearch command-line toolchain, installed off the default PATH. Only
# a fleet that declares it in `env:` can reach it; see the script's header and
# fleets/nr-full.yaml. An arm without it sees an image where these commands do
# not resolve, which is the state the comparison needs.
COPY install-toolchain.sh /usr/local/bin/install-toolchain
RUN chmod +x /usr/local/bin/install-toolchain \
    && install-toolchain \
    && ! command -v rg > /dev/null \
    # Build-time only. Left in place it sits in the agent's PATH describing the
    # apparatus that is measuring it — scripts/agent-surface-audit reports it.
    && rm -f /usr/local/bin/install-toolchain

RUN mkdir -p /logs/artifacts

WORKDIR /instance
