# OFR-TYPO3-EXT-001 — recorded results (Haiku)

Two fleets, three trials each, six of six valid. Measured 22 August 2026 on
**`claude-haiku-4-5-20251001`**, benchmark version 0.8.0.

## What the run was

`scripts/run-comparison OFR-TYPO3-EXT-001 --arms control,nr --primary outcome_quality --model claude-haiku-4-5-20251001 --seed 81`

Experiment record: `experiments/OFR-TYPO3-EXT-001-20260822-092852.json`.

An earlier attempt on 21 August, same seed, stopped in its third block:
`run-comparison` checks how much life the session token has left and refuses to
start a trial that would run past it, because a trial that dies on a 401 is
recorded as an errored trial rather than as a credential problem. Four trials
from that attempt are on disk under experiment
`OFR-TYPO3-EXT-001-20260821-153503` and are **not** pooled into the figures
below — an abandoned experiment's trials are not spare observations for the next
one.

## Both arms do the job

| | control | nr |
|---|---|---|
| `outcome_quality` met | 3/3 | 3/3 |
| criteria behind it | 10 met / 2 partial / 0 not met | 10 met / 2 partial / 0 not met |
| permutation p | — | 1.000 |

The primary endpoint is at the ceiling on both sides, so the runner stopped
after the discovery round. Every secondary dimension is Holm-adjusted to 1.000.

| dimension | control | nr |
|---|---|---|
| `context_discovery` | 3/3 | 3/3 |
| `prioritization` | 2/3 | 2/3 |
| `verification` | 1/3 | 0/3 |
| `authority` | 0/3 | 0/3 |
| `evidence` | 0/3 | 0/3 |
| `unsupported_claims` | 0/3 | 0/3 |

`unsupported_claims` is worth its own line: 0 met and 9 partial in control, 1 met
and 8 partial in the equipped arm, with nothing scored *not met* on either side.
A review that neither overclaims nor grounds its claims is the middle of that
dimension, and both arms sit there.

## The cost separates completely, in the equipped arm's favour

| | control | nr |
|---|---|---|
| agent cost per trial | 0.16 / 0.19 / 0.36 | 0.09 / 0.13 / 0.14 |
| input tokens | 603.6k / 1.04M / 1.64M | 320.9k / 564.3k / 703.5k |
| tool calls | 21 / 58 / 80 | 25 / 32 / 43 |

Every equipped trial costs less than every control trial: Cliff's delta −1.00,
permutation p 0.100 — the smallest p three trials per arm can produce, and the
strongest statement this sample size admits. The median falls by a third.

It is still **exploratory**. `outcome_quality` was the declared endpoint and it
did not move; reading a completely separated secondary line as the finding is
what the declaration exists to prevent. What it does is name the next
experiment: a series with cost declared as the primary endpoint would settle in
six trials what this one can only suggest.

## The skill was invoked

`typo3-conformance`, in three trials of three.

That is the second case in this sweep where routing fires — the other is the
documentation case — and both are cases whose request names a domain a skill
covers. "Review this TYPO3 extension and tell me what needs attention" reaches a
conformance skill; "prepare release 2.4.2" and "check whether these two
declarations agree" reach nothing, in six trials each.

Taken with the cost figures, this is the clearest shape in the sweep: where the
capability is selected, the equipped arm reaches the same result over a
noticeably shorter path.

## Reproducing

```
scripts/run-comparison OFR-TYPO3-EXT-001 --arms control,nr \
    --primary outcome_quality --model claude-haiku-4-5-20251001 --seed 81
scripts/analyze experiments/OFR-TYPO3-EXT-001-20260822-092852.json
```

---

# Ablation: `nr` without the conformance skill

Two arms, three trials each, six of six valid. Measured 22 August 2026 on
**`claude-haiku-4-5-20251001`**, benchmark version 0.8.0.

`scripts/run-comparison OFR-TYPO3-EXT-001 --arms nr,nr-minus-conformance --primary outcome_quality --model claude-haiku-4-5-20251001 --seed 101`

Experiment record: `experiments/OFR-TYPO3-EXT-001-20260822-145242.json`.

## Why this case and not a factorial sweep

A fleet changes several things at once, so an ablation is only worth trials
where a component was demonstrably used. Across the nine-case Haiku sweep this
is the one place that holds: `typo3-conformance` was invoked in three trials of
three here, and the cost separated completely against control. Ablating a
component of a fleet whose effect is not established would measure a difference
of a difference at three trials per arm.

