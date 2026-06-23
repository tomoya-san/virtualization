"""
Common benchmark runner.

Runs one of the workload programs (cpu_bound or io_bound) for a number of
trials, times each trial with a high-resolution monotonic clock, prints summary
statistics, and appends every trial as a row to a CSV file. Run this script
identically on the native macOS host and inside the UTM guest; the only
difference between the two runs should be the (virtual vs physical) CPU.

Examples
--------
Native host:
    python3 benchmark.py --program cpu --label native --trials 10
    python3 benchmark.py --program io  --label native --trials 10

UTM guest (same Python version!):
    python3 benchmark.py --program cpu --label guest --trials 10
    python3 benchmark.py --program io  --label guest --trials 10

Results accumulate in results.csv so you can compare native vs guest afterwards.
"""

import argparse
import csv
import os
import platform
import statistics
import sys
import time
from datetime import datetime, timezone

import cpu_bound
import io_bound

PROGRAMS = {
    "cpu": cpu_bound,
    "io": io_bound,
}

CSV_FIELDS = [
    "timestamp_utc",
    "label",
    "program",
    "workload",
    "trial",
    "seconds",
    "result",
    "python_version",
    "machine",
    "system",
]


def describe_environment() -> dict:
    """Collect the parts of the environment we want recorded in every row."""
    return {
        "python_version": platform.python_version(),
        "machine": platform.machine(),
        "system": f"{platform.system()} {platform.release()}",
    }


def run_benchmark(program_key: str, workload: int, trials: int, warmup: int):
    module = PROGRAMS[program_key]
    fn = module.run

    # Warmup runs are not recorded; they prime caches, the allocator, branch
    # predictors, etc., so the measured trials are more stable.
    for _ in range(warmup):
        fn(workload)

    samples = []
    result = None
    for i in range(trials):
        start = time.perf_counter()
        result = fn(workload)
        elapsed = time.perf_counter() - start
        samples.append(elapsed)
        print(f"  trial {i + 1:>3}/{trials}: {elapsed:.6f} s")
    return samples, result


def summarize(samples):
    return {
        "min": min(samples),
        "mean": statistics.mean(samples),
        "median": statistics.median(samples),
        "max": max(samples),
        "stdev": statistics.stdev(samples) if len(samples) > 1 else 0.0,
    }


def append_csv(path: str, rows: list):
    file_exists = os.path.exists(path)
    with open(path, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        if not file_exists:
            writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--program", required=True, choices=PROGRAMS.keys(),
                        help="which workload to run: 'cpu' or 'io'")
    parser.add_argument("--label", required=True,
                        help="run label, e.g. 'native' or 'guest'")
    parser.add_argument("--trials", type=int, default=10,
                        help="number of timed trials (default: 10)")
    parser.add_argument("--warmup", type=int, default=2,
                        help="number of untimed warmup runs (default: 2)")
    parser.add_argument("--workload", type=int, default=None,
                        help="workload size; defaults to the program's DEFAULT_WORKLOAD")
    parser.add_argument("--csv", default="results.csv",
                        help="output CSV path (default: results.csv)")
    args = parser.parse_args()

    module = PROGRAMS[args.program]
    workload = args.workload if args.workload is not None else module.DEFAULT_WORKLOAD

    env = describe_environment()
    print(f"program       : {args.program}")
    print(f"label         : {args.label}")
    print(f"workload      : {workload}")
    print(f"trials/warmup : {args.trials}/{args.warmup}")
    print(f"python        : {env['python_version']}  ({sys.executable})")
    print(f"machine       : {env['machine']}  system: {env['system']}")
    print("-" * 48)

    samples, result = run_benchmark(args.program, workload, args.trials, args.warmup)
    stats = summarize(samples)

    print("-" * 48)
    print(f"result        : {result}")
    print(f"min   : {stats['min']:.6f} s")
    print(f"mean  : {stats['mean']:.6f} s")
    print(f"median: {stats['median']:.6f} s")
    print(f"max   : {stats['max']:.6f} s")
    print(f"stdev : {stats['stdev']:.6f} s")

    timestamp = datetime.now(timezone.utc).isoformat()
    rows = []
    for i, sec in enumerate(samples, start=1):
        row = {
            "timestamp_utc": timestamp,
            "label": args.label,
            "program": args.program,
            "workload": workload,
            "trial": i,
            "seconds": f"{sec:.9f}",
            "result": result,
        }
        row.update(env)
        rows.append(row)

    append_csv(args.csv, rows)
    print(f"\nappended {len(rows)} rows to {args.csv}")


if __name__ == "__main__":
    main()
