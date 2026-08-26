# Instrument failures

Twenty-one ways this benchmark measured the wrong thing while looking like it was
working. Recorded because they share one shape, and that shape is the thing to
defend against:

> **None of them crashed. Every one produced a plausible number.**

A harness that dies is a nuisance. A harness that returns `0.0` for a criterion
its judge never evaluated is a liar, and nothing downstream can tell the
difference. Two of these reached a published page before they were caught.

Not one was found by a gate. The first thirteen were found by holding a number
against something known independently — a report that had been read, an earlier
measurement, or an implausible spread. The last five were found by an external
review reading the code, which is a different instrument and found a different
class of failure: three of them sat in files whose own comments described the
opposite behaviour, so no amount of holding numbers against reality would have
pointed at them.

Each of the five now has a test that fails against the commit before the fix.
That is the first time anything here has been gated rather than only recorded.

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

## 9. The environment explaining the answer

The runtime case seeded its database from `seed-reported-state.php`, and the
Dockerfile copied that file into the **agent's** container. Its header comment
named the orphaned row, the unresolved foreign keys and the unique-key
collision — the mechanism the case asks the agent to find. Two trials read it
with `cat`, and every trial could have.

`scripts/contamination-check` passed throughout, correctly: it asks whether a
verifier-side file sits in a directory that ships to the agent, and this one
was placed there deliberately, for the seeding step. The check tested intent;
nothing tested the sandbox.

**Fix:** the case's files — seed, target lock, build scripts, the toolchain
installer — are deleted before the readiness marker is written, and the agent
phase does not begin until that marker exists, so the window is closed by the
ordering rather than by a rule. Credentials no longer say "benchmark".
**Guard:** `scripts/agent-surface-audit` builds the case, starts the instance,
and greps everything the agent can read for the measuring apparatus. It found
two more leaks on its first run, one of them a script in the agent's own PATH
describing the benchmark.

## 10. A probe that reported "nothing provisioned" for thirteen skills

The capability probe exists to tell "the tool was not there" from "the tool was
there and unused". On the first clean five-arm run it reported `skills: none`
for every arm, including fleets carrying nine and thirteen. It looked in Claude
Code's default config directory; Harbor sets `CLAUDE_CONFIG_DIR` to
`/logs/agent/sessions`.

Read as a result, that number said the stack was never delivered — the exact
misreading the probe was built to prevent, produced by the probe.

**Fix:** it checks the path Harbor uses, and the MCP config with it.
**Guard:** the ledger counts skills from the collected artifacts as a second,
independent view and prefers it. One source of truth for a number this
load-bearing was one too few.

## 11. The same probe voiding an arm that worked

The mirror image, one day later: the probe marked the companion's server
`unreachable` in an arm whose agent had called it 57 times across all three
trials, and the ledger printed VOID over a valid result. The probe launches a
server itself and asks it to describe itself; that handshake can fail for
reasons the agent never meets.

**Fix:** usage settles it. A capability that was demonstrably called was
provisioned, whatever the probe concluded, and the probe now decides only for
capabilities nobody touched.

## 12. A silent no-op that disarmed every tool arm

The edit that was supposed to declare `PROVISION_PACKAGES` and
`PROVISION_COMPANION_REF` in the cases was a string replacement anchored on a
password that had not been renamed yet. It matched nothing, changed nothing,
and reported success. No case declared the variables, so every companion and
dev-mcp arm ran without its server: the companion arms came back at six tool
calls and twenty-seven cents, because those skills stop when their server does
not answer, and scored as a bad tool.

Diagnosing it needed a second fix. Closing the ground-truth leak had deleted
the install log, and with it every trace of what a provision did.

**Fix:** the insertion refuses to proceed when its anchor is missing.
**Guards:** `validate-tasks` requires a case to declare every `PROVISION_` key
any fleet passes, and a sanitised `provisioning.txt` records what an arm was
given and whether it worked — the file that finally said `companion_ref=<none>`.

## 13. A floor under total failure

The contract eval's negative criteria — "did not report `title` as broken" —
are trivially true of an answer that says nothing. A trial whose agent could
not reach its model endpoint answered `API Error: Unable to connect to API` and
scored 3 of 11 rather than 0.

