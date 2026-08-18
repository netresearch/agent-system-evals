# Instrument failures

Eight ways this benchmark measured the wrong thing while looking like it was
working. Recorded because they share one shape, and that shape is the thing to
defend against:

> **None of them crashed. Every one produced a plausible number.**

A harness that dies is a nuisance. A harness that returns `0.0` for a criterion
its judge never evaluated is a liar, and nothing downstream can tell the
difference. Two of these reached a published page before they were caught.

Not one was found by a gate. Every one was found by holding a number against
something known independently — a report that had been read, an earlier
measurement, or an implausible spread.

## 1. A judge that could not see the evidence

The agent judge inherits the workspace as its working directory and the Claude
Code CLI confines file access to it. Pointed at `/app`, it could not open
`/logs/verifier/trajectory.json` — and scored every criterion not-met,
producing a complete, well-formed, entirely wrong vector for a review that was
strong.

It said so in its own reasoning: *"session path is restricted to /app"*.
Nothing in the pipeline treated that differently from a genuine zero.

**Fix:** `cwd = "/logs"`. **Guard:** `tests/test.sh` scans judge reasoning for
admissions of blindness and fails the verifier when it finds them. A verifier
that cannot see must fail loudly, never score low.

## 2. A one-character secret that corrupted every archived file

Harbor treats every value in `[verifier.env]` as a secret and removes that
literal string from all captured output. A flag passed as `"1"` therefore
replaced every digit 1 everywhere: `python3.12` became `python3.[REDACTED]2`,
and `"step_id": 1` in the recorded trajectory became `"step_id": [REDACTED]` —
340 substitutions across 1.1 MB, leaving a file that no longer parsed.

The redaction lands on the stored files, not on what the containers read, so
grading inside that trial worked. What it destroyed was the archive, which is
most of the point: the trial can never be regraded or audited.

**Fix:** the flag was unnecessary and was removed. **Guard:**
`scripts/run-evaluation` refuses to start when a declared `[verifier.env]`
value is shorter than 12 characters, checked against real values at run time
because they are not knowable earlier.

## 3. A rate-limited judge that took the whole run with it

Eight dimensions calling the judge concurrently hit an Anthropic rate limit,
and reducing concurrency to one did not help — the limit is on the credential,
not the parallelism. RewardKit retries only on a schema mismatch, so a
throttled call raises, and one raised reward aborts the run, discarding every
dimension that had already scored.

**Fix:** judging moved to the Claude Code CLI, the path a subscription actually
grants, installed into the verifier image at build time.

## 4. Timeouts scored as zeros, and published

Nine criteria across three recorded jobs hit the 300-second judge timeout. An
agent judge opens the trajectory from disk itself, which an LLM judge never has
to do, and 300 seconds did not cover it.

This one reached the public page. Control's prioritization was reported as 0.61
against 0.94 and called a real improvement attributable to the Netresearch
stack. Regraded without the timeout, control scores 0.94 as well: the
improvement did not exist.

**Fix:** 900 s per judge, 5400 s per verifier. **Guard:** `scripts/compare`
refuses two jobs when either contains a criterion whose judge errored, and says
to regrade rather than averaging over it.

## 5. A transcript that cut the final answer in half

Handing the judge the raw trajectory cost it 40 turns and then a CLI exit, so
it was given a bounded transcript instead — with individual messages capped at
4000 characters. The agent's final report is 8000 characters on a review and
24,818 on the richest run, so the judge saw a fraction of the one artefact most
dimensions grade.

Every report-shaped dimension collapsed across every fleet. The scores moved so
far that they were obviously about the instrument.

**Fix:** the final answer is reserved and rendered whole under a marked
heading, whatever the budget. **Guard:** a test asserts it survives at three
different budgets.

## 6. Evidence placed in a channel the judge does not read

RewardKit's agent path builds its prompt, appends the `atif-trajectory` path,
and **ignores `files` entirely**. Moving the evidence into `files` left the
judges with no pointer to anything; they explored blindly and every dimension
collapsed again.

**Fix:** `atif-trajectory` points at the bounded transcript — the one channel
that reaches an agent judge. **Guard:** `scripts/validate-rubric` rejects an
agent judge that has no pointer.

## 7. A revoked credential, reported as three bad trials

The runtime case's `companion` and `nr-companion` fleets came back as three
graded trials beside three errored ones. Read as a result, that is a fleet
performing worse. It was not: the trials that died carry
`401 OAuth access token has been revoked`.

A subscription token lives about two hours and is revoked the moment Claude
Code refreshes it. A fleet of three runtime trials takes longer than that, and
the token was read once at launch — so the run outlived its own credential.
Because Harbor reports per trial, the job did not fail; it reported a mixture,
and a mixture looks like data.

**Fix:** `scripts/run-evaluation` refuses to start when the session token
expires sooner than the run is expected to take, and says so instead of
producing half a fleet. **Guard:** the check is exercised in three directions —
it fires on a short-lived token, stays silent on a healthy one, and stays
silent on a token the credentials file does not describe.

## 8. A session limit, arriving as a zero

The re-run then produced `ApiRateLimitError` on all six trials and a mean of
`0.0000`. The number is well-formed and entirely meaningless: `You've hit your
session limit · resets 2:50am (UTC)`.

No fix belongs in the code for this one — it is a quota, not a defect. It
belongs here because of its shape. Both this and the failure above arrive as
plausible numbers rather than as errors, and both would have been published as
fleet differences by anyone reading only the metrics block. **The habit that
catches them is the same one at the end of this file: a dimension that moves
when nothing about the agent changed is a question about the instrument.**

## What this cost, and what it teaches

Four regrade rounds. The recorded agent trials survived all of it, which is the
entire argument for `environment_mode = "separate"`: the expensive half was
never at risk, and a rubric fix cost judge calls rather than agent time.

Round four changed two things at once — the pointer and the prompt — and when
it failed, neither could be blamed. Isolating one variable answered it in one
run. That rule is written into this repository's own A/B discipline
([docs/open-forward-review.md](open-forward-review.md) section 8) and was
ignored while debugging the instrument that enforces it.

The standing lesson is a habit rather than a check: **before a number becomes a
finding, hold it against something known independently.** A score that
contradicts a report you have read, a dimension that moves when nothing about
the agent changed, a spread that is implausibly wide — each is a question about
the instrument first and about the system under test second.
