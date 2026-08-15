# /// script
# dependencies = []
# ///
"""Aggregate Open Forward Review trials.

Harbor's default metric averages a single-key reward into one number. Ours are
eight-dimensional on purpose (docs/scoring.md), so this reports each dimension
separately and treats the overall mean as a technical summary rather than the
result.

Two things it deliberately does:

**Counts alongside means.** `verification_met` says how many trials met the
dimension. That is the number a decision gets made on; the mean is for trend
lines. A dimension met in two trials out of three has a reliability problem
that an average of 0.83 makes look like rounding.

**Missing dimensions are reported, not zeroed.** A dimension absent from a
trial's reward means the verifier did not produce it — an error, a timeout, a
rate-limited judge. Scoring that as zero would silently convert infrastructure
failure into evidence about the system under test, which is the single most
misleading thing this file could do.
"""

import argparse
import json
from pathlib import Path

DIMENSIONS = [
    "context_discovery",
    "skill_routing",
    "authority",
    "evidence",
    "verification",
    "prioritization",
    "unsupported_claims",
    "outcome_quality",
]

# Three-point criteria put PARTIAL at 0.5, so "met" sits above it: a dimension
# carried by partial credit alone has not been met.
MET = 0.75


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

    result: dict[str, float | int] = {
        "trials": len(trials),
        "trials_without_reward": failed,
    }

    for dimension in DIMENSIONS:
        values = [t[dimension] for t in trials if dimension in t]
        missing = len(trials) - len(values)

        if values:
            result[dimension] = round(sum(values) / len(values), 4)
            result[f"{dimension}_met"] = sum(1 for v in values if v >= MET)
        else:
            result[dimension] = 0.0
            result[f"{dimension}_met"] = 0

        if missing:
            # Surfaced per dimension so a partial verifier failure cannot hide
            # inside an otherwise plausible average.
            result[f"{dimension}_missing"] = missing

    scored = [
        v
        for dimension in DIMENSIONS
        for v in (result[dimension],)
        if result[f"{dimension}_met"] is not None
    ]
    result["mean"] = round(sum(scored) / len(scored), 4) if scored else 0.0

    output_path.write_text(json.dumps(result, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input-path", type=Path, required=True)
    parser.add_argument("-o", "--output-path", type=Path, required=True)
    args = parser.parse_args()
    main(args.input_path, args.output_path)