**Fix:** the negative criteria require an answer to exist first.
**Guard:** the predicate is checked against four answer shapes — an API error,
an empty string, a correct answer, and one that lists every property in the
file.

## 14. A metric that zeroed what it promised not to zero

`datasets/open-forward-reviews/metric.py` opened with a paragraph headed
*"Missing dimensions are reported, not zeroed"*, explaining that scoring an
absent dimension as zero "would silently convert infrastructure failure into
evidence about the system under test, which is the single most misleading thing
this file could do". Forty lines below, the `else` branch wrote `0.0` and the
mean averaged it in.

It also aggregated `skill_routing`, a dimension renamed to
`capability_selection` weeks earlier — so it summed a dimension no case emits
and ignored the one every case does — and CI's smoke test fed it the retired
name, asserted nothing about the output, and passed.

**Fix:** a dimension with no values is omitted and counted under
`<dimension>_missing`; the mean names the dimensions it covers.
**Guard:** `tests/test_metric.py`, nine cases, each one a state the old version
got wrong. Seventeen of the twenty-four new tests fail against the previous
commit.

## 15. A comparator that read "not produced" as "failed"

`scripts/compare` counted a dimension met with `t.get(dimension, 0.0) >= 0.75`.
A dimension the verifier never produced was therefore indistinguishable from
one the run failed, and the metadata cases — which grade a single dimension by
design — would have printed seven confident `0/3` rows for dimensions they do
not grade at all.

**Fix:** met, scored and missing are three numbers. Missing is reported apart
and never counted as failure.

## 16. A variant comparison that could never run

The comparator gained a rule permitting exactly one cross-case comparison: the
prepared and bare variants of one case, where the repository is the variable.
The rule was written after the fingerprint check, which collects every
difference including the task digest — and two variants differ in the task
directory by construction. The feature was refused every time it was used, on
the first line of the check written to allow it. It had never worked, and
nothing said so because a refusal reads as a configuration mistake.

**Fix:** the pair is recognised before the fingerprints are read.
**Guard:** two tests, one for the pair and one for a pair that varies the fleet
as well, which must still be refused.

## 17. Pins that pinned nothing

`versions.lock` said `harbor-rewardkit=0.1`, `scripts/bootstrap` installed
`0.1.*` and every verifier image resolved `harbor-rewardkit==0.1.*` at build
time. Seven patch releases exist. Two jobs recorded weeks apart could have been
scored by different judge harnesses, in a file whose own header states that
changing a version invalidates comparison with earlier runs. The verifier's
base image was pinned by tag rather than digest for the same reason and with
the same effect.

**Fix:** exact version, base image by digest. The Claude Code CLI is still
installed by `curl | bash` with no version and no checksum — written down in
`versions.lock` as `claude_code=unpinned` rather than left to be discovered.

## 18. A regrade that carried the old rubric's identity

`scripts/regrade` copied the source job's snapshot forward and added
`regraded_from`. Everything else was preserved, including the fingerprint that
says which rubric scored it. A job re-scored with today's rubric therefore
claimed to have been graded by the rubric of months ago, and a comparison
between a regraded job and a fresh one read the two as graded alike — which is
the precondition the whole comparison rests on.

The cause is conceptual: what was run and how it was judged were one record.
A regrade changes exactly one of the two.

**Fix:** a separate `grade` block — rubric digest, judge, RewardKit version,
timestamp — replaced on regrade while the trial fingerprint is carried
unchanged. `scripts/compare` refuses two jobs whose grade identities differ.

## 19. An agent failure recorded as a broken harness

The documentation case grades `named_the_extension` by matching a pattern
against `guides.after.xml`, which the collector produces with
`cp /app/Documentation/guides.xml …`. On the case's first trial the agent wrote
ten toctree entries and no `guides.xml`, so `cp` had nothing to copy and left no
target. `nr_artifact_matches` raised on the absent artifact, RewardKit aborted
the entire `documentation` reward, and the validity gate recorded
`INVALID_INFRASTRUCTURE`. The trial was discarded.

The raise was deliberate and its stated reason was this repository's own
principle: a missing artifact means the collector did not run, and scoring that
as the agent's failure would convert a broken harness into evidence about the
system under test. The reason simply did not apply. The collector ran. What was
missing was the agent's work — and the criterion existed precisely to notice
that. `guides.after.xml` was also listed under `required_artifacts`, so the gate
would have voided the trial on its own even with the criterion fixed: the same
mistake, made twice, in two mechanisms.

