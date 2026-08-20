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
| `dev-mcp` | 0/2 | two failed tests; a third trial never called its server and is excluded |
| **`nr-full`** | **3/3** | — |

Both Netresearch arms completed the upgrade in every trial. The unaided agent
managed two of three.

`dev-mcp` read 1/3 here until 20 August 2026. The validity gate then found that
the one trial of the three that completed the upgrade is the one where the MCP
server was never called — an arm that consists of nothing but that server, in a
run indistinguishable from a control. Counted, it credited the tool with a
success achieved without it. That is the first result in this repository where a
difference rests on something the framework itself decides rather than on a
rubric.

**It reproduced.** A second, independent run of `control` against `nr` — three
fresh trials each, days apart, same task digest — returned the same counts:
2/3 and 3/3. Pooled, that is 6 of 6 against 4 of 6.

And it is still not established. Fisher's exact test on those pooled counts
gives a one-sided p of 0.23: the direction is consistent across two runs and
the sample is too small to carry it. What is worth saying is exactly that much,
which is why it is written here rather than on the front page as a headline.

The comparison script did not notice the reproduction, and that is a gap in the
script rather than in the result. Its separation test reads the graded
dimensions; the matrix outcome is the case's most valuable signal and does not
appear among them in a form the test can see.

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

## The deepening

`verification` separated completely in the discovery stage, so the comparison
moved to four trials per arm as designed. That stage died on the subscription's
rate limit and is not reported.

The re-run that replaced it — `control` against `nr`, three trials each — found
that `verification` no longer separates, while the mechanical outcome
reproduced exactly. Both facts belong in the same paragraph: a rubric dimension
that separates once and not again was noise, and an outcome that repeats across
independent runs is not.

## Reproducing

```
scripts/run-comparison OFR-TYPO3-UPGRADE-001 --arms control,nr,companion,dev-mcp,nr-full --seed 3
scripts/capability-ledger jobs/<job>
```
