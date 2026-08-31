# AGENTS.md

Benchmark that measures whether an agent with the Netresearch stack can take an
underspecified request and work out what the job is. Execution is
[Harbor](https://harborframework.com); this repository holds the methodology,
the cases and the rubric.

## Layout

| Path | Contents |
|------|----------|
| `VERSION` | The benchmark's version. Every result names it — see docs/governance.md. |
| `dimensions.toml` | The dimension registry. A dimension exists here or nowhere. |
| `expectations/` | Case expectations, encrypted. Never plaintext, never in a task dir. |
| `docs/` | Methodology. `open-forward-review.md` is normative. |
| `docs/adr/` | Decisions, numbered. Read 0003 and 0004 before changing a case. |
| `tasks/open/` | Open Forward Review cases |
| `tasks/contracts/` | Known-failure-mode checks |
| `verifier/common/nreval.py` | Canonical evidence library; copied into each case |
| `verifier/tests/` | Verifier self-test and fixtures |
| `tests/` | Unit tests for the analysis core (metric, comparator) |
| `scripts/lib/` | Shared readers for the scripts |
| `experiments/` | One record per comparison run: seed, arms, jobs, stop reason |
| `fleets/` | Pinned skill fleets. `derives_from` + `without`/`only` declares an ablation without copying one. |
| `datasets/` | Harbor dataset manifests and aggregation metrics |
| `scripts/` | Everything runnable |
| `jobs/`, `reports/` | Generated, gitignored |

## Commands

| Command | Purpose |
|---------|---------|
| `./scripts/validate-tasks` | Harbor task validation, with the reason reported |
| `./scripts/validate-rubric` | Rubric loads; repository rules hold. No judge calls. |
| `./scripts/sync-verifier-lib [--check]` | Copy `nreval.py` into each case |
| `./scripts/verifier-selftest` | Prove the rubric separates a thorough run from a no-op |
| `./scripts/contamination-check --fleet nr` | Fail if the fleet knows a case's answers |
| `./scripts/refresh-target-lock <task-dir>` | Regenerate a target's pinned dependency set |
| `./scripts/run-smoke <CASE-ID> --fleet <name>` | One trial. Pipeline check only, not evidence. |
| `./scripts/run-evaluation <CASE-ID> --fleet <name>` | Three trials. Costs money. |
| `./scripts/compare <job-a> <job-b>` | Per-dimension counts across two jobs |
| `./scripts/analyze experiments/<file>.json` | Effect sizes, intervals and validity for a whole experiment |
| `./scripts/trial-validity --all` | Which trials may enter a statistic, and why not |
| `./scripts/expectations decrypt\|encrypt\|check` | The encrypted case expectations |
| `./scripts/judge-blinding --case <id>` | Can the judge tell which arm it graded? |
| `./scripts/scan-artifacts --all` | Credential shapes in recorded jobs, before anything is published |
| `./scripts/calibrate-judges --dry-run` | What a judge calibration would cost; drop the flag to record one |
| `./scripts/check-calibration` | Is the recorded calibration current and within threshold? |
| `./scripts/build-site` | Render the published page from the jobs it names |
| `./scripts/benchmark-version [--check]` | The benchmark's version; --check refuses a tree that should have bumped it |
| `./scripts/compare --placebo <job-a> <job-b>` | One arm against itself: the instrument's own spread |
| `./scripts/compare --variable model <job-a> <job-b>` | A model comparison, fleet and judge held constant |
| `./scripts/snapshot <job-dir>` | Resolved provenance from Harbor's job lock |
| `./scripts/invocation-census` | How often each case leads an equipped agent to load a skill |
| `./scripts/routing-overlap` | Whether a fleet skill's opening clause shares words with the request |
| `./scripts/mechanical-ledger [--case <id>]` | Every recorded trial against its case's ground-truth check |
| `./scripts/mine-cases` | Candidate cases from real pull requests and commits |
| `uv run --with pytest python -m pytest tests verifier/tests -q` | Unit tests: analysis core and verifier |

`run-smoke` and `run-evaluation` need one credential, used by both the agent
and the verifier's judge:

- `CLAUDE_CODE_OAUTH_TOKEN` — from `claude setup-token`, covered by a Claude
  subscription. LiteLLM sends an `sk-ant-oat` token as a bearer token, so
  RewardKit judges on the subscription too rather than billing separately.
- `ANTHROPIC_API_KEY` — billed per token. Wins if both are set, unless
  `REWARDKIT_FORCE_OAUTH` / `CLAUDE_FORCE_OAUTH` say otherwise.

The agent is installed under the environment baseline (`public`) and only then
restricted to `[agent] allowed_hosts` for the run itself, so the install
reaches npm and the run cannot reach the target's forge.

## Rules that are not obvious from the code

**Never put a case's expected findings anywhere the agent can reach.** Not in
the instruction, the environment, an injected skill, or a reachable URL. A
leaked expectation cannot be un-learned by the skills that saw it, and the case
is finished. Expectations live encrypted in `expectations/<case-id>.md.enc`
and nothing in either container carries them — see `expectations/README.md`
for why they moved and what that does not repair.

**The agent must not be able to reach the target's own forge.** Ground truth
lives in the target's future commits. `[agent] network_mode = "allowlist"` with
the forge excluded is what keeps an open review from being a lookup.

**`[verifier] environment_mode = "separate"` is mandatory.** Not a preference:
Harbor refuses to regrade anything else, so a shared verifier freezes the case
against the rubric it first ran under.

**Do not grade reasoning.** `nreval` never reads `reasoning_content`, on
purpose. Judge prompts say the same. Stated intent is not evidence.

**A criterion a no-op can satisfy is not measuring work.** `verifier-selftest`
enforces this and has already caught one: crediting an unmodified working tree
gave an idle agent a score for discovering nothing.

**Report counts, not means.** `2/3`, never `0.67`. Three trials do not support
two decimal places.

**Only the fleet may differ in an A/B.** `scripts/compare` refuses runs that
differ in case, agent, model, judge or trial count.

## Harbor facts that cost time to find

Measured against Harbor 0.21.0; all four contradict what the surrounding
material suggested.

- Task schema is **1.4**. `artifacts` is a **top-level** key, not part of
  `[environment]`.
- `-p` is a **dataset** path. Point it at the parent directory and select with
  `-i <task-directory-name>` — the directory name, not `[task].name`.
- An invalid `task.toml` is reported as *"0 tasks available in this dataset"*,
  naming neither case nor field. `./scripts/validate-tasks` prints the real
  error. `authors` wants tables (`[{ name = "..." }]`), not strings.
- Skills cannot be pinned to a commit SHA. Harbor resolves refs with
  `git ls-remote`, which returns nothing for a bare SHA. Pin a tag; the
  resolved commit is recorded in the job lock.
- RewardKit is a separate package. The documented invocation
  (`uvx --with harbor-rewardkit@0.1 rewardkit`) fails; use
  `uvx --from 'harbor-rewardkit==0.1.*' rewardkit`.
- `harbor-framework/benchmark-template` is unmaintained. Scaffold with
  `harbor init`.

## Before opening a pull request

```
./scripts/validate-tasks
./scripts/validate-rubric
./scripts/sync-verifier-lib --check
./scripts/verifier-selftest
uv run --with pytest python -m pytest verifier/tests -q
./scripts/contamination-check --fleet nr
```

CI runs exactly these. No agent trial gates a pull request: one trial is not
evidence, and paying for one that cannot decide anything teaches people to
ignore the result.

Sign off every commit (`git commit -s`).