This is the sharpest instance of the failure mode this document catalogues, and
it runs in the opposite direction from the rest. Every earlier entry describes
an instrument that reported something the system never earned. This one is an
instrument that erased a real result — and erased it *only* when the agent
performed badly, so the discard is correlated with the outcome. A benchmark that
drops its worst trials as infrastructure noise reports a system better than it
is, and reports it with a clean conscience, because the invalid trials are
excluded by a rule everyone agrees with.

**Fix:** the two questions are now asked by the two mechanisms that can answer
them. `nr_artifact_matches` returns False for an absent artifact — absent
behaviour, not absent infrastructure. A case declares in
`metadata.required_artifacts` what must exist regardless of what the agent did,
and the validity gate voids the trial by name when it does not; a `cp` artifact
belongs there only when its source is part of the environment.
`tests/test_nreval_artifacts.py` pins both halves, so the fix cannot be read as
"never raise": an absent trajectory still does.

## 20. A regrade that no comparison would accept

Instrument failure 18 gave a regraded job its own `grade` block so a comparison
could tell which rubric scored it. The repair worked and the result was
unusable: `scripts/compare` reported `has no valid trial to compare` for every
regraded job.

Harbor stamps `agent_execution.finished_at` when the agent phase ends. A regrade
replays a recorded trial through a new rubric and starts no agent, so the field
is absent, and the validity gate read that absence as a killed run —
`INVALID_AGENT: agent phase never finished`. True, and entirely beside the
point. Every trial of every regraded job was discarded.

The consequence is the shape this document keeps recording. The documentation
prescribes a regrade as the cheap repair when two runs carry different rubric
digests — judge calls, no agent time, the whole argument for
`environment_mode = "separate"`. That path produced nothing that could be
compared, and the only symptom was a sentence that reads like a missing
directory. The obvious response to it is to re-run the agent, which is the
expensive thing the regrade exists to avoid.

**Fix:** `classify()` already receives the job snapshot, and a regraded snapshot
carries `regraded_from`. The finish-time check is skipped when it is present,
and nothing else is: the trajectory must still be there and must still record
steps, which is the agent-phase evidence a regrade actually carries forward.
`tests/test_validity.py` pins both directions — the same trial without the
marker is still refused, so the exemption cannot be read as "stop checking".

Found the same day as 19, by trying to run the comparison that the bare case
exists for.

## 21. The answer key was in `.git`

The two cases outside TYPO3 were built with `git clone` followed by `git
checkout <sha>`. That puts the pinned commit in the working tree and every
later commit in `.git`: the fix each case exists to see written, its tests, its
commit messages, and a remote called `origin` pointing at the forge. The Python
image carried 13 commits past its target, the Go image 6.

The first Python trial ran `git log --oneline --all --grep="star-notifications"`
in its third tool call, found both upstream fixes, read them with `git show
<sha>:scripts/check-stars.py`, and reproduced their identifiers and test names
verbatim — `DEFERRED_GIVEUP_STREAK_KEY`,
`test_streak_reaching_the_threshold_turns_the_run_red`. It scored 0.94. The
number is a measurement of whether an agent thinks to look at the log.

Nothing in the run said so. The trajectory is valid, the collectors ran, the
mechanical check passed on a correct tree, the judge saw a competent
investigation. The validity gate cannot see this and should not try to: what
the agent may read is a property of the environment, and the environment is
what was wrong.

The TYPO3 cases never had this defect. `build-instance.sh` does `git init`, a
`--depth 1 --no-tags` fetch of the one commit, and `git remote remove origin`,
with a comment saying why — "the fix for the defect under investigation lives
in this repository's future". The new build scripts were written beside it and
did not copy it.

**Fix:** both scripts now follow the same arrangement and prove it at build
time — `git rev-list --all --count` must be 1 and there must be no remote — so
an image with a future in it does not build. `tests/test_environment.py` asserts
the same of every build script in the repository, against the source, so the
next case written beside these cannot repeat it either. The two recorded trials
are discarded by name in each case's RESULTS.md; they are not evidence about
anything.

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
