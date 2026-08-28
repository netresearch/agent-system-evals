# Which silent cases have a capability to route to

Eight of eleven cases grade a stack whose skills are never loaded. Until 28
August that was read as a routing problem. It is not one: adding
`github-release-skill` to the release case's fleet moved skill invocation from
0 of 6 to 6 of 6 at Fisher exact p 0.002, while rewriting a skill's own
description moved nothing. **The lever that works is what the fleet carries.**

So the question for every silent case is answerable rather than speculative:
does the organisation publish a skill whose description claims the work this
request asks for? This document answers it case by case.

## Two instruments were discarded before this one

**A word-overlap matcher.** Score every Netresearch skill description by shared
words with the request. Discarded because it fails its own counter-probe: run
against `OFR-TYPO3-UPGRADE-001`, a case that routes to `typo3-extension-upgrade`
in 23 of 29 trials, it returns *nothing matches*, and its best answer to a
continuous-integration question was a Figma handoff skill. An instrument that
cannot find a match where one demonstrably exists is not evidence that no match
exists.

**The marketplace catalogue.** The first reading used the descriptions listed by
`find-org-skills.py`, which reads each marketplace's `.claude-plugin/marketplace.json`.
That is the wrong text. Routing reads the `description` in the skill's own
`SKILL.md`, and of the 38 Netresearch skills where both could be compared,
**37 differ**. They are two registers rather than two versions: the catalogue
carries a summary written for a human browsing plugins ("Security audit patterns
for PHP applications…"), `SKILL.md` carries trigger text written for an agent
deciding whether to load ("Use when conducting security assessments — OWASP Top
10 / API / LLM…").

The difference is not cosmetic. It reversed two of the five findings below, and
the first version of this document published both of them.

## Case by case, read against `SKILL.md`

| case | what the request asks for | a skill whose description claims it | in the fleet? | what follows |
|---|---|---|---|---|
| `OFR-TYPO3-RELEASE-001` | prepare a release | `github-release` | no | **measured**: 0/6 → 6/6, p 0.002 |
| the three version-metadata cases | reconcile what an extension declares about supported versions | `typo3-conformance` | yes | routing, not composition |
| `OFR-PY-CI-001` | is a scheduled job's red exit right | `github-project` — "CI fails, authoring or consuming reusable workflows, editing a repo's own `.github/workflows`" | no | **testable** |
| `OFR-TYPO3-RUNTIME-001` | why does saving in a backend module do nothing | `typo3-ddev` — "whenever a running TYPO3 instance is wanted, started or reached" | no | **testable**, partially |
| `OFR-GO-LDAP-001` | a timing side channel in a Go library | `go-development` — "LDAP/AD clients" | **yes** | routing, not composition |
| `CON-TYPO3-EXTBASE-001` | find properties Extbase cannot persist | none | — | a gap in the catalogue |

## What changed when the right text was read

**The Go case is not a composition problem.** `go-development` was in the fleet
for all five trials and its description names LDAP/AD clients, which is exactly
what the target is. It was invoked zero times. The first version of this
document said the capability was scoped to another language, on the strength of
a catalogue line reading "Security audit patterns for PHP applications" — a
sentence that appears nowhere in the skill that routes.

It also sharpens the release-case finding rather than contradicting it. The
release request says *"prepare the 2.4.2 release"* and the skill's description
says "releases"; the Go request says *"with this library you can tell whether an
account exists just from how long a failed login takes"* and never says LDAP.
The word is in the repository, not in the request. **Routing keys on the words
the request uses, not on what the code turns out to be.**

**The CI case's candidate changed.** The catalogue described `git-workflow` as
"Git workflow best practices for teams and CI/CD pipelines"; its `SKILL.md`
describes branching, Conventional Commits, PR review threads and merges, and
does not claim continuous integration at all. `github-project` does — "CI fails,
authoring or consuming reusable workflows, editing a repo's own
`.github/workflows`". A fleet built on the first reading would have added a
skill that does not claim the work and reported the result as composition
failing.

## The experiments this leaves

1. `OFR-PY-CI-001` with `github-project` added — `fleets/nr-ci.yaml`.
2. `OFR-TYPO3-RUNTIME-001` with `typo3-ddev` added. Weaker: the skill claims
   reaching a running instance, not diagnosing a save that silently fails, and
   the case's environment already provides the instance. Worth running because
   46 equipped trials with zero invocations is the largest silent block in the
   benchmark, and this is the only skill that names anything the case involves.
3. Nothing for `CON-TYPO3-EXTBASE-001`. No skill claims Extbase persistence
   rules; `typo3-conformance` is nearest and is already in the fleet.

## What this does not claim

That an agent *should* have loaded any of these. Routing is the agent's
decision and the measured rate is what it is. This establishes only which cases
had something to route to, so a zero can be read as a statement about the fleet
where it is one, and about the agent where it is one.
