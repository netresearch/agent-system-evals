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

## Measured since, and then falsified

`OFR-PY-CI-001` ran with `github-project` added and **did not move: 0 of 3
against 0 of 3**. From that plus the four earlier routing runs I wrote a rule
here and on the published page:

> A skill is reached when the words the request itself uses appear in the
> opening clause of its description.

**That rule is wrong, and the evidence refuting it was already on disk when I
wrote it.** Checking every silent case against the opening clause of every skill
its fleet carries:

| case | skills whose opening clause shares a word with the request | invoked |
|---|---|---|
| version metadata | `typo3-extension-upgrade` — *extensions, typo3, versions* | 0/7 |
| restraint | `typo3-conformance` — *check, typo3*; `typo3-extension-upgrade` — *versions* | 0/9 on `nr` |
| Go LDAP | `security-audit` — *security*, and the request opens "Someone from the **security** side says…" | 0/5 |
| Extbase contract | `php-modernization` — *property*; `typo3-testing` — *class, extension* | 0/6 |
| runtime bug | `typo3-docs` — *translation* | 0/46 |
| Python CI | none | 0/8 |

Five of six silent cases have shared vocabulary in an opening clause and none of
them route. Shared words predict nothing.

## What actually survives the six runs

Two interventions moved routing completely, and both did the same thing: they
put **the action the request asks to perform** into the opening clause, in the
request's own terms.

| intervention | before | after |
|---|---|---|
| add `github-release` — opens *"Use when creating releases, version bumps, tagging"*; request says *"prepare the 2.4.2 release"* | 0/6 | 6/6 |
| rewrite `typo3-conformance` to open *"Use when checking which TYPO3 versions an extension declares it supports, when composer.json and ext_emconf.php disagree"*; request asks which versions it supports and says the statements disagree | 1/6 | 6/6 |

`typo3-extension-upgrade` shares three words with the metadata request and
describes *upgrading to a newer LTS*, which is not what was asked.
`security-audit` shares "security" and describes *conducting an OWASP
assessment*, which is not what was asked either. The difference is between a
description that names the requested action and one that happens to use the same
nouns.

**And the second of those two positives is close to circular.** I wrote that
opening clause from the request, so it matching the request is not a discovery.
The release case is the one clean positive: an existing published skill, written
without this benchmark in view, whose first clause names the request's verb.

So what is claimable is narrow: *a skill whose opening clause names the action a
request asks for can go from never being loaded to always being loaded, and both
composition and wording can put it there.* It is not a predictor. Nothing here
lets anyone look at a fleet and a request and say in advance whether a skill will
be reached — five cases where it plausibly should have been say it will not.

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
   held — and it was an easier prediction than it looked. Under the corrected
   reading above, this case shares no vocabulary at all with `typo3-ddev`'s
   opening clause and describes an action the skill does not claim, so both the
   rule as written and its corrected form expected a zero. It confirms the
   negative direction and nothing more. Three trials is small and the Wilson interval reaches 0.56, so this
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
