# OFR-TYPO3-UPGRADE-001 — recorded results (Haiku)

Two fleets, three trials each, six of six valid. Measured 22 August 2026 on
**`claude-haiku-4-5-20251001`**, benchmark version 0.8.0.

The last case of the Haiku sweep and the one where the two arms behave least
alike — while the declared endpoint stays flat.

## What the run was

`scripts/run-comparison OFR-TYPO3-UPGRADE-001 --arms control,nr --primary outcome_quality --model claude-haiku-4-5-20251001 --seed 91`

Experiment record: `experiments/OFR-TYPO3-UPGRADE-001-20260822-101714.json`.

## Neither arm completed the upgrade

| | control | nr |
|---|---|---|
| mechanical outcome | 0/3 | 0/3 |
| `outcome_quality` met | 0/3 | 0/3 |
| per-trial score | 0.44 / 0.50 / 0.50 | 0.46 / 0.50 / 0.56 |
| permutation p | — | 0.700 |

The primary is flat and the runner stopped after the discovery round. Everything
below is exploratory.

## Two dimensions separate completely

| dimension | control | nr | delta | p | Holm |
|---|---|---|---|---|---|
| `verification` | 0/3 | 1/3 | +1.00 | 0.100 | 0.600 |
| `prioritization` | 0/3 | 2/3 | +1.00 | 0.100 | 0.600 |
| `context_discovery` | 0/3 | 0/3 | +0.56 | 0.500 | 1.000 |
| `authority` | 0/3 | 0/3 | +0.56 | 0.400 | 1.000 |
| `evidence` | 1/3 | 1/3 | +0.11 | 1.000 | 1.000 |
| `unsupported_claims` | 2/3 | 1/3 | −0.44 | 0.700 | 1.000 |

The counts understate what moved. Behind `verification` the criteria go from
**0 met / 5 partial / 19 not met** to **11 met / 6 partial / 7 not met**; behind
`prioritization`, from 0 met / 8 partial / 1 not met to 5 met / 4 partial / 0 not
met. Those are not one-trial wobbles, and both are completely separated at
delta +1.00 — the strongest statement three trials per arm admit.

They are still exploratory, and Holm puts them at 0.600 precisely because eight
dimensions were read. A confirmatory series with `verification` declared as the
primary is what these lines are for.

## What the two arms actually did

| | control | nr |
|---|---|---|
| tool calls | 4 / 5 / 5 | 27 / 33 / 117 |
| input tokens | 97.7k / 99.1k / 122.4k | 904.2k / 1.37M / 7.75M |
| agent cost | 0.02 / 0.03 / 0.03 | 0.14 / 0.25 / 1.12 |

Read the control column first. **Four to five tool calls on a TYPO3 major-version
upgrade**, around 100k input tokens, two to three cents. The unaided agent barely
engages with the task, and its `outcome_quality` of 0.44 to 0.50 is what an
answer written from general knowledge scores. Its 2/3 on `unsupported_claims` —
the one dimension where it leads — is easier to earn when little is claimed.

The equipped arm spends between ten and seventy times the tokens and separates
completely on cost in the other direction (delta +1.00, p 0.100), with one trial
at 117 tool calls and $1.12. It does not finish either. What it buys, on these
numbers, is verification and prioritisation of an upgrade it did not complete.

Whether that is worth $0.25 instead of $0.03 is a question about the task, not
about the benchmark — and it is the opposite trade from the review case measured
the same week, where the equipped arm reached the same result for a third less.

## The skill was invoked

`typo3-extension-upgrade`, in three trials of three.

Third and last case in the sweep where routing fires, after documentation and
review. All three name a domain a skill covers. The five cases where nothing was
invoked — release preparation, both version-metadata cases, the restraint case
and the runtime bug — name a task instead.

## Reproducing

```
scripts/run-comparison OFR-TYPO3-UPGRADE-001 --arms control,nr \
    --primary outcome_quality --model claude-haiku-4-5-20251001 --seed 91
scripts/analyze experiments/OFR-TYPO3-UPGRADE-001-20260822-101714.json
```

---

# Confirmatory series: `verification` declared in advance

Two arms, three trials each, six of six valid. Measured 28 August 2026 on
**`claude-haiku-4-5-20251001`**, benchmark version 2.0.0.

`scripts/run-comparison OFR-TYPO3-UPGRADE-001 --arms control,nr --primary verification --model claude-haiku-4-5-20251001 --seed 171`

Experiment record: `experiments/OFR-TYPO3-UPGRADE-001-20260828-074950.json`.

## Why this run exists

The exploratory series of 22 August separated completely on `verification` and
`prioritization` — delta +1.00, permutation p 0.100, Holm 0.600 over eight
dimensions read at once. That is what the deepening rule calls a hypothesis:
it names the next experiment rather than settling anything. This is that
experiment, with `verification` declared before the first trial and read as the
only endpoint.

## It did not confirm

| | control | nr |
|---|---|---|
| `verification` met | 0/3 | 0/3 |
| criteria behind it | 0 met / 4 partial / 20 not met | **8 met / 3 partial / 13 not met** |
| Cliff's delta | — | +0.33 |
| permutation p | — | 0.600 |

The count is flat and the criteria are not: eight criteria met against zero is
the largest shift this case has produced on any dimension. But the dimension
crosses its threshold in no trial of either arm, so what moved is the middle of
the distribution and not the outcome — and the earlier +1.00 does not survive
its own confirmation.

