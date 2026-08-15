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
6. **Contamination clean.** `scripts/contamination-check` passes.

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
