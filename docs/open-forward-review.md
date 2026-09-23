# Open Forward Review — normative specification

This document defines what an Open Forward Review (OFR) is and what a case must
satisfy to enter the benchmark. It is normative: a case that violates a MUST is
not an Open Forward Review, whatever else it may be worth.

## 1. The question

An Open Forward Review answers one question:

> Does the Netresearch agent engineering stack shorten the path from a
> realistic, deliberately underspecified request to a defensible result — in
> agent time, tool calls and tokens — against the same model working bare?

A frontier model reaches most answers eventually. The stack exists to make it
reach them sooner and for less: a skill is a shortcut before it is an
explanation, and where a step can be a script it is not a paragraph. The review
therefore measures two things and reports both. Whether the job got done is the
floor — the case's mechanical outcome where it has one, the judged dimensions
where it does not. What it cost to get there is the point — `cost`,
`input_tokens` and tool calls, each a declarable endpoint under §8. A stack that
reaches an outcome the bare model never reaches has earned its cost; one that
reaches the same outcome for more has not; one that reaches it for less is what
this repository exists to find and to keep.

It measures the behaviour of the *whole system* — agent, model, skills,
harness, canonical sources — not the correctness of any one skill, and it
measures it under one shape of session: **one request, one cold start, one run
to a result** under the case's timeout. Long sessions, several tasks in one
context, requirements that move under the agent — none of that is measured
here, and a result from here says nothing about it. Single-skill correctness
belongs in that skill's own eval; a specific known failure mode belongs in a
contract eval under `tasks/contracts/`.

## 2. The prompt

**MUST** be phrased as a colleague would phrase it, and **MUST NOT** name the
method.

Acceptable:

```
Review this TYPO3 extension and tell me what needs attention.
```

Not acceptable:

```
Run automated-assessment, then typo3-conformance. Read AGENTS.md. Check
composer.lock. Run PHPStan and report Fluid 5 incompatibilities.
```

The second prompt measures instruction following. That is a real property, but
it is not this one, and a benchmark that conflates them will report a healthy
score for a system whose routing is broken.

Concretely, the prompt **MUST NOT** mention:

- the TYPO3 (or other framework) version to assume
- any skill, by name or by description
- any tool, command, or file to inspect
- any category of finding the reviewer is expected to produce
- the existence of `AGENTS.md`, documentation, tests, or CI

## 3. The target

**MUST** be a real repository at a pinned commit SHA. Not a branch, not a tag
that can move, not a constructed fixture.

**MUST NOT** contain defects introduced for the benchmark. Synthetic defects are
the defining feature of a contract eval and they change what is being measured:
an injected bug has a known location and a known fix, so the case silently
acquires the findings checklist that section 2 forbids.

The strongest targets are **historical snapshots**: a commit immediately before
a real improvement landed. The later change is then available to the verifier
as one input to ground truth, without ever having been visible to the agent. See
[ADR 0005](adr/0005-holdout-cases.md) for why that ground truth stays
verifier-side.

## 4. Known concerns

A case may — and normally should — record what an experienced reviewer knows
about the target. That record **MUST** be encrypted, in
`expectations/<case-id>.md.enc` (see `expectations/README.md`), and **MUST
NOT** be present in:

- the agent's workspace or environment image
- the instruction
- any injected skill
- any file the agent can reach over the network
- **any plaintext file in this repository**, whatever directory it sits in

The last line was added on 20 August 2026, after the previous requirement —
"verifier-side only" — turned out to be satisfied by files committed in
plaintext in a public repository. Keeping expectations out of the agent's
container is isolation; it is not secrecy, and the two were being used
interchangeably.

Violating this does not merely inflate a score, it destroys the case
permanently, because the leaked expectation cannot be un-learned by the skills
that were exposed to it — or by a model trained on the repository.

## 5. Evidence

Grading **MUST** rest only on observable behaviour:

- the trajectory (messages, tool calls, commands, observations)
- the resulting workspace state and git diff
- collected artifacts and command output
- the final response

Private reasoning is **MUST NOT** be graded even where a harness exposes it. An
agent that reaches a defensible result by an unstated route has done the job;
one that narrates excellent intentions and does nothing has not. Grading
reasoning rewards the second.

## 6. Verifier isolation

The verifier **MUST** run with `environment_mode = "separate"`. Two reasons, and
the second is the one that bites:

1. The agent must not be able to influence its own grading.
2. Harbor can only regrade recorded trials whose verifier resolved to
   `separate`. A case that grades in-place is stuck with the rubric it was first
   run under, and every rubric improvement costs a full re-run.

## 7. Repetition

A single run is an anecdote. Evaluation **MUST** report at least three
independent trials per variant, as a count, not a mean:

```
verification   2/3
```

Reporting `0.667` implies a precision the sample size does not support.

## 8. A/B discipline

When comparing two variants, everything except the variable under study **MUST**
be held constant: target SHA, prompt, environment image, agent, model, judge
model, rubric digest, resource limits, network policy, trial count.

The variable is **declared**, not inferred. `scripts/compare --variable` and
`scripts/analyze --variable` take one of:

