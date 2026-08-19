# PHP 8.3. Both matrix legs declare `php ^8.2` — checked against Packagist
# rather than assumed, because a wrong floor here would silently make one leg
# unresolvable and look like an agent failure.
FROM php:8.3-apache

ENV DEBIAN_FRONTEND=noninteractive \
    COMPOSER_ALLOW_SUPERUSER=1 \
    COMPOSER_NO_INTERACTION=1 \
    COMPOSER_HOME=/composer

RUN apt-get update && apt-get install -y --no-install-recommends \
        git unzip libzip-dev libicu-dev libsqlite3-dev \
    && docker-php-ext-install -j"$(nproc)" zip intl pdo pdo_sqlite mysqli pdo_mysql \
    && rm -rf /var/lib/apt/lists/*

COPY --from=composer:2 /usr/bin/composer /usr/bin/composer

# The target declares ext-pdo. Verified at build time so a missing extension
# surfaces here rather than as an unexplained failure at run time.
RUN php -r 'exit((int) !(extension_loaded("pdo") && extension_loaded("intl")));'

# Copied before preparation: the same pinning logic warms the cache here and
# checks the outcome after a run, and two implementations of it would drift.
COPY matrix-lib.sh /usr/local/lib/matrix-lib.sh
COPY target.lock /tmp/target/target.lock
COPY prepare-target.sh /usr/local/bin/prepare-target
RUN chmod +x /usr/local/bin/prepare-target && prepare-target /tmp/target/target.lock /app

# Environment readiness (ADR 0003): the commands a competent developer would
# reach for must work before the agent arrives. A failure here is a broken
# case, not a finding.
# Checked through the project's own binaries at their real location. This
# repository uses Composer's default vendor/bin — an earlier version assumed
# the .build/bin layout of a sibling extension and failed the build with
# "not found", which is the correct outcome for a wrong assumption but a poor
# use of a build minute.
WORKDIR /app
RUN vendor/bin/phpstan --version \
    && vendor/bin/phpunit --version \
    && vendor/bin/php-cs-fixer --version \
    && make help >/dev/null \
    && composer ci:test:php:unit >/dev/null

# Both legs must be resolvable from the warmed cache before the agent starts.
# If a leg cannot resolve here, the case cannot ask for it — that is a broken
# environment, and it must fail loudly at build rather than be scored as the
# agent's failure.
COPY check-matrix.sh /usr/local/bin/check-matrix
RUN chmod +x /usr/local/bin/check-matrix && check-matrix /tmp/target/target.lock

# Used by the verifier's collect hooks after the agent stops, to run the tree
# the agent left against each line of the matrix.
COPY run-matrix-leg.sh /usr/local/bin/run-matrix-leg
RUN chmod +x /usr/local/bin/run-matrix-leg

# The Netresearch command-line toolchain, installed off the default PATH. Only
# a fleet that declares it in `env:` can reach it. Without this layer the
# nr-full fleet would carry a PATH pointing at a directory that does not exist,
# and a missing PATH entry is not an error anywhere: the arm would be labelled
# as the deployed stack and run with none of its tools.
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
# Verified here rather than discovered during `typo3 setup`, which answers a
# missing driver with "The connection type \"mysqli\" does not exist" and then
# lists mysqli among the valid ones — a message that points at the argument
# instead of at the absent extension.
RUN php -r 'exit((int) !(extension_loaded("mysqli") && extension_loaded("intl")));'

ENV EXTENSION_DIR=/app
COPY target.lock /opt/case/
COPY build-instance.sh /usr/local/bin/build-instance
COPY install-instance.sh /usr/local/bin/install-instance
COPY ddev-shim.sh /usr/local/bin/ddev
COPY capability-probe.sh /usr/local/bin/capability-probe
RUN chmod +x /usr/local/bin/build-instance /usr/local/bin/install-instance \
        /usr/local/bin/ddev /usr/local/bin/capability-probe \
    && build-instance /opt/case/target.lock

# Served, not merely installed: an extension case that cannot issue a request
# cannot reproduce what a user reported, and a server that introspects a
# running application has nothing to introspect. The vhost matches the hostname
# target.lock declares; the hostname itself is set in docker-compose.yaml,
# because Docker rewrites /etc/hosts at container start.
RUN printf '%s\n' \
        '<VirtualHost *:80>' \
        '    ServerName v13.contexts.ddev.site' \
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
ENV DDEV_HOSTNAME=v13.contexts.ddev.site \
    DDEV_PRIMARY_URL=http://v13.contexts.ddev.site \
    IS_DDEV_PROJECT=true


RUN mkdir -p /logs/artifacts

# Build-time input only. Leaving it in the image would put the target's forge
# URL in front of the agent, which the network policy exists to keep out.
RUN rm -rf /tmp/target

WORKDIR /app
