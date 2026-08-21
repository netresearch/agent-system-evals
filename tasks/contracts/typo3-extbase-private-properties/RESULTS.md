# CON-TYPO3-EXTBASE-001 — recorded results (Haiku)

Two fleets, three trials each, six of six valid. Measured 21 August 2026 on
**`claude-haiku-4-5-20251001`**, benchmark version 0.8.0.

## What the run was

`scripts/run-comparison CON-TYPO3-EXTBASE-001 --arms control,nr --primary contract --model claude-haiku-4-5-20251001 --seed 71`

Experiment record: `experiments/CON-TYPO3-EXTBASE-001-20260821-152044.json`.

## Every trial, full marks

| | control | nr |
|---|---|---|
| `contract` met | 3/3 | 3/3 |
| criteria behind it | 33 met / 0 partial / 0 not met | 33 met / 0 partial / 0 not met |
| score, every trial | 1.00 | 1.00 |
| tool calls | 3 / 4 / 4 | 3 / 4 / 7 |
| agent cost | 0.02 / 0.02 / 0.03 | 0.02 / 0.02 / 0.03 |

Thirty-three criteria, six trials, not one miss on either side. Graded in both
directions, so this is not "found four things": the four `private` Extbase
properties had to be named **and** the two `protected` ones beside them had to
be left alone.

## What a ceiling means here, and what it does not

A contract eval is not built to separate fleets. It has a known answer, it runs
in seconds without a judge or an instance, and its job is to fail when a
specific known defect stops being caught — which is what makes it usable as a
merge gate, and an open review not.

So 3/3 against 3/3 is the case working, not the case saying nothing. What it
does say, and it is worth recording plainly: **on this model the unaided agent
already handles this contract perfectly.** A gate that both arms clear at full
marks reports on the model rather than on the stack, and it will go on doing
that until either the model regresses or the contract is tightened.

Against the Opus series of 19 August the control arm there scored 0.97 and the
equipped arm 1.00 — a difference of one criterion, which has now closed. The two
runs are not graded alike and the numbers are quoted as history, not as a
comparison.

## Reproducing

```
scripts/run-comparison CON-TYPO3-EXTBASE-001 --arms control,nr \
    --primary contract --model claude-haiku-4-5-20251001 --seed 71
scripts/analyze experiments/CON-TYPO3-EXTBASE-001-20260821-152044.json
```
