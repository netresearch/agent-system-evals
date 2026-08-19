# The environment every case starts from

A developer working on a TYPO3 extension has two things: the repository checked
out, and a TYPO3 instance running with that extension installed. Not sometimes
— always, because they cannot see what they are doing otherwise. That is the
baseline this benchmark measures against.

This directory holds it. Every case gets the same environment; what varies
between cases is the request, the target and the rubric, and what varies
between arms is the fleet. Nothing else.

## Why this is not a per-case decision

It was, and that was wrong. The first cases were built as repository-level
reviews, with an instance added only to the case whose defect could not be seen
without one. That silently changed the question. A benchmark run against a bare
checkout does not measure how much a tool helps a developer; it measures how
much it helps someone working in an environment no developer actually has —
and it makes tools that read a running application look inapplicable when they
are simply unused.

We are not measuring how good a development environment is. We are measuring
what skills and MCP servers add **inside a proper one**.

## What each case provides

| File | Role |
|---|---|
| `environment/target.lock` | the target, its commit, the TYPO3 line, the hostname |
| `environment/seed-reported-state.php` | optional — only where the case describes an instance already in some state |

Everything else comes from here, copied in by `scripts/sync-environment` and
checked by `scripts/validate-tasks`. Copied rather than shared through a base
image: Harbor builds each case from its own directory, so a common base would
add a build-ordering dependency that fails as "image not found" long after the
cause.

## What it builds

| Script | When | What |
|---|---|---|
| `build-instance.sh` | image build | extension at the pinned commit, base distribution, path repository, `composer require` |
| `install-toolchain.sh` | image build | the Netresearch CLI toolchain, off the default PATH — only a fleet that declares it can reach it |
| `install-instance.sh` | container start | `typo3 setup`, `extension:setup`, site config, `.htaccess`, Apache, optional seed |
| `ddev-shim.sh` | installed as `ddev` | the surface a developer's DDEV offers: `exec`, `mysql`, `describe`, `status`, `launch`, `logs` |

The instance is **served**, not merely installed. An extension case that cannot
issue a request cannot reproduce anything a user reported, and a tool that
introspects a running application has nothing to introspect.

## Why not DDEV itself

DDEV drives Docker and a trial is already inside a container, so running it
would mean handing an autonomous agent the host's Docker socket, and parallel
trials would collide on project names and ports 80/443. The recipe is the
target's own `.ddev/commands/`, carried out directly; `ddev describe` says
plainly that it is a compatible surface rather than DDEV, so an agent that
inspects finds out. See [ADR 0006](../../docs/adr/0006-runtime-fidelity.md).
