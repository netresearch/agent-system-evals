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
the first version of this document published both of them. Measured over the
Netresearch marketplace's 40 plugins: one catalogue description matches its
skill's, 37 differ, and while 38 of 38 `SKILL.md` descriptions open with "Use
when", exactly one catalogue entry does. Reported as
[retro-skill#83](https://github.com/netresearch/retro-skill/issues/83), because
the script presents the browse text as though it answered a question only the
trigger text can answer.

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

## Measured since: composition alone is not the rule

`OFR-PY-CI-001` ran with `github-project` added and **did not move: 0 of 3
against 0 of 3**. The first negative result for the composition lever, on the
case chosen because the lever looked most likely to work.

Four routing measurements from 28 August now say one thing rather than three. A
skill is reached when **the words the request itself uses appear in the opening
clause of the description**. Both halves are load-bearing:

| the skill in the fleet… | loaded | case |
|---|---|---|
| opens by naming the request's words | 6/6 | release, after adding `github-release` |
| opens by naming the request's words | 6/6 | restraint, after moving them into the first sentence |
| names them 35 words in, in a trigger list | 1/6 | restraint, first attempt |
| covers the work under other words | 0/3 | Python CI, after adding `github-project` |
| covers the work under other words | 0/5 | Go: skill says "LDAP/AD clients", request says "library" |
| is not in the fleet at all | 0/6 | release, before |
| covers the work under other words | 0/3 | runtime bug, after adding `typo3-ddev` — **predicted before the run** |

So the sweep's question was the wrong one. "Does a skill claim this work?" does
not predict routing; "does a skill open by naming what the request says?" does,
on five for five so far. That is a harder bar, and it means the two catalogue
gaps below are not the only cases without a reachable capability — the Go case
has one installed and unreachable.

## The experiments this leaves

1. ~~`OFR-PY-CI-001` with `github-project` added~~ — **run, did not move.**
   `tasks/open/py-scheduled-job-exit-code/RESULTS.md` records why, and why the
   obvious follow-up is not being run: rewriting `github-project`'s opening
   clause to suit this case would be the benchmark writing a skill's
   description for its own benefit, and that skill's first sentence is
   contested space among eight other subjects.
2. `OFR-TYPO3-RUNTIME-001` with `typo3-ddev` added — **and this one is now a
   test of the rule rather than of the case.** The rule above was derived from
   five measurements after the fact, which is the weakest way to hold a rule.
   This is the first case it can be applied to before the run.

   **Prediction, recorded before launching: 0 of N.** `typo3-ddev` opens *"Use
   whenever a running TYPO3 instance is wanted, started or reached"*; the
   request says *"saving a translation in the TextDb backend module does
   nothing — the dialog closes, but the old value is still there"*. Instance,
   started, reached, DDEV: none of those words is in the request, and the case's
   environment hands the agent a running instance without being asked. By the
   rule this is the "covers the work under other words" row, and it should not
   route.

   An invocation refutes the rule outright. A zero is the first out-of-sample
   confirmation, on the benchmark's largest silent block — 46 equipped trials,
   zero invocations — and it converts that block from unexplained to explained.

   **Run, 28 August: 0 of 3 against 0 of 3, Fisher p 1.000.** The prediction
   held. Three trials is small and the Wilson interval reaches 0.56, so this
   could not distinguish never from sometimes; what it could have produced, and
   did not, is the single invocation that would have falsified the rule. The
   record is in `tasks/open/typo3-runtime-save-bug/RESULTS.md`.
3. Nothing for `CON-TYPO3-EXTBASE-001`. No skill claims Extbase persistence
   rules; `typo3-conformance` is nearest and is already in the fleet.

## What this does not claim

That an agent *should* have loaded any of these. Routing is the agent's
decision and the measured rate is what it is. This establishes only which cases
had something to route to, so a zero can be read as a statement about the fleet
where it is one, and about the agent where it is one.
