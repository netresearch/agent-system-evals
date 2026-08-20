# Governance

Who may change what, and what a change does to results already recorded.

Written on 20 August 2026, after an external review pointed out that nothing
said when a case retires, how a rubric change is versioned against results that
already exist, or who reviews a case other than the person who wrote it. Every
rule below has a mechanism behind it; where it does not, the entry says so
rather than describing an intention.

## The benchmark has a version

`VERSION` at the repository root. A result names it, and two results with
different versions are not comparable without saying what moved between them.

The three parts mean different things:

| Part | Bumped when | Effect on recorded results |
|---|---|---|
| **major** | a case is added, retired or replaced; a dimension is added or removed | earlier results measure a different benchmark and are not comparable |
| **minor** | a rubric changes; the judge, its prompt or its input changes | earlier results are comparable only after a regrade |
| **minor** | a fleet moves to a new skill version | earlier results measured a different arm; no regrade repairs that, only new trials |
| **patch** | tooling, documentation, anything that cannot move a score | comparable |

The middle row is the one that gets skipped. A rubric edit is cheap to make and
changes what every future number means; the regrade that repairs comparability
costs judge calls and no agent time, which is the entire argument for
`environment_mode = "separate"` (ADR 0004).

**While the leading zero stands, the parts shift one place.** At `0.x.y` the
project is not claiming stability, so a case addition moves `0.3.0` to `0.4.0`
rather than to `1.0.0`, a rubric change moves `0.4.0` to `0.4.1`, and a patch
change does not move the version at all — there is nowhere left for it to go.
This is the ordinary `0.x` convention and is written down because the table
above would otherwise read as an instruction to declare 1.0.

`scripts/benchmark-version` prints the version and names the part a change
demands. It does not compute the next number: which digit that lands on depends
on the paragraph above, and a script that guessed would be wrong on the day the
leading zero goes.

## Cases

**Admission** is the lifecycle in [case-lifecycle.md](case-lifecycle.md):
observed friction from real work, a retro, a judgement that the finding is
system-level rather than skill-level, and human review. An interesting
hypothesis is not a case.

**Review by someone else.** A case is admitted by a person who did not write
it, recorded in the case's `README.md` under *Reviewed by*. This repository has
been written by one person, so as of today **no case satisfies this** — the
field exists, and it is empty, which is the honest state rather than a rule
nobody applied.

What such a review is for is not a second opinion on the prose. It is the four
questions in [CONTRIBUTING.md](../CONTRIBUTING.md): can the agent reach the
answers, is the prompt still open, does the rubric grade behaviour rather than
wording, and would a failure here mean anything.

**Retirement.** A case retires when any of these becomes true:

- its expectations have been published, or are demonstrably in a model's
  training data
- its target repository has changed under it in a way the pinned commit no
  longer represents
- every arm has scored the same on it three measurement series running — it no
  longer separates anything and costs the same to run
- the friction it came from has been fixed at the source, so the case measures
  history

A retired case moves to `tasks/retired/`, keeps its results, and stops being
run. It is not deleted: the recorded trials are evidence about the instrument
even when they are no longer evidence about a stack.

**The five public cases that predate 20 August 2026 are on notice.** Their
expectations were committed in plaintext in a public repository from the day
each was written (ADR 0005). They remain useful for development and are not
evidence about any system that could have read them.

## Rubrics

A rubric change is a **minor** bump and invalidates comparison with earlier
results until both sides are regraded. Two mechanisms enforce the parts that
can be enforced:

- the grade snapshot records the rubric digest, and `scripts/compare` refuses
  two jobs whose digests differ
- `scripts/check-calibration` refuses a calibration measured against a rubric
  that has since changed

What is not enforced: nothing stops a rubric edit from landing without a
version bump. `scripts/benchmark-version --check` is the gate, and it is
advisory until someone wires it into a required check.

## Holdout rotation

ADR 0005 keeps a private holdout set so that public-case improvement can be
told apart from memorisation. The rule: **a holdout case is replaced when its
detail is published, and the set is replenished as ordinary work rather than in
response to having burned one.**

No holdout case exists today. The public dataset is the only one, and the
overfit signal ADR 0005 describes — public rising while holdout is flat —
cannot currently be read.

## Who decides

| Decision | Who |
|---|---|
| admit a case | its author, plus one reviewer who did not write it |
| retire a case | anyone, on one of the criteria above, in a pull request |
| change a rubric | its author, with the version bump and a regrade plan |
| publish a result | whoever ran it, after `scripts/build-site` renders it from the artifacts |
| spend judge calls on a calibration | the repository owner |
| cut a release of a fleet skill | that skill's repository, not this one |

## What this document does not do

It does not make the benchmark independent. Cases, rubric, fleets and analysis
are written by the same people whose stack is under test, and the review rule
above is the only structural check on that — currently unfilled. An external
case review is
[issue #16](https://github.com/netresearch/agent-system-evals/issues/16)'s
neighbour and is not scheduled.
