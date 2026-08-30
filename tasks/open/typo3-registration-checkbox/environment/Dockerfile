# A third-party TYPO3 extension at the commit before a reported validation
# defect was fixed, with its test stack installed and ready to run.
#
# No web server and no database service: the defect is reachable through the
# extension's own functional stack on SQLite, which is where the check runs.
# The cost of that choice is stated in the sibling case's Dockerfile and holds
# here too — an agent that would have clicked through a calendar cannot.
FROM php:8.2-cli

ENV DEBIAN_FRONTEND=noninteractive \
    COMPOSER_ALLOW_SUPERUSER=1 \
    COMPOSER_NO_INTERACTION=1 \
    COMPOSER_HOME=/composer

# Pinned, though this case's defect does not depend on it. A sibling case's
# did, and its check could not have failed under UTC — see
# docs/case-lifecycle.md criterion 8. Pinning costs nothing and removes a class
# of silent pass.
ENV TZ=Europe/Berlin

RUN apt-get update && apt-get install -y --no-install-recommends \
        git unzip libzip-dev libicu-dev libsqlite3-dev ca-certificates tzdata \
    && docker-php-ext-install -j"$(nproc)" zip intl pdo_sqlite \
    && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo "$TZ" > /etc/timezone \
    && printf 'date.timezone=%s\n' "$TZ" > /usr/local/etc/php/conf.d/timezone.ini \
    && rm -rf /var/lib/apt/lists/*

COPY --from=composer:2 /usr/bin/composer /usr/bin/composer

COPY target.lock /tmp/target.lock
COPY build-target.sh /tmp/build-target.sh
RUN chmod +x /tmp/build-target.sh && /tmp/build-target.sh && rm -f /tmp/build-target.sh

COPY install-toolchain.sh /usr/local/bin/install-toolchain
RUN chmod +x /usr/local/bin/install-toolchain \
    && install-toolchain \
    && ! command -v rg > /dev/null \
    && rm -f /usr/local/bin/install-toolchain

WORKDIR /app
RUN mkdir -p /logs/artifacts
