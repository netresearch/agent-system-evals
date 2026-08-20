# OFR-TYPO3-EXT-001 — recorded results

Four fleets, three trials each, no errored trials and no errored criteria.
Measured 19 August 2026 on the rebuilt environment: the instance is served, the
control arm provisions nothing, and the agent's sandbox was audited for
evaluation machinery before any trial ran.

Everything recorded before that date is withdrawn. The environment had leaked
the case's own files into the agent container, both products were installed for
every arm including control, and the comparison checked five fields where the
specification requires ten. None of those numbers describe this benchmark.

| Fleet | What it is | Skills delivered |
|---|---|---|
| `control` | Claude Code alone | none |
| `nr` | eight Netresearch skill repositories | 9 |
| `companion` | the TYPO3 Dev Companion, skills and MCP server | 12 |
| `nr-full` | the deployed Netresearch setup plus its toolchain | 13 |

`dev-mcp` does not appear: the target declares TYPO3 `^12.4`, so its developer's
instance is a v12.4 one, and that package requires `^13.4`. The fleet states
this as a version floor and the case is exempt.

Thirteen skills against twelve repositories is not a discrepancy — a skill
repository may ship more than one.

## Quality — met out of three

| Dimension | control | nr | companion | nr-full |
|---|---|---|---|---|
| context_discovery | 3/3 | 3/3 | 3/3 | 3/3 |
| evidence | 3/3 | 3/3 | 3/3 | 3/3 |
| prioritization | 3/3 | 3/3 | 3/3 | 3/3 |
| outcome_quality | 3/3 | 3/3 | 3/3 | 3/3 |
| verification | 2/3 | 3/3 | 3/3 | 2/3 |
| unsupported_claims | 1/3 | 0/3 | 0/3 | 0/3 |
| authority | 0/3 | 0/3 | 2/3 | 1/3 |
| capability_selection | n/a | 0/3 | 0/3 | 0/3 |

Nothing here separates completely, so nothing here is a finding. `authority`
is weak in every arm — the dimension asks whether each claim came from the
source that owns that fact, and no configuration reliably manages it.

`capability_selection` is n/a for control by construction: an arm offered
nothing had no selection to get right.

## Cost — every trial, not a median

| | control | nr | companion | nr-full |
|---|---|---|---|---|
| agent cost | 2.21 / 2.80 / 3.54 | **1.27 / 1.40 / 1.55** | 4.52 / 5.83 / 9.26 | **1.08 / 1.34 / 1.43** |
| input tokens (M) | 1.39 / 1.79 / 3.29 | **0.80 / 0.93 / 1.11** | 3.77 / 5.95 / 10.60 | **0.73 / 0.88 / 1.00** |
| tool calls | 32 / 34 / 41 | 24 / 31 / 34 | 52 / 63 / 69 | 27 / 27 / 35 |

**The cost ranges do not overlap.** The dearest Netresearch run costs less than
the cheapest unaided one — $1.55 against $2.21 — and the same holds for
`nr-full` at $1.43. The companion runs the other way, its cheapest trial at
$4.52 above control's dearest at $3.54.

Complete separation of two groups of three happens by chance one time in
twenty. That is the strongest statement this sample size can make: enough to
act on, not enough to call established, and the reason the comparison script
deepens where it sees one.

**The saving is not in doing less.** Tool calls overlap — 24 to 34 against 32
to 41 — while input tokens separate cleanly at roughly half. The agent takes a
similar number of steps and carries much less context through them. A procedure
it has adopted is one it does not have to reconstruct.

## What was used

In all three `nr` and `nr-full` trials the agent invoked exactly one skill,
`typo3-conformance`, and none of the other eight or twelve. The companion arms
reached exactly one of theirs, `typo3-extension-conformance`, and called its
MCP server 57 times.

So the halved cost belongs to one skill being adopted, not to a stack being
present. The other skills were carried and never opened — and on this case that
still costs less than not having them.

## Reproducing

```
scripts/run-comparison OFR-TYPO3-EXT-001 --arms control,nr,companion,nr-full --seed 2
scripts/capability-ledger jobs/<job>
scripts/compare jobs/<a> jobs/<b>
```
