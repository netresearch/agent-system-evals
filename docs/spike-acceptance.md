# Phase 1 — Harbor spike acceptance

Harbor is adopted only if it carries the whole case. Criteria below are checked
against Harbor 0.21.0 with case `OFR-TYPO3-EXT-001`.

Status values: `verified` (measured here), `pending` (not yet measured).
Nothing is marked from documentation alone.

| # | Criterion | Status | Evidence |
|---|---|---|---|
| 1 | Target reproducible at a pinned SHA | verified | image built; inside it `HEAD` equals the pinned commit, no remotes, clean tree, no `composer.lock`, no `AGENTS.md` |
| 2 | Fresh agent session per trial | verified | one control trial ran end to end in 6 m 28 s on a subscription token |
| 3 | Exact prompt delivered unmodified | verified | the instruction appears once, verbatim, in the recorded trajectory |
| 4 | Netresearch skills injectable | verified | free `nop` run with two pinned skills completed |
| 5 | Resolved skill commits recorded | verified | job lock carries `git_url`, a resolved git object and a content digest per skill; for an annotated tag the recorded id is the tag object, not the commit |
| 6 | Trajectory usable for grading | verified | resolved and staged by the verifier, evidence manifest written from it, and the archived copy parses (17 steps, ATIF-v1.7) once the redaction defect below was fixed |
| 7 | Tool calls observable | verified | 22 `Bash` and 4 `Read` calls recorded in the trajectory |
| 8 | Final answer preserved | verified | the agent's report is present in the trajectory's last agent step |
| 9 | Workspace artifacts preserved | verified | all four collect hooks ran; all three declared artifacts collected with status `ok` |
| 10 | Separate verifier works | verified | verifier image built from `tests/`, container started, `test.sh` executed |
| 11 | RewardKit expresses our rubric | verified | the real criteria scored recorded fixtures into per-dimension rewards |
| 12 | Three trials independently executable | verified | `main` fleet ran `k=3`: three trials, zero errored, three complete reward vectors |
| 13 | Result viewer useful | verified | `harbor view` served the recorded job (HTTP 200) |
| 14 | Regrade works | verified | three regrades of one recorded trial, no agent re-run; this is how the judge configuration was fixed |
| 15 | CI execution feasible | verified | every gate in `.github/workflows/validate.yml` runs locally and is free |

All fifteen are verified. Seven were established with the free `nop` agent,
which proves the plumbing but by construction says nothing about a trajectory;
the real trials and regrades closed the rest.

**Harbor is adopted.** It carried the case, including the parts that were
assumed rather than known. Nothing in the spike required extending it, let
alone replacing any of it.

## Three defects the real trials exposed

None of these were predictable from the documentation, and each was found by
running the thing.

**A short value in `[verifier.env]` corrupts every archived file.** Harbor
treats each value in that table as a secret and removes the literal string from
captured output. A flag passed as `"1"` therefore replaced every digit 1
everywhere: `python3.12` became `python3.[REDACTED]2`, and `"step_id": 1` in
the recorded trajectory became `"step_id": [REDACTED]` — 340 substitutions
across 1.1 MB, leaving a file that no longer parsed.

The redaction lands on the stored files rather than on what the containers
read, so grading inside that trial worked on intact data. What it destroyed was
the archive, and the archive is most of the point: that trial can never be
regraded or audited. `scripts/run-evaluation` now refuses to start when a
declared value is shorter than 12 characters, checked against real values at
run time because they are not knowable earlier.

**A subscription token cannot judge through direct API calls.** Eight
dimensions calling the judge concurrently hit an Anthropic rate limit — and
reducing concurrency to one did not help, because the limit is on the
credential rather than on the parallelism. RewardKit retries only on a schema
mismatch, so a throttled call raises, and one raised reward aborts the run,
discarding every dimension that had already scored.

Judging now runs through the Claude Code CLI (`judge = "claude-code"`), which
is the path a subscription actually grants. The CLI is installed into the
verifier image at build time, because the verifier's run-time allowlist does
not include `claude.ai` and should not.

**A judge that cannot see the evidence returns confident zeros.** The agent
judge inherits the workspace as its working directory, and the Claude Code CLI
confines file access to it. Pointed at `/app`, it could not open
`/logs/verifier/trajectory.json` and scored every criterion not-met, producing
a complete, well-formed, entirely wrong result vector for a review that was
in fact strong.

It reported the cause in its own reasoning — "session path is restricted to
/app" — but nothing in the pipeline treats that as different from a genuine
zero. The fix is `cwd = "/logs"`. The lesson is larger than the fix: this is
the shape a rubric failure takes when it is dangerous. Not a crash, but a
plausible number. It was caught only because the agent's report had been read
first and the score did not match it.

## Rule

If a central criterion fails, extend Harbor before replacing any part of it.
Replacement is the last resort, and the reason for a replacement belongs in an
ADR.

## Known deviations from the original plan

Measured against Harbor 0.21.0 during the spike. Each of these was assumed
otherwise beforehand, and each was found by running the thing rather than by
reading about it.

1. **Task schema is 1.4, not 1.3.**
2. **`artifacts` is a top-level key**, not a member of `[environment]`.
3. **`benchmark-template` is unmaintained** and points to `terminal-bench`.
   Cases are scaffolded with `harbor init` instead; see
   [ADR 0001](adr/0001-use-harbor.md).
4. **RewardKit is a separate package** (`harbor-rewardkit`). The invocation in
   Harbor's documentation, `uvx --with harbor-rewardkit@0.1 rewardkit`, fails —
   uv looks for a distribution named `rewardkit`. Use
   `uvx --from 'harbor-rewardkit==0.1.*' rewardkit`.
5. **Skills cannot be pinned to a commit SHA.** Harbor resolves a `--skill` ref
   with `git ls-remote <url> <ref>`, which returns nothing for a bare SHA and
   fails with "No matching ref". Fleets pin tags; the resolved commit is
   recovered from the job lock, so the record stays exact.
6. **`-p` is a dataset path, not a task path.** Pointed at a task directory it
   resolves zero tasks. Point it at the parent and select with `-i`, using the
   task **directory name** rather than `[task].name`.
7. **An invalid `task.toml` is reported as "0 tasks available in this
   dataset".** `Task.is_valid_dir` swallows the validation error, so the
   message names neither the case nor the field. `scripts/validate-tasks` runs
   the same validation and prints the real error. The fault here was `authors`
   given as strings where Harbor wants tables.
8. **The verifier image is built from `tests/`**, which is its Docker build
   context; the rubric reaches the container only because `tests/Dockerfile`
   copies it to `/tests`. Setting `[verifier.environment] docker_image`
   instead skips the build, and the run fails with
   `bash: /tests/test.sh: No such file or directory` — a message about the
   symptom, not the cause.