Two things follow. The first is about this case: the equipped arm does more
verifying and still never verifies enough to meet the dimension, which is a
statement about how far the fleet gets rather than whether it helps. The second
is about the rule that produced the hypothesis. A completely separated
exploratory line at three trials per arm was, here, noise dressed as a finding
— exactly what the one-in-ten figure in
[docs/open-forward-review.md](../../../docs/open-forward-review.md) section 11
predicts will happen roughly one time in ten.

## The rest of the table

| dimension | control | nr | Holm |
|---|---|---|---|
| `context_discovery` | 3/3 | 0/3 | 0.600 |
| `prioritization` | 0/3 | 1/3 | 1.000 |
| `unsupported_claims` | 2/3 | 0/3 | 1.000 |
| `authority` | 0/3 | 0/3 | 1.000 |
| `evidence` | 1/3 | 1/3 | 1.000 |
| `outcome_quality` | 0/3 | 0/3 | 1.000 |

`context_discovery` separates completely in the *other* direction this time —
3/3 against 0/3, delta −1.00, the same p 0.100 and Holm 0.600 that
`verification` carried in August. It is exploratory, it is one of seven lines
read at once, and it is recorded here without a claim attached for the same
reason the August lines should have been.

**And the calibration since has given it a second reason.** Four of those six
trials score within one judge step of the 0.75 threshold, so their met/not-met
answers are the ones measured to flip on identical input — 7 of 12 such
measurements did, against 1 of 20 further from the line (instrument failure
24). `scripts/analyze` now marks the row, and this one is marked. A 3/3
against 0/3 built from boundary scores is a statement about the instrument.

`typo3-extension-upgrade` was invoked in three trials of three, as before.

## Cost

| | control | nr |
|---|---|---|
| agent cost | 0.05 / 0.06 / 0.11 | 0.07 / 0.09 / **1.23** |

One equipped trial cost $1.23, twenty times the control median and ten times
its own arm's next-highest. The interval spans −0.04 to +1.18 and the median
difference is three cents. A mean over this arm would be a number about one
trial.


---

# The Opus jobs of 20 August, read after the fact

Not a run of this benchmark's comparison machinery: separate jobs from 19 and
20 August, before `scripts/run-comparison` existed, found by asking the
recorded artefacts a question none of those jobs had declared.

## What the artefacts say

Every job on this case collects `matrix-*.txt`, the maintainers' own
resolve-and-test matrix run after the agent stops. The case declares the pass
condition (`resolve: ok` and a passing test leg), so the outcome can be
recomputed for any trial ever recorded — `scripts/mechanical-ledger` does it.
On `claude-opus-5`, 20 August, counting only trials the validity gate admits:

| arm | matrix passes | as first recorded |
|---|---|---|
| `control` — the bare agent | **5/6** | 4/6 |
| **`nr` — the equipped fleet** | **9/9** | 9/9 |
| `nr-full` | 6/7 | 5/7 |
| `companion` | 2/3 | 0/3 |
| `dev-mcp` | 2/2 | 0/2 |

Fisher exact, `nr` against `control`: **p 0.40**. There is a direction and the
sample comes nowhere near carrying it.

**The right-hand column is a correction, not a footnote.** The check read
`\nOK (` out of the matrix files, which PHPUnit prints only when a run is clean
of deprecations — and v14.3 deprecates a method this extension calls, so the
target leg could never print it. Eight trials that had passed were counted as
failures (instrument failure 30). This claim has now been wrong twice, for two
unrelated reasons, and both times in the direction that flattered the equipped
arm: first by counting rate-limited trials as failures, now by counting passes
as failures.

## The number this nearly became

Counting every recorded trial rather than every valid one, the same table reads
`control` 4/10 against `nr` 10/10 — Fisher exact p 0.011, and it was written up
here as the strongest evidence in this repository that the stack changes the
work rather than the routing.

It is not. Six of `control`'s ten "failures" were trials that never ran: jobs
from the night of 19 August whose trials all raised `ApiRateLimitError`, spent
zero input and zero output tokens, and produced no agent transcript at all.
`scripts/trial-validity` has always classified them `INVALID_INFRASTRUCTURE`;
the first version of `mechanical-ledger` did not ask it, and so counted a
rate-limited night as six failures of the bare agent.

The same mistake produced a second wrong explanation on the way. Those jobs'
matrix files end in

```
--- pinning to ^14.3
--- resolve: failed
The temporary constraint "^14.3" for "typo3/cms-backend" must be a subset of
the constraint in your composer.json (^12.4 || ^13.4)
```

which reads like a broken collector, and was written up as one. It is not that
either: the message says the manifest still declares the old range, which is
what an unfinished upgrade looks like, and the identical message appears in
Haiku trials whose other leg resolves and tests cleanly in the same run. The
collector was never broken. Two explanations, both invented rather than
measured, for an artefact of counting dead trials.

## What it is, and what it is not

A direction worth a declared run, at a price:

- **Not a declared endpoint.** The question was asked of the data afterwards.
  With eight dimensions and a mechanical outcome per case, something separates
  somewhere; that is why `--primary` is required before a run starts, and these
  jobs predate that rule.
- **Not reproducible on the small model.** On Haiku the case reads 0/3 and 0/3
  for both arms on two separate days, all six trials valid. Both arms fail, and
  they fail differently — one leaves the requirement at `^12.4 || ^13.4`
  untouched, the other widens it to `^12.4 || ^13.4 || ^14.4`, a constraint for
  a TYPO3 version that does not exist. There is nothing to compare at a floor,
  so confirming this needs Opus 5: roughly $370 for twelve trials at the
  $28–31 per trial these jobs recorded.
