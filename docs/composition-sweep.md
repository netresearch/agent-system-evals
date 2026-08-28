# Which silent cases have a capability to route to

Eight of eleven cases grade a stack whose skills are never loaded. Until 28
August that was read as a routing problem. It is not one: adding
`github-release-skill` to the release case's fleet moved skill invocation from
0 of 6 to 6 of 6 at Fisher exact p 0.002, while rewriting a skill's own
description moved nothing. **The lever that works is what the fleet carries.**

So the question for every silent case is now answerable rather than
speculative: does the organisation publish a skill whose description claims the
work this request asks for? This document answers it case by case, and the
answers are not all the same shape.

## How this was decided, and how it was not

The first attempt was mechanical — score every Netresearch skill description by
word overlap with the request. It was discarded because it fails its own
counter-probe. Run against `OFR-TYPO3-UPGRADE-001`, a case whose fleet routes
to `typo3-extension-upgrade` in 23 of 29 trials, the matcher returns **nothing
matches**. An instrument that cannot find a match where one demonstrably exists
cannot be evidence that no match exists, and its top hit for a CI question was
a Figma handoff skill.

What follows is a reading of the 73 Netresearch skill descriptions in the
marketplace catalogue against each request. A reading is weaker evidence than a
measurement, which is why each row ends in an experiment or in a statement
about the catalogue rather than in a conclusion about agents.

## Case by case

| case | what the request asks for | a skill that claims it | what follows |
|---|---|---|---|
| `OFR-TYPO3-RELEASE-001` | prepare a release | `github-release` | **measured**: 0/6 → 6/6, p 0.002 |
| `OFR-TYPO3-CONSISTENT-001` and the two metadata cases | reconcile what an extension declares about supported versions | `typo3-conformance`, already in the fleet | routing, not composition — round two running |
| `OFR-TYPO3-RUNTIME-001` | find out why saving in a backend module does nothing | none | a gap in the catalogue |
| `CON-TYPO3-EXTBASE-001` | find properties Extbase cannot persist | none; `typo3-conformance` is nearest and is in the fleet | a gap, narrower |
| `OFR-GO-LDAP-001` | a timing side channel in a Go library | `security-audit` — **for PHP applications** | a scope gap, not a missing skill |
| `OFR-PY-CI-001` | decide whether a CI job's red exit status is right | `git-workflow` claims CI/CD pipelines; the fleet does not carry it | **testable now** |

## The three findings, in order of what can be done about them

**One is an experiment waiting to run.** `OFR-PY-CI-001` runs on fleet
`nr-general`, which carries three skills: assessment, harness, security audit.
None of them names continuous integration, workflows, exit statuses or GitHub
Actions. `netresearch/git-workflow-skill` does — "Git workflow best practices
for teams and CI/CD pipelines" — and it is not in the fleet. That is the same
shape as the release case exactly, and it is worth twelve trials.

**One is a scope gap worth reporting to the skill's owners.**
`security-audit` opens "Security audit patterns for **PHP** applications
following OWASP guidelines". The Go case asks a security question about a Go
library, and the fleet carries that skill plus `go-development`, whose
description covers project structure, error handling and concurrency and does
not mention security. The capability exists in the organisation and is scoped
to a language the case is not written in. No composition change available:
there is no Go security skill to add.

**Two are gaps in the catalogue, and no experiment fixes them.** Nothing among
the 73 skills claims debugging a running TYPO3 backend module, and nothing
claims Extbase persistence rules. For these two cases the equipped arm is the
unaided agent carrying luggage, and the benchmark should say so rather than
report them as a stack that chose not to help. The runtime case has 46 equipped
trials on record and zero invocations; that number is now interpretable.

## What this does not claim

That an agent *should* have loaded any of these. Routing is the agent's
decision and the measured rate is what it is. This document only establishes
which cases had something to route to, so a zero can be read as a statement
about the fleet where it is one, and about the agent where it is one.
