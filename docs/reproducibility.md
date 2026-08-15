# Reproducibility and provenance

A result is only interpretable next to the exact system that produced it.
"Skill routing regressed" is not a finding if the agent model also changed.

## What every recorded run pins

| Layer | Pinned as |
|---|---|
| Harbor | version, from `versions.lock` |
| RewardKit | version, from `versions.lock` |
| Agent | agent name and CLI version |
| Model | model id as sent, not a family name |
| Judge | provider, model id, and rubric digest |
| Skills | resolved commit SHA per skill, read from the Harbor job lock |
| Target | repository URL and commit SHA |
| Environment | built image digest |
| Case | task digest |

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
