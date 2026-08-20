# /// script
# dependencies = []
# ///
"""Aggregate Open Forward Review trials.

Harbor's default metric averages a single-key reward into one number. Ours are
multi-dimensional on purpose (docs/scoring.md), so this reports each dimension
separately and treats the overall mean as a technical summary rather than the
result.

Three things it deliberately does:

**Counts alongside means.** `verification_met` says how many trials met the
dimension. That is the number a decision gets made on; the mean is for trend
lines. A dimension met in two trials out of three has a reliability problem
that an average of 0.83 makes look like rounding.

**Missing dimensions are omitted, not zeroed.** A dimension absent from a
trial's reward means the verifier did not produce it — an error, a timeout, a
rate-limited judge. Scoring that as zero would silently convert infrastructure
failure into evidence about the system under test, which is the single most
misleading thing this file could do. The previous version said exactly that in
its docstring and then wrote `result[dimension] = 0.0` anyway, and fed the zero
into the mean; `<dimension>_missing` was emitted beside it, so the output looked
careful while being wrong.

**Unknown dimensions are reported, never dropped.** A rubric can introduce one
faster than this file learns about it — `consistency` existed in two cases for a
week before any aggregation knew the name. Anything present in the rewards and
absent from `DIMENSIONS` is counted under `dimensions_unexpected` and named
under `dimensions_unexpected_names`.

**There is no overall mean.** There used to be, computed across dimensions and
described in this file as "a technical summary rather than the result" — a
disclaimer that travels with the docstring and not with the number. It cannot
be defended: `NOT_MET`/`PARTIAL`/`MET` are ordinal, mapping them to 0/0.5/1 and
averaging assumes the steps are equal, and averaging *across* dimensions
assumes they weigh the same. Neither is validated, and the number of criteria
in a dimension silently becomes its weight — so the fixed 0.75 threshold means
something different in each. Anything that needs one number can compute it and
own the assumption; this file will not hand one out.

Harbor formats the *first* key of this output with `:.3f`, so the first key
must be a number. `trials` is. Everything after it is informational and read as
JSON.

`DIMENSIONS` is a literal copy of `dimensions.toml`, which is the definition.
The copy exists because the dataset manifest publishes this file on its own and
it must run detached from the repository; `scripts/validate-rubric` fails when
the two disagree.
"""

import argparse
import json
from pathlib import Path

# BEGIN GENERATED: dimensions.toml
DIMENSIONS = [
    "context_discovery",
    "capability_selection",
    "authority",
    "evidence",
    "verification",
    "prioritization",
    "unsupported_claims",
    "outcome_quality",
    "consistency",
    "release",
    "contract",
]
MET = 0.75
# END GENERATED


def main(input_path: Path, output_path: Path) -> None:
    trials: list[dict] = []
    failed = 0

    for line in input_path.read_text().splitlines():
        if not line.strip():
            continue
        reward = json.loads(line)
        if reward is None:
            # A trial that produced no reward at all. Counted, never averaged
            # in as zero.
            failed += 1
            continue
        trials.append(reward)

    result: dict = {
        "trials": len(trials),
        "trials_without_reward": failed,
    }

    for dimension in DIMENSIONS:
        values = [t[dimension] for t in trials if dimension in t]
        missing = len(trials) - len(values)

        if values:
            # The per-dimension mean stays: within one dimension the criteria
            # are at least comparable, and a trend line over the same rubric is
            # what it is for. `_met` is the number a decision gets made on.
            result[dimension] = round(sum(values) / len(values), 4)
            result[f"{dimension}_met"] = sum(1 for v in values if v >= MET)
            result[f"{dimension}_n"] = len(values)
        elif not trials:
            continue
        else:
            # No trial produced this dimension. That is a statement about the
            # verifier or about which dimensions this case grades — never about
            # the system under test — so it gets a count and no value.
            result[f"{dimension}_missing"] = missing
            continue

        if missing:
            # Surfaced per dimension so a partial verifier failure cannot hide
            # inside an otherwise plausible average.
            result[f"{dimension}_missing"] = missing

    unexpected = sorted({key for trial in trials for key in trial} - set(DIMENSIONS))
    if unexpected:
        result["dimensions_unexpected"] = len(unexpected)
        result["dimensions_unexpected_names"] = ",".join(unexpected)

    output_path.write_text(json.dumps(result, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input-path", type=Path, required=True)
    parser.add_argument("-o", "--output-path", type=Path, required=True)
    args = parser.parse_args()
    main(args.input_path, args.output_path)
