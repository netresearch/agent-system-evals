# OFR-TYPO3-EXT-001 — recorded results

Four fleets, three trials each, no errored trials and no errored criteria.
Case, agent (claude-code on claude-opus-5), model, judge, rubric, environment
and trial count identical; only the fleet differs.

| Fleet | What it is |
|---|---|
| `control` | Claude Code alone |
| `nr` | eight Netresearch skills |
| `companion` | the TYPO3 Dev Companion: twelve skills and its MCP server |
| `nr-companion` | both stacks together |

Jobs recorded before the fleet rename carry `fleet: main` in their snapshot;
that is the fleet now called `nr`.

## Quality — met out of 3 (mean)

| Dimension | control | nr | companion | nr-companion |
|---|---|---|---|---|
| skill_routing | 0/3 (0.33) | 3/3 (1.00) | 3/3 (1.00) | 3/3 (1.00) |
| prioritization | 3/3 (0.94) | 3/3 (0.94) | 3/3 (1.00) | 3/3 (1.00) |
| context_discovery | 3/3 (1.00) | 3/3 (0.92) | 3/3 (1.00) | 3/3 (1.00) |
| outcome_quality | 3/3 (1.00) | 3/3 (1.00) | 3/3 (1.00) | 3/3 (1.00) |
| evidence | 3/3 (0.88) | 3/3 (0.88) | 3/3 (1.00) | 3/3 (1.00) |
| verification | 3/3 (0.88) | 3/3 (0.79) | 3/3 (0.88) | 3/3 (0.88) |
| unsupported_claims | 1/3 (0.72) | 0/3 (0.61) | 2/3 (0.78) | 2/3 (0.89) |
| authority | 0/3 (0.50) | 0/3 (0.36) | 1/3 (0.53) | 0/3 (0.53) |

## Cost — median per trial, agent side

| | control | nr | companion | nr-companion |
|---|---|---|---|---|
| tool calls | 27 | **18** | 58 | 70 |
| wall time | 260 s | **156 s** | 576 s | 579 s |
| input tokens | 1,304,269 | **517,883** | 4,052,407 | 4,823,265 |
| agent cost | $2.16 | **$0.91** | $4.95 | $5.59 |

## What this shows

**All four produce equally usable reviews.** `outcome_quality` is 3/3
everywhere, and six of the eight dimensions are flat across the four.

**The difference is effort, and it is large.** A factor of six in cost and
nearly four in wall time separates the cheapest configuration from the dearest.
The Netresearch stack is the cheapest — 2.4× cheaper than the unaided agent and
5.4× cheaper than the companion — while producing output the rubric cannot
distinguish from theirs.

**Two dimensions stay weak everywhere.** No fleet reaches source authority
reliably. `unsupported_claims` is weakest on `nr` (0/3) and strongest on
`nr-companion` (2/3, 0.89), which is better than either stack alone — evidence
that the two compose rather than collide, on this case.

**The most expensive configuration buys the least.** `nr-companion` costs six
times what `nr` does and reaches no dimension that `nr` does not, apart from
`unsupported_claims`.

## What this does not show

One case, one agent, one model, three trials per fleet. `skill_routing` for
`control` is partly definitional: with no injected skills there is less to
route to, though the judge counted Claude Code's own entry points as available.
Differences of one trial are within noise at this sample size.

## Corrections

The first published version of these numbers was wrong in two dimensions.
Nine criteria across three jobs had hit the judge timeout, and RewardKit
records a timed-out judge as 0.0. Control's prioritization was reported as 0.61
against 0.94, and called a real improvement attributable to the stack; measured
without the timeout it is 0.94 on both sides and the improvement does not
exist. Control's `unsupported_claims` was reported as 0.50 and is 0.72.

Six instrument failures were found and fixed while producing this table, every
one of them returning a plausible number rather than an error. They are listed
in [docs/instrument-failures.md](../../../docs/instrument-failures.md).