| Variable | What differs | What is held |
|---|---|---|
| `fleet` (default) | the provisioned stack | everything else, including the model |
| `model` | the agent's model | the fleet, the judge, the rubric |
| `repository` | the target's agent-facing scaffolding | the fleet and the case's identity |

An agent-model comparison is a legitimate experiment and asks a different
question from a fleet comparison: not whether the stack helps, but whether what
it adds depends on how strong the model underneath is. The judge stays where the
rubric pins it, so the grading instrument does not move with the thing being
graded.

Until 20 August 2026 there was no declaration and only `fleet` existed. That
made every other experiment either impossible or silently wrong: `compare`
refused a model pair outright, and `analyze` — which checked nothing at all —
pooled one without comment. The careful tool blocked what the sloppy one
allowed.

The judge **MUST NOT** be told which variant it is grading, and **MUST NOT** be
able to work it out. Telling it that one side is "the improved skill set" is a
request for the answer, not a measurement — but so is handing it a transcript
that names the arm's own skills.

That was the state until 20 August 2026: the rubric asked the judge not to
infer the variant, and `scripts/judge-blinding` then measured 23 to 147
mentions of an arm's own capabilities per trial in the text the judge reads.
Every dimension except `capability_selection` is now judged from a transcript
whose capability names are replaced by stable pseudonyms; that dimension asks
*which* capability was chosen and needs the names.

The residual is measured rather than assumed. After neutralisation the literal
test is clean, and a leave-one-out nearest-centroid classifier still recovers
the arm in 6 of 18 recorded transcripts against a chance rate of 1 in 6 —
p = 0.065, which is suggestive and not established at that sample size. So:
redaction removes what a judge could read; it does not remove how an arm
writes. Any claim that grading here is blind should say the first and not the
second.

### Ablations

A fleet changes several things at once, so a difference it produces belongs to
the fleet and to no component in it. Where a component question is worth
answering, an **ablation fleet** states its difference from a parent and
inherits the rest:

```yaml
name: nr-minus-conformance
derives_from: nr
without:
  - netresearch/typo3-conformance-skill
```

Derived rather than copied on purpose. A copy still names the parent's old skill
versions on the day the parent moves, and the arm then measures two changes
while reporting one. Removing a skill the parent does not carry is refused,
because an ablation that ablates nothing reads as a component that changes
nothing.

### A zero invocation count is ambiguous

`capability_selection` and the raw count of `Skill(` calls are read as evidence
about routing. They are only that once the fleet's contents have been checked
against the task, because a zero has three causes and they are findings about
different things:

| the capability was | what the zero says |
|---|---|
| on offer and not selected | a routing result — about the agent and the skill's description |
| not on offer | a composition result — about the fleet manifest |
| not needed | nothing; the task did not call for one |

A case **MUST** record, in its README, what capability its task plausibly needs
and whether the fleet carries it. Without that line the count cannot be read at
all, and the failure is silent: a fleet missing the relevant skill produces the
same zero as an agent that ignored it.

This was written after publishing the opposite. Six of nine cases in the August
2026 Haiku sweep recorded zero invocations, and the conclusion drawn — that
routing keys on the vocabulary of the request rather than on where the work
turns out to live — was withdrawn for the release case: the instruction says
"prepare the 2.4.2 release", `netresearch/github-release-skill` activates on
that word, and neither `nr` nor `nr-full` carries it. The vocabulary was there
and the capability was not.

**Read with that table, the bug-report cases are on offer and not selected.**
Four cases open on a report of wrong behaviour rather than on a named job — the
figure resize, the calendar event, the runtime save failure, the registration
checkbox — and under Haiku 4.5 none of them has loaded a skill in any equipped
trial: 0 of 24, 0 of 12, 0 of 52 and 0 of 6 (`scripts/invocation-census`,
September 2026). The runtime case's zero is a composition result — its README
records that the instance-operation skill sits in `nr-full` and not in the `nr`
arm that ran. The other three are routing results: `nr` carries
`typo3-testing`, whose description opens on a reported defect that has to be
reproduced as a failing test, and on the registration case the `Skill` tool was
in the tool list and all eight skills were listed in every `nr` trial. Set
against the cases that do route — the review and the upgrade, at 53 of 54 and
257 of 263 — the pattern is the one the release case first suggested and then
withdrew for want of a capability: this model reaches for a skill when the
request names a domain or an artefact, and not when it describes something that
is broken. That is a limit of the fleet on this model, not a property of any
one description; `typo3-testing`'s was rewritten to name the situation and read
0 of 3 on the resize case. Whether a model that opens skills more readily
behaves otherwise is the measurement that would separate the model from the
skills, and it has not been run. One further channel was tried and closed on
the resize case: a description that names the directory the right test belongs
in (`Tests/Functional/`), present in every candidate trial, moved no test there
(0 of 6). On a bug-report request the description is neither routed nor acted
on under this model.

## 9. Case admission

A case enters the benchmark only via the lifecycle in
[case-lifecycle.md](case-lifecycle.md): it must originate in observed friction
from real work, survive a retro, be judged system-level rather than
skill-level, and pass human review. An interesting hypothesis is not a case.

