# OFR-TYPO3-RUNTIME-001 — recorded results

Four fleets, three trials each, against an installed TYPO3 13.4 instance; no
errored trials and no errored criteria. Case, agent (claude-code on
claude-opus-5), model, judge, rubric, environment image and trial count
identical; only the fleet differs.

| Fleet | What it is |
|---|---|
| `control` | Claude Code alone |
| `nr` | eight Netresearch skills |
| `companion` | the TYPO3 Dev Companion: twelve skills and its MCP server |
| `dev-mcp` | balatD/typo3-dev-mcp: its MCP server, no skills |

Both MCP servers answered in 3 of 3 trials of their arm.

## Quality — met out of 3 (mean)

| Dimension | control | nr | companion | dev-mcp |
|---|---|---|---|---|
| evidence | 3/3 (0.96) | 3/3 (1.00) | 3/3 (1.00) | 3/3 (0.88) |
| verification | 3/3 (0.85) | 3/3 (0.83) | 3/3 (0.83) | 3/3 (0.88) |
| authority | 3/3 (0.97) | 3/3 (1.00) | 3/3 (0.92) | 3/3 (0.83) |
| prioritization | 3/3 (0.94) | 2/3 (0.89) | 3/3 (1.00) | 3/3 (1.00) |
| unsupported_claims | 2/3 (0.78) | 1/3 (0.72) | 2/3 (0.78) | 2/3 (0.89) |
| outcome_quality | 2/3 (0.75) | 1/3 (0.75) | 2/3 (0.71) | 1/3 (0.71) |
| context_discovery | 3/3 (0.90) | 3/3 (0.88) | 3/3 (0.88) | **1/3 (0.69)** |
| skill_routing | 0/3 (0.36) | 0/3 (0.36) | 0/3 (0.39) | 0/3 (0.39) |

## Cost — per trial, agent side

Three trials, so every trial is shown. A median alone would be read as a
measurement here, and it is not one.

| | control | nr | companion | dev-mcp |
|---|---|---|---|---|
| tool calls (median) | 93 | 106 | 68 | 49 |
| wall time (median) | 1157 s | 1394 s | 967 s | 899 s |
| agent cost, each trial | 2.99 / 6.76 / 8.21 | 7.17 / 8.33 / 19.11 | 3.83 / 4.10 / 6.25 | 2.72 / 3.18 / 8.22 |
| range | $2.99–8.21 | $7.17–19.11 | $3.83–6.25 | $2.72–8.22 |

## What this shows

**The quality columns are flat, and that is the finding.** Every arm solves the
case. Every arm reaches the top mark on the mechanism. What separates the arms
is one trial here or there, which this repository's own comparison tool refuses
to call a result — and it refuses correctly: an earlier control-vs-nr run
showed `nr` ahead on two dimensions and did not reproduce when re-run.

This is a ceiling, not a tie. A case the base agent solves completely cannot
show what better tooling is worth, however good the tooling is. The same holds
for the upgrade case, where `control` widened the constraints and passed 719
tests on both TYPO3 lines at the first attempt.

**Cost does not separate them either, at this trial count.** The medians
suggest it does — `dev-mcp` at 47% of control, `companion` at 61%, `nr` at
123% — and the per-trial figures show why that reading fails: the spread
*inside* each arm swallows the difference between them. Control alone runs
from $2.99 to $8.21, a factor of 2.7 on identical inputs, and `dev-mcp`'s
range of $2.72–8.22 covers virtually the same ground.

Stated plainly because it was published the other way first: the median gap
was written up here as a 53% saving that independently replicated the vendor's
own figure. It does not. Three trials with that variance cannot carry the
claim, and the same one-trial caution applied to every quality column has to
apply to the cost column.

What survives is weaker and worth keeping: `companion` is the only arm whose
range is both narrow and low ($3.83–6.25), and `nr` the only one whose *whole*
range sits above control's median. Neither is a result yet. Cost is now the
only dimension with any headroom left on this case, which makes it the one
worth spending trials on.

The direction against the review case still stands on its own numbers: there
the same companion cost **three times** what control did. A tool that looks
cheap on a runtime question and expensive on a repository question is a
finding about where it fits, even before the runtime figure is settled.

**The arm with the fewest tool calls is also the least grounded.**
`context_discovery` is mechanical, not a judgement: it checks whether the agent
read the package manifest, the source, and the project's own documentation.
The `dev-mcp` arm read the project documentation in **none** of its three
trials. It asked the running system instead — the same behaviour that produces
its low call count.

Whether that is a defect depends on what the documentation holds that the
server cannot report: conventions, intent, known problems. On this case it cost
nothing measurable — `outcome_quality` is 0.71 against control's 0.75, inside
the noise. The honest statement is that the trade is real and this case does
not price it. A case whose answer lives in a `Documentation/` directory would.

**`skill_routing` carries no signal here.** No agent invoked a skill in any
arm, including the ones with eight and twelve available. That is not a routing
failure: none of the Netresearch skills covers runtime diagnosis, and the
conformance skill says nothing about Extbase property visibility, which is the
defect. There was nothing to reach for.

## The shared weakness

Two criteria of `outcome_quality` stay low in every arm. The substantive one is
`addressed_the_existing_damage`: the agents observe the orphaned row, state
that it collides with the unique key, and do not tell the developer to remove
it. A reader who applies only the code fix is left with a database that still
fails.

`accounted_for_the_silence` is near-uniform at the middle mark, and is recorded
as an open rubric question rather than a result — a criterion that returns the
same value almost every time is not telling the arms apart, and the judge's
reasoning suggests it rewards drawing a contrast rather than understanding one.

## Reproducing

```
./scripts/run-evaluation OFR-TYPO3-RUNTIME-001 --fleet control
./scripts/run-evaluation OFR-TYPO3-RUNTIME-001 --fleet nr
./scripts/run-evaluation OFR-TYPO3-RUNTIME-001 --fleet companion
./scripts/run-evaluation OFR-TYPO3-RUNTIME-001 --fleet dev-mcp
./scripts/compare jobs/<a> jobs/<b>
```

`nr-companion` exists as a fleet and is not in this table: the comparison was
narrowed to one stack per arm.

Several runs were lost to instrument failures before these numbers stood up —
a revoked session token reported as three bad trials, a companion arm that
would have run without its MCP server, and trials scored zero after dying on a
transport fault. All are recorded in
[docs/instrument-failures.md](../../../docs/instrument-failures.md).
