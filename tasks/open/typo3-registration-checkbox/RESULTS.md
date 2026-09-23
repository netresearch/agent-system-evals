# OFR-TYPO3-REGISTRATION-001 — recorded results (Haiku)

## First measurement, 23 September 2026: level, and the stack is never reached for

`experiments/OFR-TYPO3-REGISTRATION-001-20260923-072029.json`, seed 5099,
Haiku 4.5, benchmark 10.7.0. Twelve trials, twelve valid, bare (`control`)
against `nr`, declared on `mechanical_outcome` with `--run-out`, six per arm.

The case had been in the repository since 30 August without a result. Its one
earlier attempt stopped with "arm control failed in round 1 block 1" — the
runner's fail-closed branch, taken when it cannot resolve a job path — while
the three trials of that attempt had completed on disk with rewards. The
environment was sound; the stop was the runner's. The first launch of this
round also stopped at once, because the Docker daemon on the measuring machine
was not running; it was started and the round relaunched unchanged.

| arm | passed the case's check | `skill_invoked` | agent cost, six trials | agent steps |
|---|---|---|---|---|
| `control` | 2/6 | 0/6 | $0.10, $0.24, $0.27, $0.27, $0.33, $0.38 | 18–52 |
| `nr` | 2/6 | 0/6 | $0.15, $0.21, $0.31, $0.42, $0.44, $0.44 | 24–58 |

**Level on the outcome, and no skill loaded in any trial.** Fisher p 1.000 on
the declared endpoint; `outcome_quality` 2/6 on both arms; cost median $0.27
→ $0.37, p 0.394, exploratory. With nothing loaded, the `nr` arm is the bare
model plus eight skills it never opens, and the result reads that way.

**The ceiling the README expected is not here.** The case was admitted as
"near its ceiling" on a pre-use check of three control trials, two of which
fixed it. At six per arm and the current environment the control arm reads
2/6. The earlier figure was three trials; this one is six, and the case has
more room than its admission assumed — which also means an equipped arm could
now show an improvement, had it loaded anything.

**Every failure is the same test.** All eight failing trials, four per arm,
fail `requiredCheckboxGroupWithNothingTickedIsAnError`: the agent fixes the
single required checkbox the maintainer's report names and leaves a checkbox
*group* with nothing ticked — an empty array rather than an empty string —
still passing. The four passing trials handled both shapes. That is the
defect's second input shape, the one the report does not spell out.

**Where this case sits in the benchmark.** It joins the cases whose request is
a report of wrong behaviour — the resize, calendar and runtime bugs — on which
no skill has been loaded in any trial under this model. The routing rule
measured elsewhere holds here: a description reaches Haiku when the request
names a domain or an artefact ("review", "upgrade", a file to write), and not
when it describes something that is broken. `typo3-testing`'s description
names this situation — a reported defect to be reproduced as a failing test —
and was not loaded on the resize case either (0/24).

**What would move this case**, stated and not started: the one step the
passing trials took and the failing ones did not is testing the empty-group
input. That is the testing skill's rule — reproduce the report as a failing
test, then vary its input — and it never reaches this model through a
description. A lever for this case has to reach the agent before the skill
does, or not through the skill.
