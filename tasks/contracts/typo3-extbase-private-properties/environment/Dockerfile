# A contract eval: cheap and deterministic by construction. No database, no web
# server, no judge — the condition is known and the check either fires or does
# not. See ADR 0002 and this case's README.
FROM php:8.3-cli

ENV DEBIAN_FRONTEND=noninteractive \
    COMPOSER_ALLOW_SUPERUSER=1 \
    COMPOSER_NO_INTERACTION=1

RUN apt-get update && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

# The extension under test. Synthetic and minimal on purpose: a contract eval
# should fail for one reason only, and a real extension brings a dozen other
# things an agent could reasonably report instead.
COPY extension /app
WORKDIR /app
# No composer install, and no vendor tree. The question is about what the
# source declares, which needs no dependencies resolved — and a contract eval
# that pulls a framework to answer it is not cheap enough to gate a merge.
RUN php -l Classes/Domain/Model/Product.php > /dev/null \
    && php -l Classes/Domain/Model/Category.php > /dev/null \
    && git init -q . && git add -A \
    && git -c user.email=case@example.com -c user.name=case \
        commit -q -m "shop_catalogue" 

# The Netresearch toolchain, off the default PATH. A contract eval compares
# arms too — does the check fire with the stack and without it? — so it has to
# be able to host the fleets, even though its own grading needs none of this.
COPY install-toolchain.sh /usr/local/bin/install-toolchain
RUN chmod +x /usr/local/bin/install-toolchain \
    && install-toolchain \
    && ! command -v rg > /dev/null \
    && rm -f /usr/local/bin/install-toolchain

RUN mkdir -p /logs/artifacts
