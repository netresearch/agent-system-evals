# PHP 8.3: within the target's declared TYPO3 v12.4 support window and new
# enough for the PHPUnit and PHPStan majors its dev dependencies allow.
FROM php:8.3-cli

ENV DEBIAN_FRONTEND=noninteractive \
    COMPOSER_ALLOW_SUPERUSER=1 \
    COMPOSER_NO_INTERACTION=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        git unzip libzip-dev libicu-dev \
    && docker-php-ext-install -j"$(nproc)" ftp zip intl \
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
RUN chmod +x /usr/local/bin/prepare-target && prepare-target /tmp/target/target.lock /app

# Environment readiness (ADR 0003): the commands a competent reviewer would
# reach for must work before the agent arrives. A failure here is a broken
# case, not a finding.
WORKDIR /app
RUN composer ci:test:php:lint \
    && .build/bin/phpstan --version \
    && .build/bin/phpunit --version \
    && .build/bin/php-cs-fixer --version \
    && make help

# The TYPO3 Dev Companion server, for the fleets that register it.
#
# It is a PHP process the client launches over stdio, so it has to be inside the
# container; only the MCP config that points at it varies per fleet. That means
# the code sits in the image for every fleet, including the ones that do not use
# it — a small confound, stated here and in fleets/companion.yaml rather than
# hidden. Nothing registers it, no skill mentions it, and no path leads to it
# from /app.
#
# Pinned by commit because the project asks for it: a 0.x package whose surface
# is explicitly not settled.
ARG COMPANION_REF=845c0c633ae921962387f38b8e941ede4d26d1a3
RUN git clone -q https://github.com/TYPO3/dev-companion.git /opt/typo3-dev-companion \
    && git -C /opt/typo3-dev-companion checkout -q "$COMPANION_REF" \
    && cd /opt/typo3-dev-companion \
    && composer install --no-interaction --no-progress --no-ansi --quiet \
    && php /opt/typo3-dev-companion/bin/typo3-dev-companion help >/dev/null

# Harbor collects everything written here.
RUN mkdir -p /logs/artifacts

# Build-time input only. Leaving it in the image would put the target's forge
# URL in front of the agent, which the network policy exists to keep out of
# reach.
RUN rm -rf /tmp/target

WORKDIR /app
