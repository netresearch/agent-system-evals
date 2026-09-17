# OFR-TYPO3-CALENDAR-001 — recorded results

## Round 37, 17 September 2026 — the fleet neither helps nor harms

`experiments/OFR-TYPO3-CALENDAR-001-20260917-142859.json`, seed 4311, Haiku
4.5, benchmark 8.0.1. Six trials, six valid, `control` against `nr`.

| | `control` | `nr` |
|---|---|---|
| `calendar: ok` | 1/3 | 1/3 |
| `Skill(` calls | 0/3 | 0/3 |

Fisher exact p 1.000. The runner stopped after the discovery round.

**The round was run to settle a suspicion, and it settles it against me.**
The ledger's older rows read `control` 4 of 13 against `nr` 2 of 9, which looks
like a fleet that costs its arm something. Those rows are three separate days
in late August, measured against a different benchmark version — not a
comparison. Measured as one, on one day, with blocks and a declared endpoint,
the two arms are indistinguishable.

**What the case does show is that it is passable and rarely passed.** One trial
in three, in both arms, on a defect about daylight saving. That is not a case
nobody can solve and not one anybody solves reliably; it is the shape a case
has when the model can do it and usually does not.

## Nothing was invoked, and this case is not alone

`skill_invoked` is 0 of 3 in the equipped arm, and 0 of 12 across every
recorded trial of this case. `scripts/invocation-census` puts that in context:

| cases that route | cases that never do |
|---|---|
| `OFR-TYPO3-EXT-001` 41/42, `OFR-TYPO3-UPGRADE-001` 173/179 | this case 0/12, `OFR-TYPO3-RESIZE-001` 0/15, `OFR-TYPO3-RUNTIME-001` 0/52, `OFR-PY-CI-001` 0/11, `OFR-TYPO3-METADATA-001` 0/7 and `-BARE` 0/3, `OFR-GO-LDAP-001` 0/5, `CON-TYPO3-EXTBASE-001` 0/6 |

Eight cases, **0 of 111 equipped trials**. Two cases carry almost all of the
routing this benchmark has ever recorded, and both of them are requests that
name what they want as a noun: review this extension, upgrade this extension.
The eight are reports of something being wrong.

That is a measurement about the descriptions in the fleet, not about the cases.
A skill that never opens is measured as the base model with extra installation
cost, which is what most rows of this benchmark have been. The one case where
moving words in a description turned this around —
`OFR-TYPO3-CONSISTENT-001`, 0 of 27 to 11 of 12 — did it by putting the
request's own artefacts in the opening clause. `OFR-TYPO3-RESIZE-001` shows the
limit of that move: a description written for the reported-defect shape did not
route either.
