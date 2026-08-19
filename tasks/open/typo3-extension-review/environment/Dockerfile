# PHP 8.3: within the target's declared TYPO3 v12.4 support window and new
# enough for the PHPUnit and PHPStan majors its dev dependencies allow.
FROM php:8.3-apache

ENV DEBIAN_FRONTEND=noninteractive \
    COMPOSER_ALLOW_SUPERUSER=1 \
    COMPOSER_NO_INTERACTION=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        git unzip libzip-dev libicu-dev default-mysql-client curl ca-certificates \
    && docker-php-ext-install -j"$(nproc)" ftp zip intl mysqli pdo_mysql \
    && rm -rf /var/lib/apt/lists/*

COPY --from=composer:2 /usr/bin/composer /usr/bin/composer

# The target declares ext-ftp and ext-zlib. zlib is compiled in; ftp is
# installed above. Verified at build time so a missing extension surfaces here
# rather than as an unexplained agent failure at run time.
RUN php -r 'exit((int) !(extension_loaded("ftp") && extension_loaded("zlib")));'

# target.lock is the single source of truth for what is under review. Harbor
# passes no build arguments, so the build reads the file rather than repeating
# its values here, where they could drift.
COPY target.lock target-composer.lock /tmp/target/
COPY prepare-target.sh /usr/local/bin/prepare-target
RUN chmod +x /usr/local/bin/prepare-target \
    && prepare-target /tmp/target/target.lock /app \
    # Build-time only. Left in the agent's PATH it carries the target
    # repository and the pinned commit — the case's provenance, which
    # scripts/agent-surface-audit reports as a leak and rightly so.
    && rm -f /usr/local/bin/prepare-target

# Environment readiness (ADR 0003): the commands a competent reviewer would
# reach for must work before the agent arrives. A failure here is a broken
# case, not a finding.
WORKDIR /app
RUN composer ci:test:php:lint \
    && .build/bin/phpstan --version \
    && .build/bin/phpunit --version \
    && .build/bin/php-cs-fixer --version \
    && make help


# Harbor collects everything written here.
# The Netresearch command-line toolchain, installed off the default PATH. Only
# a fleet that declares it in `env:` can reach it — an arm without it sees an
# image where these commands do not resolve, which is the state the comparison
# needs. Without this layer the nr-full fleet would carry a PATH pointing at a
# directory that does not exist: an arm labelled as the deployed stack, running
# with none of its tools and nothing failing anywhere.
COPY install-toolchain.sh /usr/local/bin/install-toolchain
RUN chmod +x /usr/local/bin/install-toolchain \
    && install-toolchain \
    && ! command -v rg > /dev/null \
    # Build-time only. Left in place it sits in the agent's PATH describing the
    # apparatus that is measuring it — scripts/agent-surface-audit reports it.
    && rm -f /usr/local/bin/install-toolchain


# --- the instance this case runs against -------------------------------------
#
# Every case starts from what a developer has: the repository checked out and a
# TYPO3 instance running with that extension installed. See
# environment/common/README.md. The heavy half happens here; `typo3 setup` and
# the rest need a database and run at container start.
ENV EXTENSION_DIR=/app
COPY target.lock /opt/case/
COPY build-instance.sh /usr/local/bin/build-instance
COPY install-instance.sh /usr/local/bin/install-instance
COPY ddev-shim.sh /usr/local/bin/ddev
COPY capability-probe.sh /opt/probe/capability-probe
RUN chmod +x /usr/local/bin/build-instance /usr/local/bin/install-instance \
        /usr/local/bin/ddev /opt/probe/capability-probe \
    && build-instance /opt/case/target.lock

# Served, not merely installed: an extension case that cannot issue a request
# cannot reproduce what a user reported, and a server that introspects a
# running application has nothing to introspect. The vhost matches the hostname
# target.lock declares; the hostname itself is set in docker-compose.yaml,
# because Docker rewrites /etc/hosts at container start.
RUN printf '%s\n' \
        '<VirtualHost *:80>' \
        '    ServerName v12.nr-sync.ddev.site' \
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
ENV DDEV_HOSTNAME=v12.nr-sync.ddev.site \
    DDEV_PRIMARY_URL=http://v12.nr-sync.ddev.site \
    IS_DDEV_PROJECT=true

RUN mkdir -p /logs/artifacts

# Build-time input only. Leaving it in the image would put the target's forge
# URL in front of the agent, which the network policy exists to keep out of
# reach.
RUN rm -rf /tmp/target

WORKDIR /app
