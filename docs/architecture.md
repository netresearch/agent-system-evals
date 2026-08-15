# Architecture

## Boundary

```
                    REAL USER WORK
                          │
                          ▼
                        RETRO
                          │
                 observed system failure
                          │
                          ▼
                Open Forward Review case
                          │
                          ▼
   ┌──────────────────────────────────────────────┐
   │                   HARBOR                     │   not ours
   │                                              │
   │   pinned environment                         │
   │   + pinned agent and model                   │
   │   + pinned Netresearch skill fleet           │
   │   + natural-language instruction             │
   │        ↓                                     │
   │   observable trajectory + artifacts          │
   └───────────────────┬──────────────────────────┘
                       │
                       ▼
              separate verifier                      ADR 0004
                       │
             ┌─────────┴──────────┐
             ▼                    ▼
      mechanical evidence     RewardKit judges
        (verifier/common)     (tests/<dimension>)
             │                    │
             └─────────┬──────────┘
                       ▼
          multi-dimensional verdict
                       │
             ┌─────────┴─────────┐
             ▼                   ▼
       Harbor viewer         dashboard
       (debugging)           (history)
             │
             ▼
          failure?
             │
             ▼
           RETRO ──► skill / checkpoint / harness / canonical source
             │
             ▼
       candidate fleet ──► same case re-run ──► compare
```

## What this repository owns

The methodology and the parts of it that are executable:

- the Open Forward Review specification and its admission rules
- real cases with pinned targets and human baselines
- the eight-dimension system rubric and its calibration fixtures
- the mechanical evidence library that reads Harbor trajectories
- fleet manifests and A/B conventions
- contamination guard and holdout strategy
- the retro evidence bridge and Learning-Id linkage
- historical reporting

## What it deliberately does not own

Agent runners, agent adapters, container orchestration, trajectory formats,
trial viewers, judge frameworks, artifact collectors, job persistence. Harbor
provides all of these; re-implementing any of them is a defect, not a feature.

## Level separation

```
┌──────────────────────────────────────────────────────────┐
│              OPEN FORWARD REVIEWS                        │
│   Does the whole system frame the job correctly?         │
│              (this repository)                           │
└───────────────────────┬──────────────────────────────────┘
                        │
       ┌────────────────┼────────────────┐
       ▼                ▼                ▼
   harness         automated-         per-skill
   integration     assessment         evals
   (agent-harness) (checkpoints)      (skill repos)
       │                │                │
       └────────────────┼────────────────┘
                        ▼
                      retro
```

There is no second assessment implementation here. `automated-assessment` keeps
owning project and skill checkpoints; this repository asks whether the agent
reaches it at all.

## Data flow into retro

A failed criterion is exported as structured evidence — case, trial, fleet,
criterion, observation, trajectory step references — and handed to `/retro`.
Retro decides authority, enforceability and reach. Nothing in this repository
patches a skill automatically; an eval that edits the system it measures is not
a measurement.