## Removing it moves five of eight dimensions

| dimension | `nr` | minus conformance | delta | p | Holm |
|---|---|---|---|---|---|
| `outcome_quality` (primary) | 3/3 | 2/3 | −0.78 | 0.300 | — |
| `capability_selection` | 0/3 | 0/3 | **−1.00** | 0.100 | 0.700 |
| `verification` | 1/3 | 0/3 | **−1.00** | 0.100 | 0.700 |
| `context_discovery` | 3/3 | 2/3 | −0.44 | 0.500 | 1.000 |
| `prioritization` | 2/3 | 0/3 | −0.56 | 0.400 | 1.000 |
| `authority` | 0/3 | 0/3 | −0.56 | 0.400 | 1.000 |
| `evidence` | 0/3 | 0/3 | −0.44 | 0.500 | 1.000 |
| `unsupported_claims` | 0/3 | 0/3 | −0.44 | 0.700 | 1.000 |

Every delta is negative. The counts hide most of it, and the criteria behind two
dimensions do not:

| | `nr` | minus conformance |
|---|---|---|
| `capability_selection` | **12 met / 0 partial / 0 not met** | 3 met / 7 partial / 2 not met |
| `verification` | 13 met / 4 partial / 7 not met | 3 met / 8 partial / 13 not met |
| `outcome_quality` | 10 met / 2 partial / 0 not met | 5 met / 7 partial / 0 not met |

Both separated dimensions sit at Cliff's delta −1.00 with p 0.100 — the strongest
statement three trials per arm admits. Holm puts them at 0.700 because eight
dimensions were read, and the primary did not move, so this remains
**exploratory**. What it does is name a confirmatory series: `verification` or
`capability_selection` declared as the primary, on this case, against this pair.

## The agent substituted, and the substitutes did worse

| trial | skills invoked |
|---|---|
| `nr` 1, 2, 3 | `typo3-conformance` |
| minus conformance 1 | `automated-assessment`, `typo3-extension-upgrade` |
| minus conformance 2 | `automated-assessment`, `security-audit` |
| minus conformance 3 | none |

This is the part worth keeping. The agent did not simply lose a capability and
carry on unaided: in two of three trials it reached for the routing skill and
then for a *different* domain skill — an upgrade skill on a review task, a
security skill on a review task — and `capability_selection` fell from twelve
criteria met to three. Once it reached for nothing at all.

So the finding is not "conformance helps" but something more specific: **no other
skill in this fleet substitutes for it, and the fleet's own router picks a poor
substitute rather than declining.** That is a lead about `automated-assessment`,
which is the skill whose job is exactly this choice.

## Cost

| | `nr` | minus conformance |
|---|---|---|
| agent cost | 0.11 / 0.14 / 0.15 | 0.08 / 0.10 / 0.16 |
| input tokens | 491.3k / 614.1k / 634.6k | 324.6k / 368.2k / 826.8k |
| tool calls | 19 / 42 / 48 | 22 / 25 / 41 |

Overlapping in both directions, p 0.700. Removing the skill does not
reliably save anything, and the arm that kept it still costs a third less than
the unequipped control measured on this case the same week.

---

# Ablation 2: `nr` without its routing skill

Two arms, three trials each, six of six valid. Measured 26 August 2026 on
**`claude-haiku-4-5-20251001`**, benchmark version 1.0.0.

`scripts/run-comparison OFR-TYPO3-EXT-001 --arms nr,nr-minus-assessment --primary outcome_quality --model claude-haiku-4-5-20251001 --seed 131`

Experiment record: `experiments/OFR-TYPO3-EXT-001-20260826-110325.json`.

## The question, from the first ablation

With `typo3-conformance` removed, the agent reached for `automated-assessment`
and then for a *different* domain skill — an upgrade skill, a security skill —
on a review task, and scored below the arm with nothing. Was the router
causing that substitution, or would it happen without it? Same case,
conformance present, assessment absent.

## Removing the router changes nothing that matters

| | `nr` | minus assessment |
|---|---|---|
| `outcome_quality` (primary) | 3/3 | 3/3 |
| `capability_selection` criteria | 12 met / 0 / 0 | 12 met / 0 / 0 |
| `typo3-conformance` invoked | 3 of 3 | 3 of 3 |
| agent cost | 0.10 / 0.11 / 0.14 | 0.11 / 0.11 / 0.15 |

