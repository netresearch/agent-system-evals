# OFR-TYPO3-RUNTIME-001 — diagnose a reported save failure

```
Editors report that saving a translation in the TextDb backend module does
nothing — the dialog closes, but the old value is still there. Please find out
what is going on.
```

The first **runtime** case: the agent works against an installed TYPO3 13.4
instance with the extension active and a database in the state a real
production report described.

## Why this case is a runtime case

The reported behaviour is invisible in the checkout. A save that silently
inserts an orphaned row instead of updating, and then collides with a unique
key on every later attempt, is a property of the running system. Nothing in
the source says which rows exist, what the resolved TCA looks like once every
extension has loaded, or which extensions are active at all.

That is also why this case can measure a class of tool the repository-level
cases cannot assess: a server that introspects a running installation has
nothing to read in a checkout, and scoring it there would produce a bad number
for a reason unrelated to its quality.

## How the instance is built

The recipe is the target's own `ddev install-v13`, run without DDEV — see
[ADR 0006](../../../docs/adr/0006-runtime-fidelity.md).

DDEV itself cannot run here: it drives Docker, and a trial is already inside a
container, so using it would mean handing an autonomous agent the host's Docker
socket. What a developer's DDEV actually gives the agent is reproduced instead:
the instance is **served over HTTP** by Apache under the hostname
`.ddev/config.yaml` declares, and a `ddev` command answers the subcommands an
agent reaches for — `exec`, `mysql`, `describe`, `status`, `launch`, `logs`.
`ddev describe` states plainly that it is a compatible surface rather than
DDEV, so an agent that checks finds out.

That is not cosmetic. The case is about a backend module, and without a web
server the reported behaviour could only be described, never triggered. The
backend now accepts a login, so the failure can be reproduced.

Split by what needs a database:

| Build time | Container start |
|---|---|
| extension checkout at the pinned commit | `typo3 setup` |
| `composer create-project typo3/cms-base-distribution:^13.4` | `extension:setup` |
| path repository + `composer require` | site configuration |
| | seed the reported state |

The agent phase is held back by an environment healthcheck until the instance
answers `typo3 site:list`, so no trial can start against a half-installed
system.

Verified before the case was admitted: TYPO3 setup completes, `nr_textdb` is
activated alongside 24 core extensions, the site is listed, and the database
holds both rows the report describes.

## Seeded data, not an injected defect

The defect is the extension's own, at the commit before it was fixed. What is
seeded is the *situation*: the record an editor was trying to change, and the
orphaned row a failed save left behind. Reproducing it would need a click in
the backend module and this environment has no web server — and a developer
handed this ticket receives exactly this state anyway.

## Results

See [RESULTS.md](RESULTS.md). In short: every agent in every fleet found the
root cause and established it against the running instance, no tool stack made
a difference beyond noise, and all of them left the same gap — they see the
orphaned row and never tell the developer to remove it.
