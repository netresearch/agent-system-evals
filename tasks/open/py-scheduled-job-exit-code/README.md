# OFR-PY-CI-001 — a scheduled job that reports its designed hand-over red

```
The star-notifications job went red again last night. The log says:

    GitHub primary rate limit still in effect after 0 attempt(s) — the next wait
    of 1523s exceeds the 600s left in the budget … The next scheduled run
    retries with a fresh budget.

Every run after it was green. Is red actually the right answer there? Sort it
out.
```

The second case outside TYPO3 and PHP
([issue #16](https://github.com/netresearch/agent-system-evals/issues/16)), in
a domain none of the others touch: a scheduled CI job, and what its exit status
means to the people who read it.

## The target

`netresearch/maint` at `681f2c39`, the commit before the fix. `scripts/
check-stars.py` runs every fifteen minutes under GitHub Actions and notifies a
chat room about new stargazers. It has a per-run sleep budget for rate limits,
and the comment beside that constant says why: a run that cannot get through
hands over to the next scheduled run, because the schedule is the outer retry
loop.

Then it exits 1 for doing exactly that. The log line in the prompt is the
script working as designed and being reported as a failure — which trains
everyone to ignore red runs on that workflow.

## Why this case exists

It is the first case whose defect is not in what the code does but in what it
*says* about what it did. The right change is small and the wrong change is
smaller: catch the exception, exit 0, done. The difference between them is
whether the agent worked out which of the script's several give-ups is a
hand-over with a promised end and which are genuine failures.

There is a second layer, and it is why this target was chosen over a simpler
one. The real fix landed in two commits a week apart. The first made the
hand-over green; the second noticed that a green hand-over is only sound while
some later run can do the work, and that a permanently starved token would
hand over forever, green, processing nothing. A case with a nuanced ground
truth separates better than one with an obvious one.

## What is graded

Mechanically: the script is driven as the workflow drives it — as `__main__`,
against a fake API, with sleeping disabled — and its exit status read for three
answers. The designed hand-over exits 0 with a warning; a secondary limit that
outlasts the budget still exits non-zero; a bad token still exits non-zero.
Deliberately shape-agnostic: it imports no function the fix might have named.
Beside it: the project's own suite passes with whatever the agent added, and
the diff is in the script the log line came from.

By judge, one dimension, `exit_semantics`: whether the agent established that
the exit was designed before changing it, whether the reds that matter stayed
red, whether permanent starvation was considered, and whether the diff is
confined to what was asked.

## What the environment provides

The repository at its pinned commit on the interpreter its CI uses, with the
test dependencies installed from its own hash-pinned list, so the agent's
`pytest` is CI's `pytest`. No GitHub API: the case is about a script that
cannot get through, and a trial that could would be measuring a different day.

## Status

**Never run.** The case validates and its environment builds; no trial has been
recorded against it, so nothing here is a result.

## Reviewed by

Nobody yet. `docs/governance.md` requires a case to be admitted by someone who
did not write it; this repository has been written by one person, so the field
is empty rather than filled in by its author.

## Origin

Run 13078 of `netresearch/maint`'s star-notifications workflow on 13 August
2026, PR #52 the next day, and PR #53 a week later. No learning store exists in
which a retro id could be looked up; `source_learning_id` is coined here the way
the earlier ones were, and this section is where it points.

## What capability this task plausibly needs

Recorded so that a skill-invocation count of zero can be read. A zero means one
of two things — the capability was on offer and was not selected, or it was not
on offer — and those are findings about different things (see issue #24).

Reading Python, reading a GitHub Actions workflow, and reasoning about the
GitHub API's rate-limit semantics. **The organisation publishes no Python
skill.** `netresearch/github-project-skill` covers workflows and is in no fleet.
`fleets/nr-general.yaml` carries the three skills of `nr` that are not TYPO3 or
PHP; none names any of this.

**Absent from every fleet.** A zero here is a composition result, and this case
records it as such rather than as routing.
