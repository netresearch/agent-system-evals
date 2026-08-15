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
| 6 | Trajectory usable for grading | verified in the trial, damaged in the archive | the verifier resolved and staged it (`/logs/agent/trajectory.json`) and wrote the evidence manifest from it; the archived copy was then corrupted by the redaction described below |
| 7 | Tool calls observable | verified | 22 `Bash` and 4 `Read` calls recorded in the trajectory |
| 8 | Final answer preserved | verified | the agent's report is present in the trajectory's last agent step |
| 9 | Workspace artifacts preserved | verified | all four collect hooks ran; all three declared artifacts collected with status `ok` |
| 10 | Separate verifier works | verified | verifier image built from `tests/`, container started, `test.sh` executed |
| 11 | RewardKit expresses our rubric | verified | the real criteria scored recorded fixtures into per-dimension rewards |
| 12 | Three trials independently executable | pending | `-k` accepted; only `k=1` has been run |
| 13 | Result viewer useful | pending | needs a recorded run worth viewing |
| 14 | Regrade works | pending | needs a recorded run to regrade |
| 15 | CI execution feasible | verified | every gate in `.github/workflows/validate.yml` runs locally and is free |

Eleven of fifteen are verified. Seven were established with the free `nop`
agent, which proves the plumbing but by construction says nothing about a
trajectory; the first real trial closed four more.

The remaining four all depend on one usable recorded trial, and the first one
did not produce one. Two defects, both now fixed, and both worth stating
because neither was predictable from the documentation.

## Two defects the first real trial exposed

**A short value in `[verifier.env]` corrupts every archived file.** Harbor
treats each value in that table as a secret and removes the literal string from
captured output. A flag passed as `"1"` therefore replaced every digit 1
everywhere: `python3.12` became `python3.[REDACTED]2`, and `"step_id": 1` in
the recorded trajectory became `"step_id": [REDACTED]` — 340 substitutions
across 1.1 MB, leaving a file that no longer parses.

The redaction is applied to the stored files after the fact, not to what the
containers read, so grading inside the trial worked on intact data. What was
destroyed is the archive: the trial can never be regraded or audited, which is
most of why the artifacts are kept at all. `scripts/run-evaluation` now refuses
to start when a declared value is shorter than 12 characters.

**One rate-limited judge discards the whole verifier run.** Eight dimensions
called the judge concurrently and one hit an Anthropic rate limit. RewardKit
retries only on a schema mismatch, so the call raised, and a raised reward
aborts the run — seven dimensions had already scored and went with it, leaving
no `reward.json`. Judge concurrency is now capped at 2 in `tests/test.sh`.

This is the failure mode where a benchmark quietly lies: a rate-limited
verifier looks exactly like a system that failed to produce evidence.

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
