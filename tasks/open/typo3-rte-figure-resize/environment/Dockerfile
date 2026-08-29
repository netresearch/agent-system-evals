# The extension at the commit before a reported rendering defect was fixed,
# with its own test stack installed and ready to run.
#
# No web server and no database service, which is a deviation from the other
# open cases and is deliberate. The reported behaviour is a pure rendering
# path: stored HTML in, rendered HTML out, through the extension's own
# functional test stack on SQLite. An agent can reproduce the report here
# without an instance, and the mechanical check runs the same way. The cost of
# an Apache + MariaDB instance bought nothing this case's question needs.
#
# What that costs is stated rather than hidden: an agent that would have looked
# at the rendered page in a browser cannot, and a tool that reads a running
# application has nothing to read. If the transcripts show arms failing for
# want of an instance rather than for want of the fix, this decision is the
# first thing to revisit.
FROM php:8.3-cli

ENV DEBIAN_FRONTEND=noninteractive \
    COMPOSER_ALLOW_SUPERUSER=1 \
    COMPOSER_NO_INTERACTION=1 \
    COMPOSER_HOME=/composer

RUN apt-get update && apt-get install -y --no-install-recommends \
        git unzip libzip-dev libicu-dev libsqlite3-dev ca-certificates \
    && docker-php-ext-install -j"$(nproc)" zip intl pdo_sqlite \
    && rm -rf /var/lib/apt/lists/*

COPY --from=composer:2 /usr/bin/composer /usr/bin/composer

COPY target.lock /tmp/target.lock
COPY build-target.sh /tmp/build-target.sh
RUN chmod +x /tmp/build-target.sh && /tmp/build-target.sh && rm -f /tmp/build-target.sh

# The Netresearch toolchain, off the default PATH: only the arm whose fleet
# names it gets the directory prepended, so an unequipped arm sees an image
# where these commands do not exist.
COPY install-toolchain.sh /usr/local/bin/install-toolchain
RUN chmod +x /usr/local/bin/install-toolchain \
    && install-toolchain \
    && ! command -v rg > /dev/null \
    && rm -f /usr/local/bin/install-toolchain

WORKDIR /app
RUN mkdir -p /logs/artifacts