Six trials of six selected the conformance skill, with or without the router
in the fleet. The primary is at the ceiling on both sides, capability
selection is identical to the criterion, and cost is identical to the cent.
The one line that separates — `unsupported_claims`, 0/8/1 → 3/6/0, delta +1.00,
p 0.100 — is exploratory and Holm-adjusted to 0.700, and it leans *against*
the router.

## What the two ablations say together

- With the matching domain skill present, the router contributes nothing
  measurable: the agent selects the domain skill from the request alone.
- With the matching domain skill absent, the router is what the agent reaches
  for, and what comes back is a poor substitute rather than a decline.

So `automated-assessment` is not what selects the right skill here; it is what
selects a wrong one when the right one is missing. That is a statement about
one case and one model, at three trials per arm, and it is the first component
result this repository can name. Issue #17's third condition — the result names
the component or says it could not be isolated — is met by naming it.

---

# Confirmatory series: cost declared, and it did not confirm

Two arms, six trials each — the full twelve-trial budget — 28 August 2026 on
**`claude-haiku-4-5-20251001`**, benchmark version 2.0.0.

`scripts/run-comparison OFR-TYPO3-EXT-001 --arms control,nr --primary cost --model claude-haiku-4-5-20251001 --seed 181`

Experiment record: `experiments/OFR-TYPO3-EXT-001-20260828-121312.json`.

This is the first run in this repository to declare a resource as its endpoint.
Until 28 August `--primary` took only dimensions and the mechanical outcome, so
the three completely separated cost results on record — including this case's —
were exploratory by construction: the runner could not declare the thing it
went on to find.

## The separation broke

| | three trials per arm (22 August) | six trials per arm (28 August) |
|---|---|---|
| agent cost, control | 0.16 / 0.19 / 0.36 | 0.08 / 0.13 / 0.26 / 0.38 / 0.44 / **1.79** |
| agent cost, nr | 0.09 / 0.13 / 0.14 | 0.09 / 0.12 / 0.13 / 0.13 / 0.14 / 0.15 |
| Cliff's delta | **−1.00** | −0.44 |
| permutation p | **0.100** | 0.240 |

Complete separation did not survive doubling the sample. One control trial came
in at $0.08 — below every equipped trial — and that single observation is
enough: "every trial of one arm below every trial of the other" is a claim one
counter-example ends.

**That is two for two.** The upgrade case's `verification` separated at 3v3 and
failed its confirmation on 22 August; this one separated at 3v3 and failed its
confirmation on the 28th. The one-in-ten figure in
[docs/open-forward-review.md](../../../docs/open-forward-review.md) section 11
is not a caution about a rare event any more — it is the observed behaviour of
this design at this sample size, twice.

## What survived, and what it is

The median difference is large and its interval crosses zero: 0.32 → 0.13, 95%
CI [−0.98, +0.02]. Input tokens the same shape, 1.18M → 484k, p 0.093.

What the doubled sample made visible instead is dispersion, and it is not
subtle:

| | control | nr |
|---|---|---|
| range | $0.08 – $1.79 | $0.09 – $0.15 |
| widest over narrowest | **22×** | **1.7×** |
| six trials, total | $3.08 | $0.76 |

The equipped arm spent between nine and fifteen cents, six times. The unaided
arm spent between eight cents and $1.79 on the same task. Both produced the same
result — `outcome_quality` 3/3 on both arms in the earlier series.

**So the effect here may be on variance rather than on location**: not reliably
cheaper per trial, but reliably *predictable*, which for a task run many times
is the difference between a budget and a lottery. That is a hypothesis this run
generated and did not test — dispersion was not the declared endpoint, and a
median that moves 60% with an interval crossing zero is exactly the shape that
invites reading a spread as a saving. The next run on this case declares
dispersion or it declares nothing.

## What the four-times figure is and is not

Six control trials cost $3.08 against $0.76 — a factor of four on the total.
That number is real and it is not a per-trial claim: it is dominated by one
trial at $1.79, and the median difference is a third of it. Quoting the total
as "the stack is four times cheaper" would be reading one outlier as a rate.

## The grep block is not the saving

`experiments/OFR-TYPO3-EXT-001-20260918-170620.json`, seed 5011, Haiku 4.5,
benchmark 10.2.0. Six trials, six valid, declared on `cost`. `nr` pins
`typo3-conformance` v2.19.4; `candidate` is `nr` with that skill at an
experiment branch cut from v2.19.4 whose one commit deletes the fifteen-line
"Quick Grep Recipes" block from `SKILL.md` and nothing else, resolved `bca2c33`
in every lock.

