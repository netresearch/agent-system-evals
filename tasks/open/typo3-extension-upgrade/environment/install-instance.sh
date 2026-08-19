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
RUNTIME_ENV=/opt/case/instance.env
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

# The hostname, written here rather than through Compose `extra_hosts`. That
# option is refused outright in combination with `network_mode: service:`
# — "conflicting options: custom host-to-IP mapping and the network mode" —
# and Harbor puts every service into the egress sidecar's namespace exactly
# that way. Docker rewrites /etc/hosts at container start, which is why a
# build-time entry is useless; this runs after that.
if [ -n "${SITE_HOSTNAME:-}" ] && ! grep -q "$SITE_HOSTNAME" /etc/hosts; then
    echo "127.0.0.1 $SITE_HOSTNAME" >> /etc/hosts
    echo "=== hostname $SITE_HOSTNAME"
fi

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
    --admin-username=admin --admin-user-password='Dev-Admin-4711!' \
    --admin-email=admin@example.com \
    --project-name="${PROJECT_NAME:-$SITE_IDENTIFIER}" \
    --server-type=other --no-interaction --force

echo "=== extension setup"
vendor/bin/typo3 extension:setup

echo "=== site configuration"
cat > config/sites/"$SITE_IDENTIFIER"/config.yaml <<SITECONF
base: '${DDEV_PRIMARY_URL:-http://$SITE_HOSTNAME}/'
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

# Only where the case describes an instance that is already in some state. A
# review or an upgrade starts from a clean installation, which is what a
# developer's own instance looks like before they touch anything.
if [ -f /opt/case/seed-reported-state.php ]; then
    echo "=== seeding the reported state"
    php /opt/case/seed-reported-state.php
fi

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

# What the ddev surface needs at run time, without the case's provenance: no
# target repository, no pinned commit, no case identifier.
cat > "$RUNTIME_ENV" <<ENVFILE
SITE_IDENTIFIER=$SITE_IDENTIFIER
SITE_HOSTNAME=$SITE_HOSTNAME
INSTANCE_DIR=$INSTANCE_DIR
DB_NAME=$DB_NAME
DB_USER=$DB_USER
DB_PASSWORD=$DB_PASSWORD
DB_HOST=$DB_HOST
ENVFILE

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

# Everything the agent must not find. The case's provenance and, where there is
# one, the seed script naming the very mechanism the agent is asked to
# establish: two trials were caught reading /opt/case/seed-reported-state.php,
# whose header describes the orphaned row, the unresolved foreign keys and the
# unique-key collision.
#
# Deleted here rather than guarded by a rule, and the ordering makes it
# airtight: the agent phase does not begin until the environment healthcheck
# passes, and the healthcheck waits for the marker written below.
echo "=== removing the case's own files from the agent's reach"
rm -f /opt/case/seed-reported-state.php /opt/case/target.lock \
      /usr/local/bin/build-instance /usr/local/bin/install-instance
# The log repeats what was seeded and names the case; the agent has no use for
# either. What the verifier needs, it collects from the database itself.
rm -f "$LOG"

touch "$MARKER"
echo "=== instance ready"
