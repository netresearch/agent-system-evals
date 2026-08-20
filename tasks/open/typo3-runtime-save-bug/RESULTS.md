# OFR-TYPO3-RUNTIME-001 — recorded results

Five fleets, three trials each, no errored trials and no errored criteria.
Measured 19 August 2026 on the rebuilt environment.

Everything recorded before that date is withdrawn, and replaced here rather
than corrected. The agent container had held `seed-reported-state.php`, whose
header described the mechanism this case asks the agent to establish, and two
trials were caught reading it. Both products were also installed for every arm,
so there was no clean control, and the comparison checked five fields where the
specification requires ten. See
[docs/instrument-failures.md](../../../docs/instrument-failures.md).

| Fleet | Skills delivered | MCP server reached |
|---|---|---|
| `control` | none | — |
| `nr` | 9 | — |
| `companion` | 12 | 3/3 trials, 3 calls |
| `dev-mcp` | none | 3/3 trials, 31 calls |
| `nr-full` | 13 | — |

## Quality — met out of three

Every arm solves the case. Nothing separates completely, so the comparison
stopped after the discovery stage: three trials can say "something might be
here", and nothing here says it.

## Cost — every trial

| | control | nr | companion | dev-mcp | nr-full |
|---|---|---|---|---|---|
| agent cost | 4.20 / 5.03 / 10.46 | 3.63 / 4.27 / 6.21 | 4.43 / 4.88 / 6.06 | 3.19 / 6.23 / 13.37 | 6.53 / 7.43 / 9.28 |
| tool calls | 60 / 70 / 123 | 54 / 66 / 81 | 65 / 70 / 86 | 60 / 85 / 151 | 85 / 104 / 121 |

**No pair separates.** Control alone spans $4.20 to $10.46 — a factor of 2.5 on
identical inputs — and every other arm lies inside that. No cost claim is made
from this case, and no median is quoted: a median of three inside a spread this
wide reads as a measurement and is not one.

## The finding is what was not used

Across all fifteen trials, **not one skill was invoked** — with nine available,
with twelve, with thirteen. Both MCP arms did reach their servers, so the
capabilities were demonstrably present; the skills simply went untouched.

Set against the review case, measured the same week on the same stack, that is
the result:

| | review case | this case |
|---|---|---|
| skills invoked | exactly one, in every trial | none, in any trial |
| cost against control | ranges separate, roughly halved | ranges overlap |

The difference is the task. A review has a procedure to adopt — the conformance
skill — and adopting it halves the context the agent carries through the work.
A runtime diagnosis has no procedure on offer here: none of the nine or
thirteen skills covers it, and the agent boots the framework itself instead,
which it did in eight of nine trials without an MCP in the earlier measurement.

Skills and servers are offers. This case shows what an offer that does not fit
the task costs and returns: `nr-full`, the largest set, is the dearest arm here
and the cheapest on the review case.

## Reproducing

```
scripts/run-comparison OFR-TYPO3-RUNTIME-001 --arms control,nr,companion,dev-mcp,nr-full --seed 1
scripts/capability-ledger jobs/<job>
```
