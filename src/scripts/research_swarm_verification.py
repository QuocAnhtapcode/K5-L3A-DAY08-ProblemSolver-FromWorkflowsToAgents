"""Run the R2 experiment with or without ticket delay in the Swarm quote."""

from __future__ import annotations

import argparse
from unittest.mock import patch

from lab8 import benchmark
from lab8.shapes import swarm_reference


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("baseline", "verified"), required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    benchmark_args = ["--shapes", "swarm", "--seeds", "11,22,33,44,55", "--out", args.out]

    if args.mode == "baseline":
        return benchmark.main(benchmark_args)

    # This alias feeds only the quote decision. MockLLM's own parser and its
    # billed parse call stay in place so the experiment changes one input.
    with patch.object(swarm_reference, "parse_delay_days", return_value=None):
        return benchmark.main(benchmark_args)


if __name__ == "__main__":
    raise SystemExit(main())