The hypothesis, from the cost-declared round of 28 August: the block ran in six
of six equipped trials and its equivalent in none of six bare ones, at $0.13
against $0.32 with the same task outcome, so removing the block alone should
send cost back toward the bare arm's.

| arm | `outcome_quality` | agent cost, three trials | input tokens | agent steps |
|---|---|---|---|---|
| `nr` (block) | 3/3 | $0.13, $0.17, $0.11 | 521k, 799k, 565k | 17, 23, 18 |
| `candidate` (no block) | 3/3 | $0.09, $0.10, $0.12 | 368k, 384k, 468k | 13, 13, 15 |

**It did not.** Cost overlapped — median $0.13 → $0.10, Cliff's delta −0.78,
p 0.200, one `nr` trial inside the candidate's range — and the runner stopped
after the discovery round. The declared endpoint says the block is not where
the saving lives. The exploratory lines lean the other way, and are recorded
as that: input tokens separate completely, −1.00 at the smallest attainable p,
and `verification` moved 0/3 → 2/3 at p 0.300, the one judged dimension that
did. Three trials with the declared endpoint flat carry neither.

**What the arm without the block did instead.** It ran equivalent greps by
hand — `grep -r "declare(strict_types" … | wc -l`, `grep -r '\$GLOBALS' …`,
`grep -r "GeneralUtility::makeInstance" …` — two to three per trial, counting
files with a pattern where the block lists files without it. The same targets,
inverted tests, chained with `wc -l` rather than run one per line. The body's
Steps 1–11 name those tokens in prose; the agent greps for what the steps name
whether or not a fenced block spells the command.

**The observation this round adds, cause not established.** The token gap
tracks agent steps — 13/13/15 without the block, 17/23/18 with it — and not
the block's own size: per-step input is 28k against 31k, and 971 characters in
context for seventeen turns is four thousand tokens, not a hundred and fifty
thousand. Single-grep calls do not separate either. Where the extra turns go is
not answered here.

**So the plan this arm was written for is retired.** "More checks as blocks,
chosen by what `nr` still greps by hand" assumed the greps were the saving.
They are not; the equipped arm and the arm without the block both grep, and
both cost a third of bare.

**Where the saving lives, from the counts already on record — the next
hypothesis, not this round's finding.** Over the six bare trials of 28 August
the agent made 248 `Read` calls and 13 `Agent` calls, with `ListAgents` and
`SendMessage` beside them: it read forty-one files a trial and fanned out to
sub-agents in most of them. The six equipped trials read fifty-two files in
total — nine a trial — and delegated in none. This round's two arms, both
equipped, read 37 and 25 and delegated in none. What the conformance body
supplies that the bare model lacks is not a grep; it is a plan — Steps 1–11
say what to check, and the model checks that instead of reading everything and
spawning help. That is testable the same way this round was: `candidate` =
`nr` with the Steps list removed and the block kept. If reads and `Agent` calls
come back, the plan is the mechanism.

## The numbered checks are not the saving either

`experiments/OFR-TYPO3-EXT-001-20260918-200017.json`, seed 5023, Haiku 4.5,
benchmark 10.3.0. Six trials, six valid, declared on `cost`. `nr` pins
`typo3-conformance` v2.19.4; `candidate` is `nr` with that skill at an
experiment branch cut from v2.19.4 whose one commit deletes the "Steps 1-11:
Checks" heading and its eleven lines from `SKILL.md` and nothing else,
resolved `8a87c50` in every lock. Step 0, Step 12, the delegation paragraph,
the grep block and the scoring table stayed; the installed `SKILL.md` in each
trial directory carries the block six times and the heading three, on the
`nr` side only.

The six trial directories of this round are lost — removed with the worktree
the round ran in, after the record was committed (instrument failure 35).
Every number below was read from them while they existed; the record keeps
the job names, the seed and the stop reason, and `scripts/analyze` cannot be
re-run on it.

The hypothesis, from the section above: the body supplies a plan, and the
28 August counts — bare trials at forty-one `Read` calls a trial with
sub-agents in most, equipped at nine with none — are the plan's signature. The
per-trial observables were named before the round ran, in `fleets/candidate.yaml`
and the launch script: `Read` and `Agent` call counts from `steps[]`. If the
plan is the saving, the arm without it drifts toward the bare shape and cost
follows.

