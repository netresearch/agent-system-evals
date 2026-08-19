#!/usr/bin/env bash
# shellcheck disable=SC2016  # the single quotes keep the PHP below intact for
# the interpreter; the shell must not expand it first.
# Install the TYPO3 instance and put it into the reported state.
#
# Runs once at container start, because it needs the database and the database
# only exists once Compose is up. Everything that does not need a database —
# the project skeleton, the extension, the vendor tree — was already done at
# build time, so this is the short part.
#
# The recipe is the target's own `ddev install-v13`, minus DDEV: create the
# base distribution, point a path repository at the extension, require it,
# write the database connection, run setup, activate the extension, write a
# site. See docs/adr/0006-runtime-fidelity.md.
#
# Idempotent: the environment healthcheck polls until the marker appears, and a
# restarted container must not reinstall over a working instance.
set -euo pipefail

LOCK=/opt/case/target.lock
# shellcheck source=/dev/null
. "$LOCK"

MARKER="$INSTANCE_DIR/.instance-ready"
LOG=/var/log/install-instance.log
exec > >(tee -a "$LOG") 2>&1

if [ -f "$MARKER" ]; then
    echo "instance already installed"
    exit 0
fi

cd "$INSTANCE_DIR"

echo "=== waiting for the database"
for _ in $(seq 1 60); do
    if php -r '
        $c = @mysqli_connect(getenv("DB_HOST"), getenv("DB_USER"), getenv("DB_PASSWORD"), getenv("DB_NAME"));
        exit($c ? 0 : 1);
    '; then
        echo "database reachable"
        break
    fi
    sleep 2
done

echo "=== database connection"
mkdir -p config/system config/sites/"$SITE_IDENTIFIER" var/log var/cache
cat > config/system/additional.php <<PHPCONF
<?php
\$GLOBALS['TYPO3_CONF_VARS']['DB']['Connections']['Default'] = [
    'charset' => 'utf8mb4',
    'driver' => 'mysqli',
    'host' => '${DB_HOST}',
    'port' => 3306,
    'dbname' => '${DB_NAME}',
    'user' => '${DB_USER}',
    'password' => '${DB_PASSWORD}',
];
// Development settings, as the target's own DDEV instance runs them: an agent
// investigating behaviour must be able to see errors rather than a blank page.
\$GLOBALS['TYPO3_CONF_VARS']['BE']['debug'] = true;
\$GLOBALS['TYPO3_CONF_VARS']['FE']['debug'] = true;
\$GLOBALS['TYPO3_CONF_VARS']['SYS']['devIPmask'] = '*';
\$GLOBALS['TYPO3_CONF_VARS']['SYS']['displayErrors'] = 1;
\$GLOBALS['TYPO3_CONF_VARS']['SYS']['trustedHostsPattern'] = '.*';
PHPCONF

echo "=== typo3 setup"
vendor/bin/typo3 setup \
    --driver=mysqli --host="$DB_HOST" --port=3306 --dbname="$DB_NAME" \
    --username="$DB_USER" --password="$DB_PASSWORD" \
    --admin-username=admin --admin-user-password='Benchmark-Admin-4711!' \
    --admin-email=admin@example.com \
    --project-name="TextDB runtime case" \
    --server-type=other --no-interaction --force

echo "=== extension setup"
vendor/bin/typo3 extension:setup

echo "=== site configuration"
cat > config/sites/"$SITE_IDENTIFIER"/config.yaml <<SITECONF
base: '${DDEV_PRIMARY_URL:-http://v13.nr-textdb.ddev.site}/'
rootPageId: 1
languages:
  -
    title: English
    enabled: true
    languageId: 0
    base: /
    locale: en_US.UTF-8
    navigationTitle: English
    flag: gb
SITECONF

echo "=== seeding the reported state"
php /opt/case/seed-reported-state.php

vendor/bin/typo3 cache:flush || true

# The instance has to be *served*, not merely installed: this case is about a
# backend module, and the reported behaviour only exists behind a request.
# TYPO3's own rewrite rules, from the file the framework ships for exactly this
# purpose. The composer distribution leaves the docroot without one, so /typo3/
# resolves through DirectoryIndex while every sub-route answers 404 — a backend
# that looks reachable and is not. Hand-written rules were tried first and were
# worse: they routed the backend into the frontend, which answers 404 in its own
# voice and hides the cause.
echo "=== rewrite rules"
cp vendor/typo3/cms-install/Resources/Private/FolderStructureTemplateFiles/root-htaccess \
    public/.htaccess

echo "=== web server"
chown -R www-data:www-data "$INSTANCE_DIR/var" "$INSTANCE_DIR/public" 2>/dev/null || true
apache2ctl -k start
for _ in $(seq 1 30); do
    if curl -fsS -o /dev/null "http://127.0.0.1/typo3/"; then
        echo "backend answers over HTTP"
        break
    fi
    sleep 1
done

touch "$MARKER"
echo "=== instance ready"
