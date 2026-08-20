# Open Forward Review — normative specification

This document defines what an Open Forward Review (OFR) is and what a case must
satisfy to enter the benchmark. It is normative: a case that violates a MUST is
not an Open Forward Review, whatever else it may be worth.

## 1. The question

An Open Forward Review answers one question:

> Can an agent equipped with the Netresearch agent engineering stack take a
> realistic, deliberately underspecified request and work out for itself what
> the job is — and then do it defensibly?

Everything below follows from that sentence. In particular, the review measures
the behaviour of the *whole system* — agent, model, skills, harness, canonical
sources — not the correctness of any one skill. Single-skill correctness belongs
in that skill's own eval; a specific known failure mode belongs in a contract
eval under `tasks/contracts/`.

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
about the target. That record is **verifier-side only**. It **MUST NOT** be
present in:

- the agent's workspace or environment image
- the instruction
- any injected skill
- any file the agent can reach over the network

Violating this does not merely inflate a score, it destroys the case
permanently, because the leaked expectation cannot be un-learned by the skills
that were exposed to it.

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

The judge **MUST NOT** be told which variant it is grading. Telling it that one
side is "the improved skill set" is a request for the answer, not a measurement.

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

## 9. Trials are interleaved, and three of them are not a measurement

Two rules that come from this repository's own results rather than from theory.

**Alternate the arms.** Every comparison recorded before August 2026 ran one
arm to completion and the other hours later. A model update, a caching change
or a backend migration in between arrives as a difference between arms and
cannot be told apart from one. `scripts/run-comparison` runs them in stages with
the order shuffled, so a drift across the session spreads over both arms.

That is block randomisation and not trial-level interleaving: within a stage,
one arm's trials still run back to back, because a Harbor job is the unit the
comparator reads. A drift inside a single stage still lands on one side. Tracked
in [issue #2](https://github.com/netresearch/agent-system-evals/issues/2).

**Three trials answer one question: is anything obviously happening.** They
cannot establish that something is. On the runtime case the spread inside a
single arm covered the whole gap between arms, and a median difference was
published as a 53% saving before anyone looked at the per-trial figures.

So a comparison starts at three per arm and continues only where a dimension
*separates completely* — no overlap between the two samples. That is the
strongest statement three trials can make, and it happens by chance **one time
in ten**: six exchangeable observations admit twenty orderings and two of them
are completely separated, one in each direction. This document, the script and
the published page all said one in twenty until August 2026 — that is the
one-sided figure, and it would apply only to a direction named before the data
were seen, which none of ours was.

It is also read across every dimension a case grades, with no correction for
looking eight times. Separation is a reason to spend more trials and is never a
result on its own. Deliberately not reported as a p-value, because with three
per side the only distinguishable outcomes are "separated" and "not", and a
p-value would dress that up as more.

Report counts and per-trial values. A median of three, standing alone, reads
as a measurement and is not one.
