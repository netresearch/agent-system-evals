# Case lifecycle

A benchmark whose cases come from imagination measures imagination. Cases here
are retro-born: each one traces to friction observed in real work.

```
real task or session
        │
        ▼
observed system-level friction
        │
        ▼
retro
        │
        ▼
is the behaviour relevant beyond a single skill?
        │
        ├── no ──► skill eval or checkpoint (not this repository)
        │
        └── yes
             │
             ▼
        OFR candidate
             │
             ▼
        human review
             │
             ▼
        benchmark case
```

## Admission criteria

A candidate becomes a case only when all of these hold:

1. **Real origin.** It traces to a Learning-Id from an actual retro, recorded in
   `task.toml` as `metadata.source_learning_id`.
2. **System-level.** The behaviour spans skills, routing, authority or
   verification. If a single skill owns it end to end, it is that skill's eval.
3. **Real target.** A public repository at a pinned SHA, with no defects
   introduced for the benchmark.
4. **Open prompt.** Satisfies section 2 of
   [open-forward-review.md](open-forward-review.md).
5. **Human baseline.** An experienced reviewer has worked the case once and
   recorded relevant areas, reasonable investigation paths, and known blind
   spots — verifier-side only.
6. **Contamination clean.** `scripts/contamination-check` passes — for every
   fleet, not one. A decision is pinned to a skill *and* a ref, so each fleet
   and each version needs its own; CI iterates all of them and a check run
   against a single fleet proves nothing about the rest.
7. **The ground truth fails before it passes.** Where a case is mined from a
   reported defect and graded by the fix's own test, that test must be run
   twice — at the pinned commit and at the fix — and must **fail at the pinned
   commit**. Same file, same command, same environment; record both numbers in
   `target.lock`.

   This is the criterion that rejects most candidates, and it cannot be read
   off the diff. Of eight mined in August 2026, two survived it:

   | why a candidate failed | example |
   |---|---|
   | the test reflects into a method the fix introduces | `rte_ckeditor_image#846` |
   | the test exercises a different method than the fix changes, and passes before it | `sf_event_mgt#1361` |
   | the test grew from 4 cases to 20 and all 20 pass before the fix | `sf_event_mgt#1364` |

   That last one is worth dwelling on, because everything readable from the
   diff said yes: an externally visible defect, a fix of eighteen lines, a test
   class that already existed, a data provider quadrupled, assertions on a
   public method with no reflection anywhere. It still does not discriminate.
   A test that ships with a fix is evidence that the author cared, not that the
   test would have caught the defect.

   **A candidate rejected here can often be recovered, and `#1364` was.** Read
   the fix for the *behaviour* it changed rather than the test it shipped, find
   an input the two versions disagree on, and write that one assertion against
   the same public surface. In that case the fix widened "an array counts as
   empty" from exactly `['']` to any array of empty strings, so the
   disagreement is a checkbox group with several options and none ticked —
   which the maintainer's provider cannot construct at all, because it passes a
   plain string for every row and `getValue()` wraps that as `['']`, the one
   shape both versions already agreed on. One added test method fails at the
   pinned commit and passes at the fix.

   The cost is that part of the ground truth becomes ours again, which is what
   mining was meant to avoid. Keep the boundary explicit: the expected
   behaviour comes from the maintainer's fix, the input comes from the
   disagreement between the two versions, and only the assertion is written
   here. Record which is which in the case's `README.md`, and never write an
   assertion the fix's behaviour does not already imply.

8. **The check could have failed for the right reason.** A ground truth that
   passes at the pinned commit is not always a bad candidate — it can be an
   environment that cannot produce the defect. `sf_event_mgt#1219` reports a
   calendar event lost on a daylight-saving day; its test passed at the pinned
   commit under `TZ=UTC`, where there is no such day, and failed under
   `TZ=Europe/Berlin` as reported. Had that case shipped without the timezone
   pinned, its check would have passed in every trial, including for an agent
   that changed nothing, and the case could never have failed anyone.

   So pin whatever the defect depends on — timezone, locale, PHP version — in
   the case environment, and satisfy criterion 7 *under those pinned settings*.

9. **The dependency tree still resolves.** Composer refuses versions with
   published advisories, and every `typo3/cms-core ^12.4` is now blocked. A
   commit from an older LTS needs `--no-security-blocking` in the case's build,
   which puts known-vulnerable dependencies in the image — acceptable in a
   sandboxed, network-restricted container, and to be stated in the case rather
   than left in a build script. This window keeps closing: a case that builds
   today may not build next year, for reasons that have nothing to do with it.

## Retirement

A case is retired when it stops discriminating: when every variant, including
`control`, passes it three times out of three over several runs. It has either
been solved or leaked. Retired cases stay in the repository, marked, because
their history is the evidence that the behaviour was once absent.

A case is **not** retired for being uncomfortable. A case the current stack
fails repeatedly is the most valuable object in the repository.

## Provenance loop

```
real incident
     │
     ▼  Learning-Id
   retro
     │
     ▼
skill / checkpoint / harness / canonical source
     │
     ▼
Open Forward Review case
     │
     ▼
future regression evidence
```

The Learning-Id appears on both ends: in the retro that produced the change, and
in `metadata.source_learning_id` of the case that will notice if it regresses.
