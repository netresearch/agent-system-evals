# ADR 0006 — Runtime cases run a real installation, built without DDEV

- Status: accepted — supersedes the original decision of 2026-08-15
- Date: 2026-08-17

## Context

Part of the Netresearch TYPO3 workflow runs against a live instance under DDEV.
Evaluating that behaviour needs a running installation: database, TYPO3 boot,
backend, resolved TypoScript.

The first version of this ADR deferred all runtime cases behind a fidelity
spike, on the reasoning that DDEV is itself a Docker orchestrator and running it
inside a Harbor sandbox means nested containerisation with unknown consequences.

That reasoning was sound and the conclusion drawn from it was not. It slid from
"running DDEV inside Harbor is risky" to "runtime is deferred", and then the
repository-level cases were built as though repository-level were the natural
scope for extension work. It is not.

**Extension work here is runtime work.** The upgrade case's own target ships
`ddev install-all`, builds two complete TYPO3 instances, and its `AGENTS.md`
names that as the recommended setup. Plugin behaviour, resolved TypoScript after
site-set merging, TCA once every extension has loaded — none of it exists in a
file. A case that reviews an extension without an instance is measuring a
reduced version of the job and should say so.

## Decision

**Runtime cases are built, and they do not use DDEV.**

DDEV supplies three things: a web server, a database, and hostnames. Harbor
supplies the first two through a Compose task. The third is not needed for
CLI-level introspection and is a Compose service name where it is.

What a runtime case installs is exactly what the target's own DDEV command
installs, minus DDEV:

```
composer create-project typo3/cms-base-distribution:^13.4 <dir>
composer config repositories.local path <extension-dir>
composer require <vendor>/<extension>:*
config/system/additional.php     # database connection
vendor/bin/typo3 setup --driver=... --no-interaction --force
vendor/bin/typo3 extension:setup
config/sites/<id>/config.yaml
```

The recipe is taken from the target repository rather than invented, so the
instance under test is the one its developers actually work against.

**Repository-level cases remain**, and their limitation is now stated rather
than implied: they measure what can be established from a checkout, which is
less than the job. `metadata.runtime` distinguishes them.

**Nested Docker stays out.** If a future case genuinely needs DDEV itself
rather than what DDEV sets up, that is a separate decision with its own
evidence.

## Consequences

Runtime cases are more expensive: a database service, an installation step, and
a longer environment build. The build is where that cost belongs — a case whose
instance cannot be provisioned must fail at build time rather than score every
trial as the agent's failure.

They also make a class of tool measurable that repository-level cases cannot
assess at all. A server that introspects a running installation has nothing to
read in a checkout; measuring it there would produce a bad score for a reason
unrelated to its quality.

The claim that DDEV fidelity is the blocker is retired. The remaining fidelity
question is narrower and honest: an instance built by this recipe is the one the
target's developers build, but it is not their laptop. Where that difference
matters for a finding, the case says so.
