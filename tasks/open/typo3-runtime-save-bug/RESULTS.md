# OFR-TYPO3-RUNTIME-001 — recorded results

Four fleets, three trials each, against an installed TYPO3 13.4 instance; no
errored trials and no errored criteria. Case, agent (claude-code on claude-opus-5),
model, judge, rubric, environment image and trial count identical; only the
fleet differs.

| Fleet | What it is |
|---|---|
| `control` | Claude Code alone |
| `nr` | eight Netresearch skills |
| `companion` | the TYPO3 Dev Companion: twelve skills and its MCP server |
| `nr-companion` | both stacks together |

## Quality — met out of 3 (mean)

| Dimension | control | nr | companion | nr-companion |
|---|---|---|---|---|
| evidence | 3/3 (1.00) | 3/3 (1.00) | 3/3 (0.96) | 3/3 (1.00) |
| prioritization | 3/3 (1.00) | 3/3 (1.00) | 3/3 (0.94) | 3/3 (1.00) |
| verification | 3/3 (0.94) | 3/3 (0.92) | 3/3 (0.85) | 3/3 (0.85) |
| authority | 3/3 (1.00) | 3/3 (0.89) | 2/3 (0.81) | 3/3 (0.92) |
| context_discovery | 3/3 (0.88) | 3/3 (0.90) | 3/3 (0.85) | 3/3 (0.88) |
| unsupported_claims | 1/3 (0.78) | 1/3 (0.67) | 2/3 (0.83) | 2/3 (0.83) |
| outcome_quality | 2/3 (0.71) | 0/3 (0.62) | 0/3 (0.62) | 2/3 (0.71) |
| skill_routing | 0/3 (0.33) | 0/3 (0.42) | 0/3 (0.39) | 0/3 (0.33) |

Both companion arms reached the MCP server in all three trials, and both used
exactly one of its tools: `typo3_project_describe`.

## Cost — median per trial, agent side

| | control | nr | companion | nr-companion |
|---|---|---|---|---|
| tool calls | 96 | 94 | **71** | 69 |
| wall time | 1434 s | 1337 s | **982 s** | 1127 s |
| input tokens | 10,868,864 | 10,425,477 | **5,417,815** | 5,997,996 |
| agent cost | $8.48 | $8.09 | **$4.83** | $5.00 |

Note the direction: on the review case the companion cost three times what
`control` did. Here it costs half. A tool that pays for itself on a runtime
question and not on a repository question is a finding about *where* it fits,
not about whether it is good.

## What this shows

**Every agent found the root cause, in every fleet.** `identified_the_mechanism`
scored the top mark in 12 of 12 trials, and so did
`a_developer_could_act_on_this`. The agents did not read it off the source:
they ran the repository call inside the TYPO3 bootstrap, produced
`Cannot access private property`, applied the change provisionally, re-ran the
save path, read the written row back out of the database, and reverted. The
merged fix (PR #101) changes exactly those properties from `private` to
`protected`.

**No tool stack made a measurable difference.** Every dimension that separates
the four arms does so by one or two trials, which this repository's own comparison
tool refuses to call a finding. An earlier run of `control` and `nr` did show
`nr` ahead on two dimensions; re-run on the corrected image, it did not
reproduce. That is what a one-trial difference is worth.

**The one reproducible weakness is shared by all of them.** Two criteria almost
never reached the top mark, across twelve trials and four fleets:

| Criterion | control | nr | companion | nr-companion |
|---|---|---|---|---|
| `accounted_for_the_silence` | 2, 2, 2 | 2, 2, 2 | 2, 2, 2 | 2, 2, **3** |
| `addressed_the_existing_damage` | 2, 1, 2 | 1, 1, 1 | 1, 1, 1 | 2, 1, 1 |

The second is a substantive gap and the judge is specific about it: the agents
*observe* the orphaned row, and state that it collides with the unique key, but
they do not tell the developer to remove it. A reader who applies only the code
fix is left with a database that still fails. Twelve trials, four tool stacks,
same omission — nine of them scoring the lowest mark available.

The first is a rubric question as much as an agent one, and is recorded as open
rather than as a result. The criterion asks whether both behaviours were
accounted for — the silent first save and the loud later one — and the judge
answers, eleven times out of twelve, that both are explained but not contrasted
as a sequence. One trial did earn the top mark, so the criterion is not capped;
it is simply near-uniform, and a criterion that returns the same value that
often is not telling the arms apart. Whether it measures understanding or
presentation needs settling before it carries weight.

**`skill_routing` carries no signal here.** No agent invoked a skill in any
arm, including the ones with eight or twelve available. That is not a routing
failure: none of the Netresearch skills covers runtime diagnosis, and the
conformance skill says nothing about Extbase property visibility, which is the
defect. There was nothing to reach for. It follows that any difference between
`control` and `nr` on this case cannot be attributed to skill *use*.

## Reproducing

```
./scripts/run-evaluation OFR-TYPO3-RUNTIME-001 --fleet control
./scripts/run-evaluation OFR-TYPO3-RUNTIME-001 --fleet nr
./scripts/run-evaluation OFR-TYPO3-RUNTIME-001 --fleet companion
./scripts/run-evaluation OFR-TYPO3-RUNTIME-001 --fleet nr-companion
./scripts/compare jobs/<a> jobs/<b>
```

Two runs were lost to instrument failures before these numbers stood up — a
revoked session token reported as three bad trials, and a companion arm that
would have run without its MCP server. Both are recorded in
[docs/instrument-failures.md](../../../docs/instrument-failures.md).
