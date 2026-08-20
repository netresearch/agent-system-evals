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
absent from `DIMENSIONS` is listed under `dimensions_unexpected`.

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

    scored: list[float] = []
    covered: list[str] = []

    for dimension in DIMENSIONS:
        values = [t[dimension] for t in trials if dimension in t]
        missing = len(trials) - len(values)

        if values:
            mean = round(sum(values) / len(values), 4)
            result[dimension] = mean
            result[f"{dimension}_met"] = sum(1 for v in values if v >= MET)
            scored.append(mean)
            covered.append(dimension)
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
        result["dimensions_unexpected"] = unexpected

    # Named, because a mean over a different set of dimensions is a different
    # number and nothing else in the output would say so.
    result["mean_over"] = covered
    result["mean"] = round(sum(scored) / len(scored), 4) if scored else None

    output_path.write_text(json.dumps(result, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input-path", type=Path, required=True)
    parser.add_argument("-o", "--output-path", type=Path, required=True)
    args = parser.parse_args()
    main(args.input_path, args.output_path)