- **Not monotone in skills.** `nr-full` carries strictly more skills than `nr`
  and reads 5/7. If the effect were "more skills, better work", that ordering
  would not appear.

---

# Round four: two skills answer to one request, and the opening clause does not settle it

`scripts/run-comparison OFR-TYPO3-UPGRADE-001 --arms nr,candidate --primary mechanical_outcome --model claude-haiku-4-5-20251001 --seed 911`

Experiment record: `experiments/OFR-TYPO3-UPGRADE-001-20260831-083713.json`.
The `candidate` arm carried `typo3-extension-upgrade-skill` at `19192dc`, in
every lock.

## What was fixed, and what it was meant to do

Reading the twelve Haiku trials of the earlier rounds one by one, rather than
as a pooled `0/6 against 0/6`, showed that the arms do not fail alike:

| | resolves v14.3 | passes |
|---|---|---|
| `control`, the bare agent | 0/6 | 0/6 |
| `nr`, equipped | 4/6 | 0/6 |

The bare agent never gets past dependency resolution. The equipped agent
installs v14.3.6 four times out of six and then loses every one of those four
to a single line:

```
Class "TYPO3\CMS\Frontend\Controller\TypoScriptFrontendController" not found
Tests/Unit/Classes/Context/AbstractContextTest.php:38
```

