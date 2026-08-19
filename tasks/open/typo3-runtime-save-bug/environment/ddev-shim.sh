#!/usr/bin/env bash
# A DDEV-compatible command surface over an instance that DDEV did not create.
#
# Why a surface and not DDEV: DDEV drives Docker, and a trial already runs
# inside a container. Real DDEV here would mean mounting the host's Docker
# socket into a container running an autonomous agent — root-equivalent control
# of the machine, and parallel trials colliding on project names and ports 80
# and 443. The realism that matters is what the developer hands the agent: an
# instance that is already up, reachable under a known hostname, with `ddev`
# as the way into it. That is what this provides.
#
# It is not a pretence. `ddev describe` says plainly that this is a compatible
# surface, so an agent that inspects rather than assumes finds out. The
# subcommands are the ones an agent actually reaches for; anything else exits
# non-zero with a pointer rather than pretending to succeed, because a silent
# no-op would be scored as agent behaviour.
set -euo pipefail

INSTANCE=/instance
LOCK=/opt/case/target.lock
# shellcheck source=/dev/null
[ -f "$LOCK" ] && . "$LOCK"
DB_HOST="${DB_HOST:-127.0.0.1}"
DB_NAME="${DB_NAME:-typo3}"
DB_USER="${DB_USER:-typo3}"
DB_PASSWORD="${DB_PASSWORD:-typo3-benchmark-password}"
URL="${DDEV_PRIMARY_URL:-http://v13.nr-textdb.ddev.site}"

usage() {
    cat <<EOF
ddev — DDEV-compatible surface for this instance (not DDEV itself)

  ddev describe            what this instance is, and where
  ddev exec <cmd>...       run a command inside the instance directory
  ddev mysql [args]        mysql client against the instance database
  ddev launch              print the URL (no browser here)
  ddev status | start | stop | restart
  ddev composer <args>     composer inside the instance
  ddev typo3 <args>        vendor/bin/typo3 inside the instance
  ddev logs [-f]           web server logs
EOF
}

apache_running() { pgrep -x apache2 > /dev/null 2>&1; }

case "${1:-describe}" in
    describe)
        cat <<EOF
NAME          nr-textdb
LOCATION      $INSTANCE
PRIMARY URL   $URL
DATABASE      mysql://$DB_USER@$DB_HOST/$DB_NAME
WEB SERVER    apache2 ($(apache_running && echo running || echo stopped))
TYPO3         $("$INSTANCE"/vendor/bin/typo3 --version 2>/dev/null | head -1 || echo unknown)

NOTE          This is a DDEV-compatible command surface, not DDEV. The instance
              was built from this project's own .ddev/commands/web/install-v13
              recipe without DDEV, because the environment is already a
              container. Paths, hostname and database match; \`ddev\` supports
              the subcommands listed by \`ddev --help\`.
EOF
        ;;
    exec)
        shift
        cd "$INSTANCE" && exec "$@"
        ;;
    mysql)
        shift
        exec mysql --skip-ssl -h "$DB_HOST" -u "$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" "$@"
        ;;
    composer)
        shift
        cd "$INSTANCE" && exec composer "$@"
        ;;
    typo3)
        shift
        cd "$INSTANCE" && exec vendor/bin/typo3 "$@"
        ;;
    launch)
        echo "$URL"
        echo "(no browser in this environment — fetch it, e.g. curl -sS $URL/typo3/)"
        ;;
    status)
        if apache_running; then echo "web: running"; else echo "web: stopped"; fi
        if mysql --skip-ssl -h "$DB_HOST" -u "$DB_USER" -p"$DB_PASSWORD" \
                -e 'SELECT 1' "$DB_NAME" > /dev/null 2>&1; then
            echo "db: running"
        else
            echo "db: unreachable"
        fi
        ;;
    start|restart)
        if apache_running; then
            apache2ctl -k graceful
        else
            apache2ctl -k start
        fi
        sleep 1
        if apache_running; then
            echo "web: running at $URL"
        else
            echo "web: failed to start" >&2
            exit 1
        fi
        ;;
    stop)
        apache2ctl -k stop || true
        echo "web: stopped"
        ;;
    logs)
        shift || true
        exec tail "$@" /var/log/apache2/typo3-error.log
        ;;
    -h|--help|help)
        usage
        ;;
    *)
        echo "ddev: '$1' is not supported by this compatible surface." >&2
        usage >&2
        exit 2
        ;;
esac
