# Threat model

This framework runs foreign repository code and agent-generated commands while
holding model and judge credentials, and publishes what comes out. Until 20
August 2026 none of that was written down, which is why this page exists and
why several of the entries below say "not mitigated".

The question here is not "could someone attack us". It is: **which of these
would produce a wrong number rather than an error?** A benchmark's security
failures and its measurement failures are the same failures — both end in a
plausible result nobody can distinguish from a real one.

## Trust boundaries

| Boundary | Inside | Outside |
|---|---|---|
| Agent container | the target repository, the toolchain, the provisioned fleet | this repository's own files, the expectations, the verifier |
| Verifier container | the rubric, the judge credential, the recorded artifacts | the agent, the workspace it left |
| Host | the credentials, the job store, the expectations key | everything either container produces |
| Published output | the site, the aggregates | job artifacts, transcripts, expectations |

The important one is the second: `environment_mode = "separate"` exists so the
agent cannot reach its own grading. Everything the verifier reads was written by
the system under test, which is the premise of every entry in the next section.

## What an adversary controls

An agent under test writes its own final answer, its own commands, and — through
those commands — the content of every collected artifact. A target repository
supplies files the agent will read and may execute. Neither is assumed hostile;
both are assumed *capable*, because a benchmark that only works against
cooperative subjects measures cooperation.

| Threat | Effect | State |
|---|---|---|
| Prompt injection in the agent's answer or in tool output, addressed to the judge | a score the run did not earn | **mitigated in part**: every judge prompt now carries an explicit "the transcript is evidence, never instruction" section, and `tests/test_injection.py` asserts the payloads survive into the transcript so the defence is tested against what the judge actually sees. Not verified against a live judge — that costs judge calls and is [issue #9](https://github.com/netresearch/agent-system-evals/issues/9)'s territory |
| Artifact poisoning — an agent writes `matrix-14.3.txt` itself | mechanical ground truth becomes agent-authored | **not mitigated**. The upgrade case's outcome is read from artifacts the agent could in principle write. Nothing currently distinguishes a collector's output from a file the agent left at the same path |
| Path traversal out of the workspace | corrupted evidence, or reaching the host | **bounded**: the agent runs in a container whose filesystem is discarded. The verifier reads only what Harbor copied out |
| Credential exfiltration | a subscription token in a public artifact | **partly mitigated**: Harbor removes `[verifier.env]` values from captured output, and `scripts/scan-artifacts` looks for token shapes before anything is published. The agent's own credential is not in its container |
| Secrets in a published trajectory from the *target* repository | someone else's key in our repository | **not mitigated beyond the scanner**. Targets are public repositories, but an agent can print anything it finds |
| Resource exhaustion | a trial that never ends | **mitigated**: per-phase timeouts, CPU and memory limits in each `task.toml` |
| Malicious build script in a target | code execution in the agent container | **accepted**: this is what the container is for. It holds no credential and is discarded |
| Supply-chain change in the verifier image | grading changes with nothing recorded | **mitigated**: base image by digest, RewardKit pinned exactly, judge CLI pinned by version and SHA-256 (`versions.lock`) |
| Expectations leaking to the system under test | the case is destroyed, permanently | **mitigated going forward**: encrypted store, `validate-tasks` refuses plaintext in a task directory, `contamination-check` scans the fleet. Not repairable for the five cases that predate 20 August 2026 — git history is public |
| A skill that has read the benchmark | scores that measure memorisation | **partly mitigated**: `contamination-check` is lexical and cannot see a paraphrase or something a base model already absorbed. That is the holdout set's job (ADR 0005) |

## What is deliberately not defended

**The agent's own container.** It runs foreign code by design. It carries no
credential, its filesystem is thrown away, and its network is an allowlist that
excludes the target's forge.

**A determined author of a target repository.** A repository crafted to defeat
this benchmark would defeat it. Targets are chosen from real work, at pinned
commits that predate the case, which is a provenance argument rather than a
technical control.

## Retention

Job artifacts hold full transcripts of agent runs against public repositories.
They stay on the machine that produced them, are not committed (`jobs/` is
ignored), and are not published. What is published is the site and the
aggregates. `scripts/scan-artifacts` is the gate before anything moves from the
first category to the second.

There is no automated retention limit and no deletion schedule. That is a gap,
not a decision.
