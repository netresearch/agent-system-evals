# Phase 1 — Harbor spike acceptance

Harbor is adopted only if it carries the whole case. Criteria below are checked
against Harbor 0.21.0 with case `OFR-TYPO3-EXT-001`.

Status values: `verified` (measured here), `pending` (not yet measured).
Nothing is marked from documentation alone.

| # | Criterion | Status | Evidence |
|---|---|---|---|
| 1 | Target reproducible at a pinned SHA | verified | `environment/target.lock`, SHA verified against the GitHub API |
| 2 | Fresh agent session per trial | pending | requires a recorded run |
| 3 | Exact prompt delivered unmodified | pending | requires a recorded run |
| 4 | Netresearch skills injectable | verified | `harbor run --skill` accepts repeatable git sources |
| 5 | Resolved skill commits recorded | verified | job lock records resolved commit per skill |
| 6 | Trajectory usable for grading | pending | requires a recorded run |
| 7 | Tool calls observable | pending | requires a recorded run |
| 8 | Final answer preserved | pending | requires a recorded run |
| 9 | Workspace artifacts preserved | verified | `artifacts` and `[verifier] collect` in schema 1.4 |
| 10 | Separate verifier works | verified | `[verifier] environment_mode = "separate"` accepted |
| 11 | RewardKit expresses our rubric | verified | one reward per `tests/` subdirectory; judge TOML plus criterion Python |
| 12 | Three trials independently executable | verified | `harbor run -k` |
| 13 | Result viewer useful | pending | requires a recorded run |
| 14 | Regrade works | pending | requires a recorded run to regrade |
| 15 | CI execution feasible | pending | requires a recorded run |

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
