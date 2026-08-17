# Netresearch Agent System Evals

A benchmark that measures whether an agent, equipped with the Netresearch agent
engineering stack, can take a realistic and deliberately underspecified request
and work out for itself what the job actually is.

This repository is **not** an eval framework. Execution, isolation, agent
integration, skill injection, trajectory recording, artifact collection,
grading and regrading are all provided by [Harbor](https://harborframework.com).
What lives here is the part Harbor cannot know: the review methodology, the real
benchmark cases, the system-level rubric, and the conventions that make results
comparable over time.

## Open Forward Reviews

An Open Forward Review gives the agent a prompt a colleague might actually send:

```
Review this TYPO3 extension and tell me what needs attention.
```

It does not say which TYPO3 version to assume, which skill to invoke, which tool
to run, or which file to open. Working that out is the thing under test. A case
that names its own method measures prompt compliance instead, which is a
different and much less interesting question.

Scoring is multi-dimensional. There is no single headline percentage, because a
run that investigates well and reports nothing useful and a run that guesses
correctly are both failures, and one number cannot tell them apart. See
[docs/scoring.md](docs/scoring.md).

## Two kinds of test, kept apart

| | Open Forward Review | Contract eval |
|---|---|---|
| Prompt | realistic, underspecified | names the condition |
| Expected result | not fully known in advance | known failure mode |
| Question | can the agent frame the job? | does the check fire? |
| Lives in | `tasks/open/` | `tasks/contracts/` |

Mixing the two destroys both. A contract eval smuggled into an open case turns
into a hidden findings checklist, and the openness is gone.

## Repository layout

```
docs/            methodology, scoring, lifecycle, ADRs
tasks/open/      Open Forward Review cases
tasks/contracts/ known-failure-mode checks
datasets/        Harbor dataset manifests and aggregation metrics
fleets/          pinned skill fleets (control / nr / candidate)
verifier/        shared mechanical evidence library
scripts/         run, compare, contamination, provenance
```

## Requirements

- Python 3.12+ and [uv](https://docs.astral.sh/uv/)
- Docker (running)
- `harbor` and `harbor-rewardkit`, installed at the versions pinned in
  [`versions.lock`](versions.lock)

```bash
./scripts/bootstrap        # installs the pinned toolchain
./scripts/run-smoke OFR-TYPO3-EXT-001
```

## Status

Phase 1 (Harbor spike). The acceptance criteria and their current state are
tracked in [docs/spike-acceptance.md](docs/spike-acceptance.md). Nothing in this
repository should be read as a settled benchmark result yet.

## Licence

Code is MIT. Methodology documentation under `docs/` is CC-BY-SA-4.0. See
[LICENSE](LICENSE).
