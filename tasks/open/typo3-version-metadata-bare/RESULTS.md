# OFR-TYPO3-METADATA-001-BARE — recorded results

Two fleets, three trials each, six of six valid. Measured 21 August 2026 on
**`claude-haiku-4-5-20251001`**, benchmark version 0.8.0.

## What the run was

`scripts/run-comparison OFR-TYPO3-METADATA-001-BARE --arms control,nr --primary consistency --model claude-haiku-4-5-20251001 --seed 51`

Randomised blocks, `consistency` declared before the first trial. The runner
stopped after the discovery round.

Experiment record: `experiments/OFR-TYPO3-METADATA-001-BARE-20260821-140311.json`.

## The fleet comparison, which is not this case's question

| | control | nr |
|---|---|---|
| `consistency` met | 2/3 | 2/3 |
| criteria behind it | 19 met / 4 partial / 1 not met | 15 met / 5 partial / 4 not met |
| Cliff's delta | — | −0.56 |
| permutation p | — | 0.300 |

| trial | tool calls | `consistency` |
|---|---|---|
| control 1 | 17 | 0.67 |
| control 2 | 10 | 0.92 |
| control 3 | 8 | 0.92 |
| nr 1 | 9 | 0.83 |
| nr 2 | 12 | 0.83 |
| nr 3 | 5 | 0.38 |

Both arms clear the threshold twice in three. The equipped arm's spread is the
wider one, on the strength of a single trial at 0.38 that made five tool calls —
the fewest in the series. At three trials per arm that is one observation, not a
tendency, and the criteria line leaning against the equipped arm rests on it.

Zero `Skill(` calls in all three equipped trials, which is now four cases in a
row on this model.

## What this case is actually for

The variable here is the **repository**, not the fleet. This is
`OFR-TYPO3-METADATA-001` with the target's agent-facing scaffolding removed at
build time — five `AGENTS.md` files, the Copilot instructions, `CONTRIBUTING.md`
and the rendered `Documentation/`. The code, the tests, the CI workflows and
both version declarations are untouched.

The question is what that scaffolding is worth, and answering it means holding
the fleet constant and comparing prepared against bare, which
`scripts/compare --variable repository` exists to do.

**That comparison is not in this document yet, and the reason is worth
recording.** The prepared case ran on 20 August under benchmark 0.6.2. The
shared verifier library changed on 21 August, so the two runs carry different
rubric digests and `scripts/compare` refuses them:

```
these runs were not graded alike:
  - rubric_digest: '4c8294c62d00a708' vs 'a39c71d42692ad28'
```

That refusal is the instrument working. Two numbers produced by two rubrics are
not a difference between repositories, and nothing about the output would have
looked wrong. Two of the six prepared trials did score lower under the current
rubric, so the refusal was not a formality.

The regrade cost judge calls and no agent time, which is the whole argument for
`environment_mode = "separate"`. It then exposed a second defect: the validity
gate discarded every regraded job as `INVALID_AGENT: agent phase never
finished`, because a regrade starts no agent and Harbor has no finish time to
stamp. Recorded as instrument failure 20.

## Prepared against bare, which is the question

With both sides graded alike, and `scripts/compare` taught to pool the three
jobs that make up one arm of a block series:

| | prepared | bare |
|---|---|---|
| `consistency` met, control | 3/3 | 2/3 |
| `consistency` met, nr | 3/3 | 2/3 |

Both arms drop by one trial, independently, in the same direction. That is more
than either arm says alone and still much less than a finding: each side is
three trials, and a one-trial difference is inside the spread a stochastic agent
produces on its own. `compare` says so in its own output — *re-run before
treating any of these as a finding* — and it is right.

What can be said is narrower and worth stating: removing five `AGENTS.md` files,
the Copilot instructions, `CONTRIBUTING.md` and the rendered documentation did
not stop either arm from reconciling the two declarations in most trials. The
scaffolding is not what makes this task solvable.

```
scripts/compare --variable repository \
    jobs/rg-OFR-TYPO3-METADATA-001-nr-20260820-204946,jobs/rg-…-205645,jobs/rg-…-210355 \
    jobs/OFR-TYPO3-METADATA-001-BARE-nr-20260821-140311,…-141150,…-141938
```

## Cost

| | control | nr |
|---|---|---|
| agent cost per trial | 0.04 / 0.05 / 0.09 | 0.02 / 0.05 / 0.05 |
| input tokens | 229.7k / 256.6k / 481.8k | — |
| tool calls | 8 / 10 / 17 | 5 / 9 / 12 |

Medians identical to the cent, Cliff's delta −0.11, p 1.000. Exploratory.

## Reproducing

```
scripts/run-comparison OFR-TYPO3-METADATA-001-BARE --arms control,nr \
    --primary consistency --model claude-haiku-4-5-20251001 --seed 51
scripts/analyze experiments/OFR-TYPO3-METADATA-001-BARE-20260821-140311.json
```
