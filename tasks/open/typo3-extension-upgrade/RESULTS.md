# OFR-TYPO3-UPGRADE-001 — recorded results

Five fleets, three trials each, no errored trials. Measured 20 August 2026 on
the rebuilt environment, first results this case has ever produced.

This is the only case with **mechanical ground truth**. The verifier does not
ask a judge whether the work looks right: it takes the tree the agent left,
pins the dependency matrix to each TYPO3 line in turn, resolves it and runs the
extension's own test suite. An arm either produced something that installs and
passes on both lines, or it did not.

## Did the upgrade actually work

| Fleet | Trials complete | What failed in the rest |
|---|---|---|
| `control` | 2/3 | one tree resolved on 14.3 and failed its tests |
| **`nr`** | **3/3** | — |
| `companion` | 0/3 | one would not resolve at all, two failed tests |
| `dev-mcp` | 1/3 | two failed tests |
| **`nr-full`** | **3/3** | — |

Both Netresearch arms completed the upgrade in every trial. The unaided agent
managed two of three. That is the first result in this repository where a
difference rests on something the framework itself decides rather than on a
rubric — and with three trials it is a signal to spend more on, not a finished
claim.

## What was used

| Fleet | Skill invoked | MCP calls |
|---|---|---|
| `control` | — | — |
| `nr` | `typo3-extension-upgrade`, 3/3 | — |
| `companion` | `typo3-extension-upgrade`, 2/3 | 38 across 3/3 |
| `dev-mcp` | — | 17 across 2/3 |
| `nr-full` | `typo3-extension-upgrade`, 3/3 | — |

**Those two skills share a name and are not the same skill.** The Netresearch
set and the TYPO3 Dev Companion each ship one called `typo3-extension-upgrade`,
for the same job, with different content. The capability ledger qualifies skill
names by fleet for exactly this reason; read across arms, the row would have
shown two different things as one.

Unlike the runtime case, skills are reached here — and by the arms that
completed the work. Unlike the review case, reaching one did not make the run
cheaper.

## Cost — every trial

| | control | nr | companion | dev-mcp | nr-full |
|---|---|---|---|---|---|
| agent cost | 10.88 / 34.04 / 38.47 | 20.18 / 22.81 / 26.58 | 1.23 / 14.92 / 15.40 | 24.72 / 33.11 / 35.42 | 28.60 / 29.32 / 31.03 |
| tool calls | 128 / 265 / 271 | 180 / 210 / 229 | 24 / 145 / 163 | 223 / 272 / 275 | 222 / 248 / 250 |

An order of magnitude more expensive than the other cases, and no pair
separates: control alone spans $10.88 to $38.47. The companion's cheapest trial
at $1.23 is the one that produced a tree which would not resolve — cheap
because it stopped, which is why cost is only readable beside the outcome
column.

## The deepening did not finish

`verification` separated completely in the discovery stage, so the comparison
moved to four trials per arm as designed. That stage died on the subscription's
rate limit — four errored trials in each of four arms — and is not reported
here. The three-trial figures above stand on their own; the question that
triggered the deepening is still open.

## Reproducing

```
scripts/run-comparison OFR-TYPO3-UPGRADE-001 --arms control,nr,companion,dev-mcp,nr-full --seed 3
scripts/capability-ledger jobs/<job>
```