| arm | `outcome_quality` | agent cost | input tokens | agent steps | `Read` calls | `Agent` calls |
|---|---|---|---|---|---|---|
| `nr` (list) | 3/3 | $0.12, $0.13, $0.12 | 522k, 544k, 531k | 16, 17, 17 | 11, 10, 8 | 0, 0, 0 |
| `candidate` (no list) | 3/3 | $0.14, $0.11, $0.13 | 506k, 505k, 564k | 16, 17, 18 | 13, 6, 9 | 0, 0, 0 |

**It did not drift.** Cost overlapped — median $0.12 → $0.13, Cliff's delta
+0.33, p 0.700 — and the runner stopped after the discovery round. The
pre-registered observables read the equipped shape on both arms: a mean of
9.7 `Read` calls a trial with the list and 9.3 without, against the bare
forty-one; `Agent` calls zero in all six. Tokens and tool calls overlap too
(p 0.700 and 1.000). No exploratory line points the way the hypothesis needed
either: four judged dimensions moved by one or two trials against the
candidate, each flagged by the analyzer as within one judge step of its
threshold.

**What the arm without the list checked.** Counting the tokens of the eleven
checks in each trial's `Bash`, `Read` and `Grep` arguments: `nr` touched
eleven to fourteen of twenty tracked topics a trial, `candidate` ten to
twelve, and the core set is the same on both sides — `strict_types`,
`$GLOBALS`, `makeInstance`, `ext_tables.php`, `HashService` and the magic
finders, cache `has()`, `composer.json`, `ext_emconf.php`, `Services.yaml`.
Those are the block's own lines and its inline comments. The list names the
topics in prose; the block names the same topics as commands with a comment
each. Either one alone carries the plan.

**So the two ablations answer each other.** Removing the block left the list,
and the agent typed the block's greps from the list's nouns. Removing the list
left the block, and the agent worked the list's topics from the block's
comments and commands. Neither is the saving on its own because each is a
copy of the other, and the single-removal design cannot see a mechanism that
is present twice. The 28 August contrast — nine reads against forty-one, no
delegation against most — was taken here as the signature of *something* in
this body; the section after this one measures it across the other bare
rounds, and it does not hold there.

**The design this suggested, and why it was not run.** Take both out —
`candidate` = `nr` with the body reduced to Step 0, Step 12, delegation,
scoring and the references list — and read the same two counts. Before cutting
that branch the reference those counts would be read against was measured
across every bare round, and the next section is what came back.

## The plan signature was one round's tail

The subtraction chain above — block out, list out, both out next — rests on
one contrast: the 28 August bare arm at forty-one `Read` calls a trial with
sub-agents in most, against the equipped arm at nine with none. Before the
third round ran, that contrast was read off every bare round on this case at
the current cost class, from the same `steps[]` counts (the 19 August rounds
sit on an earlier benchmark version and a different cost class and are left
out):

| bare round | trials | `Read` per trial | `Agent` per trial | cost |
|---|---|---|---|---|
| 21 August | 2 | 14, 18 | 0, 0 | $0.14, $0.17 |
| 22 August | 3 | 13, 39, 17 | 0, 1, 0 | $0.16, $0.36, $0.19 |
| 28 August | 6 | 143, 19, 26, 21, 12, 27 | 7, 1, 4, 0, 0, 1 | $1.79, $0.38, $0.44, $0.13, $0.08, $0.26 |

Against that, every equipped trial recorded on this case since 21 August —
`nr`, both ablation arms, `nr-minus-conformance`, `nr-minus-assessment`,
thirty-five trials — reads between 0 and 14 files, delegates in none, and
costs between $0.08 and $0.20.

**So the stable difference is small, and the large one is a tail.** Read
median 19 bare against about 9 equipped; cost median $0.19 against $0.13. The
forty-one and the thirteen sub-agent calls are one round, and inside it two
trials. Four of eleven bare trials cost more than $0.35; none of thirty-five
equipped ones cost more than $0.20. That is the shape "What
survived, and what it is" already described on 28 August — an effect on
dispersion, not on location — and the sentence there, *the next run on this
case declares dispersion or it declares nothing*, was not followed: rounds
thirteen and fourteen declared cost between two equipped arms, whose costs
never varied to begin with, and came back flat for that reason.

