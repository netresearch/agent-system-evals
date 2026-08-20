# Contributing

## Adding a case

A case is not admitted because it is interesting. It is admitted because real
work went wrong in a way that no single skill owns. The full lifecycle is in
[docs/case-lifecycle.md](docs/case-lifecycle.md); the short version:

1. Friction observed in real work, carried through a retro, with a Learning-Id.
2. Judged system-level rather than skill-level. If one skill owns it end to
   end, it belongs in that skill's eval.
3. A real target at a pinned commit, with no defects introduced for the
   benchmark.
4. A prompt that names no method, tool, skill, file or expected finding.
5. A human baseline recorded in `expectations/<case-id>.md`, encrypted with
   `scripts/expectations encrypt` and never committed in plaintext.
6. `./scripts/contamination-check` clean.

Scaffold with `harbor init --task --no-solution`, then copy the structure of
`tasks/open/typo3-extension-review`.

## Reviewing a case

The questions that matter, in order:

**Can the agent reach the answers?** Check the network allowlist excludes the
target's forge. Check the expectations are encrypted and that no plaintext
copy is staged. Check the
environment image does not carry the target's remote or lock file. This is the
one mistake that cannot be repaired later.

**Is the prompt still open?** Read it as a colleague would. If it hints at a
method, the case measures instruction-following instead.

**Can each criterion fail?** A criterion nothing could miss measures nothing.
Ask specifically what a no-op run would score — `verifier-selftest` answers it
for the mechanical ones.

**Can a no-op satisfy anything?** If yes, that criterion rewards inaction. This
has happened once already; see the comment in
`tasks/open/typo3-extension-review/tests/context_discovery/criteria.py`.

**Is the environment ready?** The commands a competent reviewer would reach for
must work in the image before the agent arrives. A failure there is a broken
case reported as an agent failure.

**Is the artifact set enough for a regrade?** A future rubric sees only what
was collected. Adding a collection hook later does not help the runs already
recorded.

## Changing the rubric

A rubric change alters what every recorded result means. Prefer regrading
history (`harbor job regrade`) over re-running agents, and say in the pull
request which recorded results the change invalidates.

Do not add a criterion that names a specific finding. That is an expected-
findings list arriving one criterion at a time, and it ends the openness of
every case that shares the rubric.

## Before opening a pull request

```
./scripts/validate-tasks
./scripts/validate-rubric
./scripts/sync-verifier-lib --check
./scripts/verifier-selftest
uv run --with pytest python -m pytest verifier/tests -q
./scripts/contamination-check --fleet nr
```

Sign off every commit (`git commit -s`). Do not squash-merge; the commit
history is the record of why the methodology looks like this.
