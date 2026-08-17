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

No DDEV. DDEV supplies a web server, a database and hostnames; of those a
runtime case needs the database, and Harbor provides it as a Compose service.
The recipe is the target's own `ddev install-v13`, minus DDEV — see
[ADR 0006](../../../docs/adr/0006-runtime-fidelity.md).

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

Not yet run. Nothing is recorded here until it is.

```
./scripts/run-evaluation OFR-TYPO3-RUNTIME-001 --fleet control
./scripts/run-evaluation OFR-TYPO3-RUNTIME-001 --fleet nr
./scripts/run-evaluation OFR-TYPO3-RUNTIME-001 --fleet companion
./scripts/compare jobs/<a> jobs/<b>
```