## 10. Retro coupling

A failed criterion is an input to `/retro`, never an automatic skill patch. The
loop runs:

```
failed criterion → evidence export → retro → authority → enforceability →
reach → materialization → candidate fleet → same case re-run → compare
```

The generalisation that reaches a skill **MUST** be free of case-specific
detail. "Determine installed versions from the lockfile before reading
constraints" is a learning. "When reviewing t3x-sync, check
DumpFileTrait.php" is contamination wearing a learning's clothes.

## 11. Arms alternate, and three trials are not a measurement

Two rules that come from this repository's own results rather than from theory.

**Randomise the trial, not the batch.** Every comparison recorded before August
2026 ran one arm to completion and the other hours later. A model update, a
caching change or a backend migration in between arrives as a difference
between arms and cannot be told apart from one.

`scripts/run-comparison` schedules a *block* — one trial of every arm, order
shuffled per block — and each trial is its own Harbor call and its own job
directory. Between 19 and 20 August it alternated whole three-trial jobs and
called that interleaving; within a stage one arm still ran back to back, so a
drift inside that stage landed on one side.

**A trial that failed as infrastructure is not a trial that failed.** Every
aggregation reads the gate in `scripts/lib/validity.py` first: a rate-limited
run, a dead agent, an empty trajectory, a provisioned server that never
answered, a collector that never ran and an errored judge each have their own
state, and only `VALID` enters a statistic. RewardKit records a failed judge as
`0.0`, which is a number the system under test never earned; nine such zeros
were once published as findings. Excluded trials are listed with their reason
and are never silently replaced — a re-run chosen because the first attempt
came out wrong is a sample chosen by its outcome.

**An endpoint may be a resource.** `--primary` takes a dimension, the
mechanical outcome, or `cost` / `input_tokens`. The last two were added on 28
August after eleven recorded comparisons, of which three reached complete
separation at the smallest attainable p — and all three were cost, none was a
dimension. Every one of those was exploratory by construction: the runner could
not declare the thing it went on to find, so the benchmark's most separated
result could only ever be reported as a hypothesis. A dimension separating says
the work changed; cost separating says the bill did, and both are results.

**An endpoint may be a spread.** `cost_spread` and `input_tokens_spread`
declare the dispersion of a resource rather than its middle, read as
Brown-Forsythe — each trial's distance from its own arm's median, then the same
rank test as everything else. Added on 18 September after the review case had
shown the same shape three times: bare trials from $0.08 to $1.79 across three
rounds, equipped ones from $0.08 to $0.20 across thirty-five, and the medians
six cents apart. A location endpoint reads that as flat, and a discovery round
of three per arm cannot contain the tail that is the finding, so a spread
endpoint never stops after the discovery round — the schedule runs to the
budget, and the budget is chosen for the tail rather than for the middle. The
first round declared on it, six per arm on that case at the current
environment, found no spread on either arm (p 0.554); the four tail trials
that motivated the endpoint all ran before the case environment moved.

**One endpoint, declared before the run.** `--primary` is required and is
written into `experiments/<case>-<stamp>.json` before the first trial starts.
Everything else `scripts/analyze` reports is labelled exploratory and carries
Holm-adjusted p-values, because a run reads every dimension a case grades and a
threshold meant for one look is a coin flip at eight.

**A quarter of the met/not-met verdicts do not reproduce.** Measured twice, on
identical input: 7 of 32 dimension measurements in the first calibration and 8
in the second flip between met and not met, and the same dimensions flip both
times — the ones scoring near the 0.75 boundary, where one criterion moving one
step crosses it. So a 2/3-against-3/3 row is inside the instrument's own step,
and the argument this section already made now has a number behind it
(`calibration/report.json`, instrument failure 24).

**Three trials answer one question: is anything obviously happening.** They
cannot establish that something is. On the runtime case the spread inside a
single arm covered the whole gap between arms, and a median difference was
published as a 53% saving before anyone looked at the per-trial figures.

So a comparison starts at three per arm and continues only where the **primary
endpoint** separates completely — no overlap between the two samples. That is
the strongest statement three trials can make, and it happens by chance **one
time in ten**: six exchangeable observations admit twenty orderings and two of
them are completely separated, one in each direction. This document, the script
and the published page all said one in twenty until August 2026 — that is the
one-sided figure, and it would apply only to a direction named before the data
were seen, which none of ours was.

Reading it across every dimension is what makes the figure misleading, and the
deepening rule therefore reads only the declared endpoint. `scripts/analyze`
reports the rest with Holm-adjusted p-values so the list cannot be read as
eight independent findings.

The statistics are exact and non-parametric throughout — permutation tests on
ranks, Fisher for pass/fail outcomes, Wilson intervals for rates, bootstrap
intervals for differences (`scripts/lib/stats.py`). With three per arm the
smallest attainable two-sided p is 0.10, so **nothing at this sample size can
clear a conventional threshold**, and a report that appears to is a report to
distrust.

Report counts and per-trial values. A median of three, standing alone, reads
as a measurement and is not one.
