# PHP 8.3. Both matrix legs declare `php ^8.2` — checked against Packagist
# rather than assumed, because a wrong floor here would silently make one leg
# unresolvable and look like an agent failure.
FROM php:8.3-cli

ENV DEBIAN_FRONTEND=noninteractive \
    COMPOSER_ALLOW_SUPERUSER=1 \
    COMPOSER_NO_INTERACTION=1 \
    COMPOSER_HOME=/composer

RUN apt-get update && apt-get install -y --no-install-recommends \
        git unzip libzip-dev libicu-dev libsqlite3-dev \
    && docker-php-ext-install -j"$(nproc)" zip intl pdo pdo_sqlite \
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

RUN mkdir -p /logs/artifacts

# Build-time input only. Leaving it in the image would put the target's forge
# URL in front of the agent, which the network policy exists to keep out.
RUN rm -rf /tmp/target

WORKDIR /app
