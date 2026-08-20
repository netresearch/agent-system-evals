# Reproducibility and provenance

A result is only interpretable next to the exact system that produced it.
"Skill routing regressed" is not a finding if the agent model also changed.

## What every recorded run pins

| Layer | Pinned as |
|---|---|
| Harbor | version, from `versions.lock` |
| RewardKit | exact patch version, from `versions.lock` |
| Agent | agent name and CLI version |
| Model | model id as sent, not a family name |
| Judge | provider, model id, and rubric digest |
| Judge binary | Claude Code version and SHA-256, from `versions.lock` |
| Verifier base image | digest, from `versions.lock` |
| Skills | resolved commit SHA per skill, read from the Harbor job lock |
| Target | repository URL and commit SHA |
| Environment | built image digest |
| Case | task digest |
| Grade | rubric digest and grading timestamp, separate from the trial |

Three of those rows were added on 20 August 2026 and two of them were repairs
rather than additions. `harbor-rewardkit=0.1` installed as `0.1.*` across seven
patch releases, the verifier's base image was pinned by a tag that moves, and
the judge's own binary came from `curl … install.sh | bash`, which always
fetches the newest release. This page listed reproducibility as a property of
the project while three of its layers floated.

Every artefact this repository writes now carries a `schema_version` as its
first key — the job snapshot, the experiment record, the calibration report and
the evidence manifest — and `scripts/lib/schemas.py` is where a record is read
rather than each consumer picking fields out of a dictionary. A version from a
future writer raises; a record from before 20 August 2026 migrates. All 86
recorded snapshots on the machine that produced them still load, and a test
asserts it.

The last row is a different repair: what was run and how it was judged used to
be one record, so a regrade carried the original rubric's identity forward and
a comparison could not tell that one side had been re-scored.

Harbor's job lock already records resolved skill commits, task digests and the
verifier environment mode. `scripts/snapshot` reads that lock rather than the
fleet manifest, because the manifest states intent and the lock states fact.

That distinction is not a nicety here. A skill **cannot** be requested by
commit SHA: Harbor resolves a `--skill` ref with `git ls-remote <url> <ref>`,
and ls-remote does not answer for a bare commit, so the run fails with "No
matching ref". Fleets therefore pin tags. A tag can be moved, and a branch in a
candidate fleet certainly will be, so the only trustworthy statement about
which code ran is what the lock resolved. `scripts/run-evaluation` rejects a
SHA-pinned fleet with this explanation rather than letting the run fail
obscurely.

One detail to quote correctly. For an **annotated** tag, the lock's
`git_commit_id` is the *tag object* SHA, not the commit SHA. Measured:
`automated-assessment-skill@v2.14.0` recorded `294f3aa5…`, which is the tag
object; the commit it points at is `2cda8f46…`. Provenance is unharmed —
a tag object is content-addressed, so moving the tag produces a different SHA
and the lock still shows it — but the value must be reported as a resolved
git object, not as a commit, and dereferenced before it is compared with a
commit from anywhere else. The lock also records a content digest per skill,
which is the stronger identity for "was this the same code".

## Snapshot identifier

Each recorded evaluation gets an identifier of the form

```
nr-eval-20260815-4f2a9c
```

and a `snapshot.json` carrying the table above. Results are quoted with the
snapshot, never on their own.

## Model drift

A model id is not a constant. Behaviour can move under an unchanged name, so a
comparison across time is a comparison of two system snapshots, not of two skill
fleets — unless the agent, model and judge are identical in both, which is the
only condition under which a difference may be attributed to the skills.

Where that condition does not hold, the report says so instead of naming a
cause.

## Regrade

Rubrics improve. Re-running agents to apply an improved rubric is expensive and
usually unnecessary: Harbor can re-verify recorded trials, so a rubric change
can be applied to history.

This is only possible for single-step tasks whose verifier resolved to
`environment_mode = "separate"`, which is why that setting is a MUST in the
specification rather than a preference. It also constrains the artifact
strategy: whatever the future rubric might need must be collected now, because a
regrade sees only what was kept.

Collected per trial: trajectory, final response, git status and diff, command
log, test and analyser output, environment metadata, and the normalised evidence
manifest.

## Two things a single harness cannot tell you

**Whether the result is about the stack or about Claude Code.** Every published
figure here comes from one agent. `scripts/sentinel` runs a case on a second
one with everything else held constant. If the fleet effect reproduces, the
finding is about the stack; if it does not *and the capability probe shows the
skills were delivered*, the finding is about the stack inside one harness —
a materially different claim from the one the results currently make. The probe
matters: skills land in a different directory per agent, so a harness that
never received them would otherwise look like one the stack failed to help.

**Whether an upgrade moved the numbers.** Harbor is pinned, and a pin only
protects until it moves. `scripts/harbor-canary` regrades a recorded job under
a candidate version and compares dimension means against what the old one
produced: same trials, same rubric, same trajectories, so any difference is the
harness. It answers identical, drifted, or cannot reproduce — and refuses to
run without a credential, because a regrade calls the judge and a failed one
would otherwise be read as harness drift.