A class removed in v14, named in the skill's own v13→v14 table — with a search
that looks only in `Classes/`. PHPUnit resolves it while *loading* the suite, so
the run dies before a test executes. Two fixes went in
([typo3-extension-upgrade-skill#56](https://github.com/netresearch/typo3-extension-upgrade-skill/pull/56)):
fifty searches widened to `Classes/ Tests/`, and a description opening with the
request maintainers actually make rather than with the word "upgrading".

## It did not move, and the reason is not the fix

| | `nr` | `candidate` |
|---|---|---|
| mechanical outcome | 0/3 | 0/3 |
| `skill_invoked` | 3/3 | 3/3 |

Both arms loaded a skill every time. **Neither loaded the one that was fixed.**

| arm | skill the agent reached for |
|---|---|
| `candidate` | `typo3-conformance` 3 of 3 |
| `nr` | `typo3-conformance` 1, `typo3-extension-upgrade` 1 |

Checked in the container rather than inferred: both `SKILL.md` files were
installed for every trial, `typo3-extension-upgrade` carrying the new opening
clause and `typo3-conformance` the old `v2.19.1` one. The reference fix was
never reached, so this run says nothing about whether it works.

## The rule needs a second half

Rounds one to three established that a skill is loaded when its description's
opening clause names what the request says, and not otherwise. Every one of
those measurements pitted a skill against **silence** — no other skill in the
fleet claimed the request.

Here two do. The request is *"We need this extension to work with the current
TYPO3 LTS"*. `typo3-extension-upgrade` now opens with "an extension has to work
with a newer or the current TYPO3 LTS", which is as close to the request as a
description gets; `typo3-conformance` says "modernization to v12/v13/v14 (v14.3
LTS is the default/gold standard)", which matches the same request through a
different door. The near-verbatim opening lost 3 of 3.

**So naming the request in the opening clause is necessary and not sufficient.
Where two skills both claim a request, something has to say which one owns it,
and that cannot be written in one of them alone.** That is the next thing to
measure.

---

# Rounds five to seven: four skill defects, each named by an artefact

Three comparisons, `nr` against `candidate`, Haiku 4.5, primary
`mechanical_outcome` declared each time. All three read 0/3 against 0/3, and
each one moved the failure to a different cause. The value is in the causes,
not in the endpoint.

| record | seed | what `candidate` carried |
|---|---|---|
| `…-20260831-094704.json` | 1013 | conformance hands the version raise away |
| `…-20260831-110325.json` | 1201 | + one search for every removed class |
| `…-20260831-131421.json` | 1307 | + what to write in a type declaration |

## Round five: the boundary moved the routing

Round four established that two skills claim this request and the one with the
near-verbatim opening clause lost 3 of 3. Round five put the other half of the
boundary into `typo3-conformance` — one sentence handing the version raise to
`typo3-extension-upgrade` by name.

| | loaded the upgrade skill |
|---|---|
| round four, `candidate` | 0/3 |
| round five, `candidate` | 2/3 |
| round six, both arms | 6/6 |

Fisher exact for round four against five is 0.4, so this is a direction on
three observations. And round six's 6/6 includes `nr`, which does not carry the
boundary — at this sample size the effect cannot be attributed to the
treatment. What can be said is that the skill is now reached, which it was not.

## Round six: the search term was lost before the search ran

The trial that resolved had done everything asked. It opened the reference,
and it searched `Classes/` **and** `Tests/` — the widening from
[#56](https://github.com/netresearch/typo3-extension-upgrade-skill/pull/56)
worked. Then it merged seven table rows into one pattern and, in doing so,
turned the row's `"TSFE\|TypoScriptFrontendController\|frontend.controller"`
into `GLOBALS\[.TSFE.\]`: it kept the `$GLOBALS` spelling and dropped the class
name. So it fixed `Classes/Context/AbstractContext.php` in four edits and never
saw the reference in `Tests/` that stopped the suite from loading.

Fixed by putting the removed class names into one copy-and-paste search before
the table ([#57](https://github.com/netresearch/typo3-extension-upgrade-skill/pull/57)).

## Round seven: the replacement was invalid PHP, and the real blocker was elsewhere

One trial did fix the test file. The suite still refused to load:

```
Fatal error: Type FrontendUserAuthentication|object|null contains both object
and a class type, which is redundant
```

PHP refuses a union mixing `object` with a class type — reproduced outside
TYPO3 with `php -r 'class A{} function f(A|object $x){}'`. Documented in
[#58](https://github.com/netresearch/typo3-extension-upgrade-skill/pull/58).

**And reading every trial rather than the endpoint showed the larger blocker
had been missed for three rounds.** Four of six trials never reached the test
suite at all. Their `composer.after.json` says why:

| constraint written | trials | outcome |
|---|---|---|
| `^13.4 \|\| ^14.3` — the documented form | 2 | resolved, installed v14.3.6 |
| `^12.4 \|\| ^13.4 \|\| ^14.4` — guessed | 4 | nothing installed |

`^14.4` matches no release: v14's LTS minor is 3, and `get.typo3.org` reports
14.3.6 as the newest. The reference showed `^14.3` twice in its first section
and never named the wrong value — and v11.5, v12.4, v13.4 make `14.4` the
obvious continuation. Fixed by naming the wrong value before the right one
([#59](https://github.com/netresearch/typo3-extension-upgrade-skill/pull/59)).

## What these three rounds are worth

No arm passed, so the mechanical endpoint has nothing to say yet. What the
rounds produced is four defects in a shipped skill, each one found by reading
a trial's own artefacts rather than by inspection, and each one general beyond
this case:

1. A search scoped to `Classes/` cannot see a removed class in `Tests/`, where
   it is fatal rather than merely failing.
2. A row whose search lists alternatives gets merged with its neighbours, and
   the term that matters is the one that goes.
3. A removed class inside a type declaration cannot be replaced by `object`
   while another class type stays in the union.
4. A reference that states the correct value without naming the attractive
   wrong one loses to the pattern.

## Rounds eight to seventeen, Haiku 4.5

From `scripts/mechanical-ledger`, validity-gated, by day. "How far the rest
got" is the rung the 14.3 leg reached; the ledger's appended 13.4 detail is
folded in here.

| day | `candidate` | how far the rest got | `nr` | how far the rest got |
|---|---|---|---|---|
| 31 Aug | 0/20 | no install 11, suite will not load 9 | 0/20 | no install 9, suite will not load 10, suite runs 1 |
| 2 Sep | 0/3 | suite will not load 3 | 0/3 | suite will not load 2, suite runs 1 |
| 4 Sep | 0/6 | no install 2, suite will not load 3, suite runs 1 | 0/6 | no install 2, suite will not load 4 |
| 5 Sep | 1/9 | no install 2, suite will not load 4, green on 14.3 only 2 | 0/9 | no install 5, suite will not load 4 |
| 9 Sep | 0/5 | suite will not load 5 | 0/5 | no install 2, suite will not load 3 |
| 10 Sep | 0/3 | suite will not load 1, suite runs on both legs 2 | 0/3 | no install 1, suite will not load 2 |

The pass on 5 September is the first trial of this case to pass both legs under
Haiku. Round sixteen (9 September) found agents that loaded only
`typo3-conformance`, audited the extension in 10 to 26 tool calls and changed
nothing; the conformance skill now tells a loaded instance to hand the version
raise over
([typo3-conformance-skill#127](https://github.com/netresearch/typo3-conformance-skill/pull/127)).

## Round seventeen: the routing holds, and the agent could not install v14

`candidate` resolves both skills at `main`. All three trials loaded
`typo3-extension-upgrade`, none loaded conformance alone, and all three wrote
`^12.4 || ^13.4 || ^14.3`. `nr` wrote `^14.3` alone, `^12.4 || ^13.4 || ^14.0`
and `^12.4 || ^13.4 || ^14.4`.

None passed, for three different defects in the code:

| trial | 13.4 | 14.3 | what broke |
|---|---|---|---|
| `JW4NTqy` | passed | will not load | `TypoScriptFrontendController` still referenced in `Tests/Unit/Classes/Context/AbstractContextTest.php` |
| `Ba6Wk49` | 3 errors | 3 errors | a test stub replaced by `stdClass` inside a namespace: `Class "Netresearch\Contexts\Tests\Unit\Service\stdClass" not found` |
| `BqshzhQ` | 20 failures | 20 failures | host resolution in `DomainContext` changed, `DomainContextTest` fails |

Each of those is visible the moment the suite runs on v14, and the skill's
step 10 says to do exactly that before calling the work done. What the agents
did with step 10:

| trial | installed v14 | ran the suite | reported |
|---|---|---|---|
| `JW4NTqy` | no — `composer update` exit 100 | yes, on 13.4 | "All 719 unit tests pass" |
| `Ba6Wk49` | no — exit 100 | no | done |
| `BqshzhQ` | not attempted | yes, 20 failures seen | committed, then stopped |

The exit 100 is not the agent's doing. The environment let the agent reach
Packagist but not the forge the archives come from, and the cache warmed at
build time held none of the versions released since — so installing the target
was impossible, for every arm, and had been since at least 18 August: 51 of the
case's 164 trajectories contain the error. Instrument failure 31 in
[docs/instrument-failures.md](../../../docs/instrument-failures.md); fixed in
[#41](https://github.com/netresearch/agent-system-evals/pull/41).

The skill's command had a second wall behind the first: one `composer update`
from v13 to v14 dies in the `typo3/class-alias-loader` plugin after writing the
lock file. The skill now installs in two passes, and says that an upgrade whose
target will not install is untested and must be reported as such
([typo3-extension-upgrade-skill#76](https://github.com/netresearch/typo3-extension-upgrade-skill/pull/76)).

Every round in this file ran on the broken environment. That does not change a
pass into a failure, but it removed the one step that would have let an agent
see its own mistakes, and the stack's advice to take that step could not show
up in the outcome.

## Round eighteen: the first round an agent could test on v14

`experiments/OFR-TYPO3-UPGRADE-001-20260910-093835.json`, seed 2411, Haiku 4.5,
benchmark 3.0.0 — the environment answers Composer from its cache, and the
upgrade skill installs the target in two passes.

| arm | passed both legs | Fisher exact, two-sided |
|---|---|---|
| `candidate` | 3/6 | 0.545 |
| `nr` | 1/6 | |

The first passes of this case under Haiku since 5 September, and three in one
round. All three `candidate` passes kept `^12.4 || ^13.4 || ^14.3`; the `nr`
pass wrote `^13.4 || ^14.3`, which is what the real migration did.

Every `candidate` trial that passed had installed v14 and run the suite on it
ten or eleven times. The three that failed did not end on a passing run there,
and the reasons are the agent's, no longer the environment's:

| trial | installed v14 | last run on v14 | reported |
|---|---|---|---|
| `wVwp469` | no | none — tested 13.4 only | "All tests pass" |
| `en3Vf8a` | yes | suite did not load, three runs | "Done ✅" |
| `PqPxpAA` | yes | none — reset the branch on counting the removed class's uses | asked whether to proceed |

The next change makes the report carry its proof — the installed version and
PHPUnit's summary line, copied from the last run — and says that replacing what
the new version removed is the upgrade, not a question for the user
([typo3-extension-upgrade-skill#77](https://github.com/netresearch/typo3-extension-upgrade-skill/pull/77)).

Exploratory and not declared: the equipped arm spent more — median $0.76
against $0.35, 4.98M against 2.12M input tokens, 92 against 46 tool calls. The four passing trials took 95 to 108 tool calls;
the four cheapest trials across both arms, at 25 to 36, all failed.

## Round nineteen: 4 of 6 against 0 of 6

`experiments/OFR-TYPO3-UPGRADE-001-20260910-111337.json`, seed 2511, Haiku 4.5,
upgrade skill at [#77](https://github.com/netresearch/typo3-extension-upgrade-skill/pull/77).

| arm | passed both legs | Fisher exact |
|---|---|---|
| `candidate` | 4/6 | 0.061 two-sided, 0.030 one-sided |
| `nr` | 0/6 | |

The widest gap this case has shown, and on the small model. `nr` never reached a
green v14 leg: two wrote `^14.4`, one never widened the constraint, two left a
suite that fails on v14 without ever installing v14 themselves, and one left a
manifest on which neither leg resolves.

The proof paragraph #77 added did not take: none of the six `candidate`
reports carried the `exit=` line; every one summarised instead. The two
`candidate` failures:

| trial | 13.4 | 14.3 | what happened |
|---|---|---|---|
| `H6Bmvfv` | failing | passed | got v14 green, never re-ran v13, reported "v12.4, v13.4, and v14.3 compatible" |
| `5V6h2k6` | passed | 3 errors, 13 failures | saw that result on v14, then committed with `--no-verify` |

The next change runs step 10 for every older line the constraint keeps and makes
the report a numbered step that pastes the last run's output on each line
([typo3-extension-upgrade-skill#79](https://github.com/netresearch/typo3-extension-upgrade-skill/pull/79)).

Exploratory: `candidate` spent a median $1.14 against $0.16 and 7.92M against
0.88M input tokens. Its passing trials ran 109 to 191 tool calls; `nr` stopped
at 15 to 127 without a pass.

## Round twenty: stopped after four trials, and what they show

`experiments/OFR-TYPO3-UPGRADE-001-20260910-131116.json`, seed 2611, upgrade
skill at [#79](https://github.com/netresearch/typo3-extension-upgrade-skill/pull/79),
benchmark 3.0.0 (the first record that names it itself).

`typo3-conformance-skill` `main` moved during the run
([#128](https://github.com/netresearch/typo3-conformance-skill/pull/128), a
Dependabot configuration removal), and `run-comparison` stopped rather than
pool two treatments: 0/2 against 0/2. Not a result — but the two `candidate`
trials show what steps 11 and 12 did not prevent:

| trial | 13.4 | 14.3 | what happened |
|---|---|---|---|
| `…131116` | passed | 16 errors | saw `Errors: 17` on v14, added skip conditions to tests, committed with `--no-verify` |
| `…132843` | failing | passed, 3 skipped | ran step 11 — installed v13, the suite failed to load — went back to v14 and wrote "Everything works" |

Both added `markTestSkipped` calls; neither wrote the step 12 report, each
ending its turn on the commit. The mechanical outcome counts `…132843`'s v14 leg
as passed with three tests skipped, because it reads PHPUnit's exit status.

This section first called that a gap in the endpoint, one that had so far
flattered the comparison arm — round eighteen's single `nr` pass carries three
skips on 14.3, none of `candidate`'s eight passes carries any. Reading the skips
themselves corrects it: every one, in all three trials, is
`if (!class_exists(TypoScriptFrontendController::class)) markTestSkipped(...)`,
next to production code that branches the same way. Where one codebase serves
two lines, a test of the branch that exists only on the older line cannot run
on the newer one, and skipping it there is the correct move. A skip count
cannot tell that apart from hiding a failure, so the endpoint stays as it is;
whether a skipped branch has a counterpart test on the newer line is a question
for the judged dimensions, not for the exit status.

Everything ignored stood at steps 11 and 12 or after them. The next change puts
the definition of done at the front of the skill and rules out skipping or
deleting *failing* tests and `--no-verify` there, naming the version-gated skip
as the legitimate case
([typo3-extension-upgrade-skill#80](https://github.com/netresearch/typo3-extension-upgrade-skill/pull/80)).

## Round twenty-one: 5 of 6 against 0 of 6

`experiments/OFR-TYPO3-UPGRADE-001-20260914-084611.json`, seed 2711, Haiku 4.5,
benchmark 3.0.0, upgrade skill at #80.

| arm | passed both legs | Fisher exact |
|---|---|---|
| `candidate` | 5/6 | 0.015 two-sided, 0.008 one-sided |
| `nr` | 0/6 | |

This is the first difference in this case below the conventional threshold, and
it came on the small model. It is not evidence that #80 itself did it: round nineteen stood at
4/6 against 0/6, one trial away. Across rounds nineteen and twenty-one the arm
passed 9 of 12, `nr` 0 of 12. `nr` again never reached a green v14 leg — three
left the constraint unresolvable (`^14.4` twice, not widened once), three left
a v14 suite that fails.

Two things the skill now states at its front still did not hold:

- **No report pasted the `exit=` line** — none of twelve, in either arm.
- **Four `candidate` trials committed with `--no-verify`.** Three of them
  passed both legs and bypassed the repository's own CaptainHook checks
  (`ci:test:php:cgl` exit 8 in one, `ci:test:php:phpstan` exit 1 in another).
  The mechanical outcome reads only the unit suite, so those passes carry
  style and static-analysis failures it cannot see. The one failure, `ScgzvFf`,
  bypassed a hook whose unit-test step had just failed, and reported "711 out
  of 719 tests passing … ready for review" — eight failures on both legs.

Exploratory: `candidate` spent a median $1.20 against $0.22, 8.59M against
1.10M input tokens and 118.5 against 41.5 tool calls.

## Round twenty-two: 5 of 6 against 0 of 6 again

`experiments/OFR-TYPO3-UPGRADE-001-20260914-102519.json`, seed 2811, Haiku 4.5,
benchmark 3.0.0, upgrade skill at
[#85](https://github.com/netresearch/typo3-extension-upgrade-skill/pull/85) —
a failing commit hook is a check to fix, not to bypass.

| arm | passed both legs | Fisher exact |
|---|---|---|
| `candidate` | 5/6 | 0.015 two-sided |
| `nr` | 0/6 | |

The same result as round twenty-one. Across rounds nineteen, twenty-one and
twenty-two `candidate` passed 14 of 18 and `nr` 0 of 18; `nr` has not reached a
green v14 leg once in those rounds.

`--no-verify` fell from four `candidate` trials to two, and both show the rule
half-followed:

- `uiLaAFZ` (passed) ran `php-cs-fixer fix` without the repository's config,
  saw the style hook fail again, then ran the fixer with the config and
  committed with `--no-verify` in the same command — so it never learned whether
  the hook would now pass — and reported "All code style requirements met".
- `CxCeDbt` (the failure) narrowed the constraint to `^14.3`, dropping both
  lines the extension supported, bypassed three failing hooks (style twice,
  PHPStan once) and reported the extension "ready for deployment". Its 14.3 leg
  is green; the 13.4 leg cannot resolve.

No report, in either arm, pasted the `exit=` line — thirty-six trials across
three rounds. That requirement has not changed behaviour once and is a
candidate for removal rather than rewording.

Exploratory: `candidate` spent a median $1.13 against $0.21, 8.14M against
1.04M input tokens and 116 against 40.5 tool calls.

## Round twenty-three: the released stack, 4 of 6 against 0 of 6

`experiments/OFR-TYPO3-UPGRADE-001-20260914-135117.json`, seed 2911, Haiku 4.5,
benchmark 3.1.0. The arms changed: rounds nineteen to twenty-two compared
`candidate` against a `nr` pinned to upgrade v3.11.1, and every fix measured
there is now released as
[v3.12.5](https://github.com/netresearch/typo3-extension-upgrade-skill/releases/tag/v3.12.5)
and pinned in `nr`. So this round asks the question the fleet is for: the
released stack against no skills at all.

| arm | passed both legs | Fisher exact |
|---|---|---|
| `nr` | 4/6 | 0.061 two-sided, 0.030 one-sided |
| `control` | 0/6 | |

`control` never installed the target once — six of six. The two `nr` failures
both failed on the v13.4 leg, which is the leg the skill added in #79:

- `3U8T7Rc` — 14.3 green (`RESOLVE=ok TESTS=passed`, 90 tests skipped, every
  skip `class_exists`-gated and therefore within the rule), 13.4 red with five
  errors.
- `7DXQ3oP` — both legs red: 13.4 with one error and fourteen failures, 14.3
  with a fatal that ends PHPUnit at exit 255. It committed with `--no-verify`
  and its own message says "Test files require refactoring to support v14".

`--no-verify` was executed in two `nr` trials and one `control` trial. One of
the two, `wdjy7jm`, passed both legs and bypassed the hooks anyway; the other
is the failure above. The rule from #85 is followed by four of six.

The `exit=` paste requirement was removed in
[#87](https://github.com/netresearch/typo3-extension-upgrade-skill/pull/87)
before this round, on the measurement recorded under round twenty-two.

Exploratory: `skill_invoked` 6/6 against 0/6 (p 0.002), and `nr` spent a median
$1.16 against $0.07, 8.42M against 239.6k input tokens and 118 against 10.5
tool calls — the cost of the difference, on this case, is roughly sixteen times
the unaided run.

A note on reading `scripts/mechanical-ledger` for this day: it groups by fleet,
model and **day**, so the `nr` row for 2026-09-14 reads 4/18 — rounds
twenty-one, twenty-two and twenty-three together, six trials each. The per-round
numbers are the ones above. The pooling also crosses a fleet change that the row
cannot show: `nr-snapshot.json` records upgrade skill v3.11.1 for the first two
rounds and v3.12.5 for this one, so those eighteen trials are two different arms
under one name.

## Round twenty-four: the sentence was in context, and nobody made the edit

`experiments/OFR-TYPO3-UPGRADE-001-20260918-073044.json`, seed 3011, Haiku 4.5,
benchmark 10.1.0. Twelve trials, twelve valid, the schedule run to its budget.

`nr` pins upgrade v3.12.5, which carries the rule against deleting a `use` line
and leaving `Foo::class` behind in `references/upgrade-v13-to-v14.md`.
`candidate` points at the skill's `main` — v3.12.6 plus
[#94](https://github.com/netresearch/typo3-extension-upgrade-skill/pull/94),
which moves that rule's load-bearing sentence into step 9 of `SKILL.md`. That is
two differences, not one: v3.12.6 also added 59 lines to two references, and it
is named here because it matters for the cost reading below.

| arm | passed both legs | Fisher exact |
|---|---|---|
| `nr` | 6/6 | 0.182 two-sided, 0.091 one-sided |
| `candidate` | 3/6 | |

`skill_invoked` 6/6 on both. `nr` reading 6/6 against round twenty-three's 4/6
on the same fleet and version is the round-to-round swing RESIZE documented, not
`nr` improving.

**The direct test, corrected.** This section first said one trial in twelve made
the edit the moved sentence names — `candidate` `084245`, with the sentence in
its context. It did not. Its v13.4 leg died on a PHP fatal in a compatibility
stub the agent wrote — `Type of …TypoScriptFrontendControllerCompatStub::$rootLine
must be array` — and the count that flagged it matched the stub's class name,
`Tests\Unit\Context\TypoScriptFrontendController…`, not the
`Class or interface … does not exist` line the deleted-import edit produces.
Read with the exact line, the edit occurs in none of the twelve trials of this
round, in either arm. Zero attempts is not a result for or against the sentence:
the question the round was for went unmeasured here, and the one trial that has
made the edit on this case remains round twenty-three's `3U8T7Rc`, with the rule
in a reference it never opened. What the twelve trials do carry — the cost
confound below, and `nr`'s swing — stands.

**The cost reading, with its confound.** Median $0.84 → $1.18, Cliff's delta
+0.78, p 0.026; tokens +42%; tool calls +31%. But the separation tracks
reference-reading, not the four body lines. `candidate` opened references in 3
of 6 trials against `nr`'s 1 of 6, and those three are the three expensive ones
— $1.56, $1.60, $1.31 — while the three that opened none sit inside `nr`'s
range. Two of the three readers failed. Whether the longer body prompts more
reading, or the longer references (v3.12.6) cost more once read, this round
cannot separate, and 3 of 6 against 1 of 6 is not itself significant.

**What this says for the case.** The explanatory fix was placed at the surface
it was moved to, and the edit it describes did not occur in any of the twelve
trials — so whether the sentence prevents it went unmeasured here. The failure it
targets is a mechanical one — an unqualified `::class` to a type that no longer
exists, findable by a grep before any test runs — and none of the skill's 45
mechanical checkpoints looks for it. A sentence did not do it; a check has not
been tried.

## Round twenty-five: the trigger was in context, and nobody pulled it

`experiments/OFR-TYPO3-UPGRADE-001-20260918-092803.json`, seed 3111, Haiku 4.5,
benchmark 10.1.0. Six trials, six valid. The first round on this case declared
on `cost` — the endpoint the benchmark now says is the point — and the runner
stopped after the discovery round: the arms overlapped, p 0.400.

`nr` pins upgrade v3.12.5. `candidate` points at the skill's `main`, which
after
[#95](https://github.com/netresearch/typo3-extension-upgrade-skill/pull/95)
carries `TU-58` — a mechanical check for the deleted-import edit of round
twenty-four — and a step-9 line saying to run the skill's own checks through
the sibling runner. Each candidate job's installed `SKILL.md` has that line and
its `checkpoints.yaml` has `TU-58`.

| arm | passed both legs | agent cost, three trials | tool calls |
|---|---|---|---|
| `nr` | 2/3 | $1.22 median | 122 median |
| `candidate` | 2/3 | $0.94 median | 99 median |

Cliff's delta −0.56 on cost, −0.78 on tool calls, p 0.400 and 0.200 — the
same size of gap round twenty-four read in the other direction, and no claim
either way.

**The direct test.** The trigger was in every candidate trial's context — the
`Skill` observation in `trajectory.json` carries it, three of three — and not
one trial attempted the runner: zero Bash calls mentioning `run-checkpoints` or
`checkpoints.yaml`, across these three and the six candidate trials of round
twenty-four with the same runner installed. `TU-58` would have had nothing to
catch this round — zero namespace-import errors in six trials — which is
unrelated: the check was not run, so it could not have.

**Why it was not pulled, from the twelve trials of both rounds.** No trial in
either round binds a variable of any kind. The agents use the absolute skill
path the loader prints — five Bash calls, all `ls`, `grep` or `find` against
`references/` — verbatim, never as `$SKILL_DIR`. The trigger asked for three
hops: notice the printed path, bind it, run. Per-step counts across the six
trials of this round say which steps get followed:

| step | what it asks | trials that ran it |
|---|---|---|
| 1 | read `references/pre-upgrade.md` | 1/6 |
| 5 | `rector process --dry-run` | 5/6 |
| 6 | `fractor process --dry-run` | 4/6 |
| 8 | `phpstan analyse` | 6/6 |
| 9 | the removed-types `grep` | 2/6 |
| 9 | the checkpoint runner | 0/6 |
| 10 | `composer update … --with typo3/cms-core:^14.3` (fenced block) | 5/6 |

Not position — step 10 sits below step 9 and gets 5/6. What is followed is a
command the agent already knows or a fenced block that runs as pasted. What is
not is a file to open or a path to construct. Step 10 is a literal block with
one hop and gets 5/6; the trigger was a block with an unresolved variable and
got 0/6.

**So the check is now the block.** The `TU-58` loop sits inlined at step 9 —
run from the extension root, no path to find, no variable to bind — extracted
from the `SKILL.md` as written and run against the pinned upstream test file:
silent as committed, one line naming the file and the type with the import
deleted. Whether a block that runs as pasted is run at step 10's rate is the
next round's question, and it is the one the restated purpose asks: a check
that runs replaces the tool calls that find the same thing by hand.

**The arm present in every round.** `nr` alone, same fleet, same version:
4/6 in round twenty-three, 6/6 in round twenty-four, 2/3 here. That range is
wider than any arm difference this case has recorded, and until it is
understood or a schedule runs to twenty-four, six per arm cannot separate the
arms on the outcome. The cost axis shows the same swing: the arm that was
dearer in round twenty-four is cheaper here.

**One correction to how this was read, recorded as instrument failure 34.**
`transcript.txt` cuts each message at 4000 characters, and the trigger sat past
that in a 13,000-character skill body; a grep over transcripts returned zero
for all three trials and was read for half an hour as "the body was not
loaded". The trajectory is the artefact; the transcript now prints where it
cuts.

## Round twenty-six: a block that runs as pasted was run, three of three

`experiments/OFR-TYPO3-UPGRADE-001-20260918-121328.json`, seed 3211, Haiku 4.5,
benchmark 10.1.0. Six trials, six valid, declared on `cost`; the arms overlapped
at the discovery round, p 1.000, and the runner stopped.

`nr` pins upgrade v3.12.5. `candidate` points at the skill's `main`, which
after
[#96](https://github.com/netresearch/typo3-extension-upgrade-skill/pull/96)
carries the `TU-58` loop inlined at step 9 — no path to find, no variable to
bind, exit 1 on a finding — in place of the instruction to run the checkpoint
runner. Each candidate job's lock resolved `dcaa62c2` and each installed
`SKILL.md` carries the block.

| arm | passed both legs | block ran | agent cost, three trials |
|---|---|---|---|
| `nr` | 2/3 | 0/3 (not installed) | $1.47, $1.15, $1.02 |
| `candidate` | 3/3 | **3/3** | $1.30, $1.33, $0.91 |

**The direct test, and the first one in this series to come back positive.**
The block ran in every candidate trial — once, once, and twice in the third,
which is what step 9 asks: before the suite and again after the edits. The
signature is `types='TypoScriptFrontendController|…'` in the Bash arguments,
so it was pasted whole rather than rebuilt. Against the three shapes step 9 has
now carried at the same position, on the same case and model:

| step 9 asked for | ran it |
|---|---|
| a rule, in the body (round twenty-four) | in context 3/3; the edit it names occurred 0/12, so untested |
| an instruction to run a script via `$SKILL_DIR` (round twenty-five) | 0/3 |
| the removed-types `grep`, beside either (rounds twenty-five) | 2/6 |
| the check itself as a fenced block (this round) | **3/3** |

Step 10's fenced block, the best-followed step in the body, is 16/18 across
rounds twenty-four and twenty-five. Three of three clears that bar at three
trials and does not establish it; the next round on this arm is a replication,
not a new question.

**What the block did not do this round is catch anything.** Neither arm made
the deleted-import edit — zero namespace-resolution errors in six trials — so
the block printed no findings and every run of it exited 0. Its value here is
that it ran; whether it saves the v13.4 leg is measured on the round where the
edit recurs, and rounds twenty-three to twenty-six put that at one trial in
thirty-six.

**Cost, declared and overlapping.** Median $1.15 → $1.30, Cliff's delta −0.11,
p 1.000; tokens and tool calls overlap the same way. A block that runs adds its
own tool call and removes none by itself, which is what the numbers show. The
saving the restated purpose asks for comes when a finding replaces the test
run that would have found it — and this round had no finding to replace.

**`nr` again.** 2/3 here after 2/3, 6/6, 4/6: the arm's own swing on this
case now spans five rounds, and every arm comparison at three or six per arm
sits inside it. `candidate` 3/3 against `nr` 2/3 is not a claim.
