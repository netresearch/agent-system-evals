# OFR-GO-LDAP-001 — a reported timing side channel, in Go

```
Someone from the security side says that with this library you can tell whether
an account exists just from how long a failed login takes. Have a look, and if
it is true, fix it.
```

The first case outside TYPO3 and outside PHP
([issue #16](https://github.com/netresearch/agent-system-evals/issues/16)).
A Go library, a security report, a running directory to check it against.

## The target

`netresearch/simple-ldap-go` at `3aef601d`, the commit before the fix landed.
The library wraps `go-ldap` for authentication against Active Directory and
OpenLDAP and has two ways of checking a password: by account name and by
distinguished name.

The report is true. The account-name path performs a dummy bind when the
account does not exist, so a missing and a present account cost the same
network round-trips; the DN path returns as soon as the lookup fails, one
round-trip earlier. A service rebind added two commits before this one widened
the gap by one more round-trip on the existent side only. The difference is
measurable from outside and tells an attacker which DNs exist.

## Why this case exists

Every earlier case is TYPO3 and PHP, and the repository's own README says its
evidence covers that and nothing wider. This is the narrowest possible step
outward that still asks the benchmark's question: a request a colleague would
send, a real defect with a real fix in the target's future, and work that
cannot be done from the diff alone — the claim has to be established against
code and a directory before it is worth a change.

It is also the shape of defect that rewards reading the neighbouring code. The
library has already solved this problem once, on the sibling path, with helpers
that the DN path can call. An agent that reads both paths finds a fix that is
three calls long; one that reads only the reported path is likely to invent a
sleep.

## What is graded

Mechanically: the verifier's regression check passes against the tree the
agent left behind. It is the upstream test for this defect with the container
setup replaced by the OpenLDAP that Compose already runs, and its observable is
the rate limiter's failure metric — before the fix the not-found path returned
before anything was recorded. A bind added without the recording the sibling
path performs fails it, and that is deliberate. Beside it: the project's own
build, vet and unit suite still pass, the diff touches the file the report is
about, and something was changed at all.

By judge, one dimension, `timing_parity`: whether the asymmetry was established
before the first edit, whether the fix mirrors the sibling path or invents a
third way, whether a guard was left that observes the fix rather than the
clock, and whether the diff is confined to what was asked.

## What the environment provides

The module at its pinned commit with every dependency downloaded, Go 1.27 with
`GOTOOLCHAIN=local`, and an OpenLDAP started by Compose with exactly the values
the target's own integration setup uses — so the project's suite is one command
away, and a test the agent writes against the directory will run.

The module proxy is reachable; the target's forge is not, because the fix lives
in its future.

## Status

**Never run.** The case validates and its environment builds; no trial has been
recorded against it, so nothing here is a result.

## Reviewed by

Nobody yet. `docs/governance.md` requires a case to be admitted by someone who
did not write it; this repository has been written by one person, so the field
is empty rather than filled in by its author.

## Origin

Issue `netresearch/simple-ldap-go#219` of 26 August 2026, surfaced during the
review of an unrelated hardening change, and fix `f14711be` the same day, whose
regression test this case's mechanical check descends from. No learning store
exists in which a retro id could be looked up; `source_learning_id` is coined
here the way the eight earlier ones were, and this section is where it points.

## What capability this task plausibly needs

Recorded so that a skill-invocation count of zero can be read. A zero means one
of two things — the capability was on offer and was not selected, or it was not
on offer — and those are findings about different things (see issue #24).

Reading and fixing Go, and working against an LDAP directory.
`netresearch/go-development-skill` exists, names LDAP/AD clients in its
description, and documents this very library's connection quirks. It is in
`fleets/nr-go.yaml` and in no other fleet.

**Present in `nr-go`; absent from `nr`.** A run against `nr` measures
composition, not routing — see the note on `fleets/nr.yaml`.
