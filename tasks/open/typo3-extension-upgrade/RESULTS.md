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

| arm | matrix passes |
|---|---|
| `control` — the bare agent | 4/6 |
| **`nr` — the equipped fleet** | **9/9** |
| `nr-full` | 5/7 |
| `companion` | 0/3 |
| `dev-mcp` | 0/2 |

Fisher exact, `nr` against `control`: **p 0.14**. The direction is there and the
sample does not carry it.

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

