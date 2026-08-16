# ADR 0007 — Writing cases keep an open prompt and gain outcome criteria

- Status: accepted
- Date: 2026-08-16

## Context

The first case asks for a review: the agent reads and reports, and everything
worth grading is in the trajectory and the final answer.

The cases that follow ask for work: move an extension onto the current LTS,
write the documentation, resolve an issue. Two things change.

The result is no longer in the trajectory. It is in the tree the agent left
behind, and the only way to know whether it is any good is to run it.

And the outcome is partly knowable in advance. "Works on the current LTS" has a
right answer in a way that "what needs attention" does not. [ADR
0002](0002-open-vs-contract-evals.md) separates open reviews from contract
evals precisely to stop those from blurring, so a writing case has to say where
it sits.

## Decision

**The prompt stays open.** It names no version, no tool, no file and no
required change. For the upgrade case it does not even say whether the older
line is kept — that is the project's own convention, discoverable from its
history and its documentation, and working it out is part of the task. A prompt
that stated it would be measuring instruction-following again.

**Outcome criteria are mechanical and are added.** Whether the result resolves,
builds and passes its own tests is decided by running it, not by a judge
reading a diff. These criteria are executed by `[[verifier.collect]]` hooks in
the agent's environment after it stops, because a separate verifier receives
artifacts and cannot run the workspace.

**Each leg runs in a scratch copy.** Testing in place would mutate the tree the
rubric inspects, and the diff would then contain the verifier's own installs —
making scope discipline, one of the things most worth measuring in a writing
task, unmeasurable.

**A failing check is a finding, never a lost trial.** Every hook ends in
`|| true` and writes its verdict to a file. A collect hook that fails takes the
evidence down with it, which is the same failure shape as a rate-limited judge:
the system under test looks bad because the instrument broke.

**Cases declare where they sit.** `metadata.writing_task = true` marks a case
whose outcome is partly knowable, and its README says so. They stay under
`tasks/open/` because their prompts are open; they are not contract evals, but
they are not as open as a review.

## Consequences

Writing cases are more expensive to build and to run: two dependency
resolutions and two test runs per trial on top of the agent's own time.

The environment must be able to produce the asked-for result before the agent
arrives. For the upgrade case that means both matrix legs are proved resolvable
at build time and the image fails loudly otherwise — a case that asks for
something its environment cannot support would score every trial as the agent's
failure.

Grading gains a dimension that the review case does not exercise: whether the
change is confined to what was asked. That is measured from the diff, not
judged from the narrative.