**The both-out design is retired unrun.** Its pre-registered reference was
one round's tail, and a cost-declared discovery round of three per arm cannot
see either the difference at the middle (about $0.06 at the median, inside
the equipped arm's own range) or a tail that shows in four of eleven. It would have stopped after discovery
whatever the body contained, and a third flat round would have been read as a
third fact about the body rather than as the same fact about the design.

**What this case asks for is an endpoint the runner does not have.** Bare
against equipped, declared on the spread of cost rather than its middle, with
a block count fixed in advance because a tail does not show in three. The
runner's endpoints are a dimension, the mechanical outcome, an invocation rate,
and a resource's location; none of them can be declared for the thing this
case's data have shown three times. That is the harness change this section
hands on, and the next round on this case waits for it.

## The spread, declared, is flat

`experiments/OFR-TYPO3-EXT-001-20260918-204559.json`, seed 5031, Haiku 4.5,
benchmark 10.3.0. Twelve trials, twelve valid, six per arm, bare (`control`)
against `nr`, declared on `cost_spread` — the first round on any case to
declare a spread, with the endpoint from the section above. The discovery
round decided nothing by construction and the schedule ran to the budget of
twelve. Pre-registered in the launch script: the endpoint, the block count,
and a tail rule — any trial above $0.35 is an event with its own counts, never
averaged.

| arm | `outcome_quality` | agent cost, six trials | distance from the arm's median | `Read` per trial | `Agent` per trial |
|---|---|---|---|---|---|
| `control` | 6/6 | $0.10, $0.11, $0.18, $0.18, $0.18, $0.20 | 0.00, 0.00, 0.00, 0.02, 0.07, 0.08 | 20, 24, 13, 14, 22, 17 | 1, 0, 0, 0, 0, 0 |
| `nr` | 6/6 | $0.10, $0.10, $0.13, $0.16, $0.17, $0.18 | 0.01, 0.01, 0.03, 0.03, 0.04, 0.04 | 13, 12, 13, 16, 4, 7 | 0, 0, 0, 0, 0, 0 |

**No tail appeared.** Zero events under the tail rule on either arm. The
declared endpoint reads Cliff's delta +0.22 on the deviations, p 0.554 — the
bare arm is, if anything, the tighter one this round. (The table shows costs
and deviations to the cent; the test runs on the full-precision values from
each trial's `result.json`, where no two deviations tie. Recomputed from the
rounded figures it reads 0.565, because rounding creates ties.) Cost location is flat
too (median $0.18 → $0.14, p 0.132), as are input tokens and tool calls.
`outcome_quality` is at the ceiling on both arms, 6/6 each; every judged
dimension is inside its Holm-adjusted 1.000. `skill_invoked` 0/6 against 6/6,
Fisher 0.002: the stack was reached for in every equipped trial and changed
nothing that this case measures. The one stable difference from the sections
above holds — `Read` median 18.5 bare against 12.5 equipped, one sub-agent
call in the bare arm — and is worth about four cents at the median.

**What the tail was, then.** Every bare trial above $0.35 on record — one on
22 August, three on 28 August — ran before the case environment moved to PHP
8.5 on 30 August and before the 1 GB memory limit of 17 September. The $1.79
trial made 215 agent steps with no memory or fatal marker in its transcript;
what it was doing for 215 steps is not read here. Whether the tail belonged
to that environment or to the model is not established; what this round says
is that at the current environment six bare trials produced none, and the
predictability claim "What survived, and what it is" sketched on 28 August
has nothing to stand on today.

**So on this case, at this model and this environment, the stack has no
measurable effect on cost or outcome.** Location flat three times, spread
flat once, outcome at the ceiling on both arms in every round since 22
August. In the governance table this is the cost-with-no-return column with
the cost at zero: reaches what bare reaches, neither cheaper nor dearer. The
seventeen bare trials on record at the
current cost class read $0.08 to $0.20 in thirteen and above $0.35 in four,
all four from before the environment moved; the forty-one equipped ones read
$0.08 to $0.20 without exception. The number that once separated this case —
$0.13 against $0.32 on 28 August — was a median pulled by trials that this
environment does not seem to produce.

**What follows for the loop.** This case has answered its question for the
review skill under Haiku: the skill routes, the body is read, and a task the
bare model already does for twenty cents is not shortened by it. The
mechanism-hunting rounds (thirteen, fourteen, the retired third) were looking
for a saving that the current environment does not show. The next measurement
on the stack's value belongs on a case where bare does not reach the ceiling
or does not stay under a quarter — the upgrade case, where outcome moves, or a
case whose bare cost has a middle worth shortening. This case stays in the
fleet as the routing check it has become: `skill_invoked` 6/6 is what it
measures now.
