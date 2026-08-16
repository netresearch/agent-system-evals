# shellcheck shell=bash
# shellcheck disable=SC2016  # the single quotes are the point: the PHP below
# must reach the interpreter with its own variables intact, not expanded by
# the shell first.
# Shared matrix helpers. Sourced, not executed.
#
# Both the build-time readiness check and the post-run outcome check have to
# pin a working copy to one TYPO3 line. Getting that wrong in either place is
# expensive in a different way: at build time it fails a good image, and after
# a run it reports a correct solution as broken.
#
# Parsing is done with `php -r`, not python3. This is a php:8.3-cli image and
# has no python3 — the first version used it and the build died with exit 127,
# which says "command not found" and nothing about which command.

# The TYPO3 packages a composer.json actually declares.
#
# Read from the file rather than hard-coded, because which packages belong here
# is part of what the agent may change — the real migration this case is drawn
# from removed two of them, and a fixed list would have called that correct
# change a failure.
typo3_packages() {
    local manifest="${1:-composer.json}"
    php -r '
        $file = $argv[1];
        if (!is_readable($file)) { exit(0); }
        $data = json_decode((string) file_get_contents($file), true);
        if (!is_array($data) || !isset($data["require"])) { exit(0); }
        $names = array_filter(
            array_keys($data["require"]),
            static fn (string $n): bool => str_starts_with($n, "typo3/cms-")
        );
        echo implode(" ", $names);
    ' -- "$manifest"
}

# The installed version of a package, or "?" when it cannot be determined.
installed_version() {
    local package="${1:?package required}"
    composer show "$package" --format=json 2>/dev/null | php -r '
        $raw = stream_get_contents(STDIN);
        $data = json_decode($raw, true);
        $versions = $data["versions"] ?? null;
        echo is_array($versions) && $versions !== [] ? $versions[0] : "?";
    ' 2>/dev/null || echo "?"
}

# Can this environment install a TYPO3 line at all, for this extension?
#
# A build-time question, and a different one from the one below. The pristine
# target declares `^12.4 || ^13.4`, so it excludes the newer line by design —
# that exclusion is the task. To ask whether the *environment* could support
# the line, the constraint has to be rewritten first.
#
# Conflating the two cost a build: the readiness check was rewritten to use the
# tree-respecting form and then correctly reported that the unmodified target
# does not admit 14.3, which is true and useless as a readiness signal.
# Extra arguments are passed to `composer update`. The readiness check passes
# `--dry-run`, which answers the question without downloading; the cache warm-up
# passes nothing, because it exists precisely to download.
env_can_install() {
    local line="$1"
    shift
    local packages
    packages="$(typo3_packages composer.json)"
    [ -n "$packages" ] || return 1

    local args=()
    local package
    for package in $packages; do
        args+=("${package}:^${line}")
    done

    composer config policy.advisories.block false >/dev/null 2>&1
    composer require --no-interaction --no-update --no-scripts "${args[@]}" >/dev/null 2>&1 || return 1
    composer update --with-all-dependencies --no-interaction \
        --no-progress --no-ansi "$@"
}

# Pin a working copy to one line and install it.
#
# Uses `--with`, a temporary constraint that must still satisfy the manifest's
# own requirement, so this asks the question that matters: does the tree the
# agent left *admit* this line? Measured, not assumed —
#
#     root ^12.4 || ^13.4, --with ^14.3  -> exit 1
#     root ^12.4 || ^13.4, --with ^13.4  -> exit 0
#
# The first version used `composer require` to pin instead, which rewrites the
# manifest before testing it. That measured whether the environment can install
# a line, not whether the agent's work admits it, and would have reported
# success for a tree the agent never touched.
#
# `--with-all-dependencies` on top: moving one TYPO3 package while its siblings
# sit on the old window is a conflict Composer reports rather than resolves.
#
# Resolution and installation are separate passes. In one pass Composer upgrades
# typo3/class-alias-loader and then executes it as a plugin in the same process,
# which dies with `Class "…\CaseSensitiveToken" not found` — the plugin's files
# changed underneath the running instance. Splitting the passes lets the new
# version load cleanly.
pin_and_update() {
    local line="$1"
    shift
    local packages
    packages="$(typo3_packages composer.json)"
    [ -n "$packages" ] || return 1

    local args=()
    local package
    for package in $packages; do
        args+=(--with "${package}:^${line}")
    done

    composer config policy.advisories.block false >/dev/null 2>&1
    composer update --with-all-dependencies "${args[@]}" --no-install \
        --no-interaction --no-progress --no-ansi "$@" || return 1

    # A dry run answers the resolution question and must not then install.
    case " $* " in
        *" --dry-run "*) return 0 ;;
    esac

    # vendor/ goes first. Composer loads plugins from the installed tree at
    # startup, then replaces their files during the install; typo3/class-alias-
    # loader then runs its already-loaded v1 class against v2 files and dies
    # with `Class "…\CaseSensitiveToken" not found`. Splitting resolution from
    # installation is not enough, because a fresh `composer install` still
    # starts from the old vendor. Removing it first makes the new versions load
    # cleanly.
    rm -rf vendor
    composer install --no-interaction --no-progress --no-ansi
}
