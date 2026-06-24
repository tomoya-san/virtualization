# Execution

Use `uv run` so the correct environment is used:

```bash
# CPU-bound workload
uv run benchmark.py --program cpu --label native --trials 10

# I/O-bound workload
uv run benchmark.py --program io  --label native --trials 10
```

Run the same commands inside the UTM guest, changing only `--label` (e.g.
`--label guest`). Every trial is appended to `out/results.csv`.

Required:

- `--program {cpu,io}` — which benchmark program to run.
- `--label` — free-form text identifying the run. It can be anything; it is just
  recorded in the `label` column of `out/results.csv` so you can tell runs apart
  (e.g. `native` vs. `guest`).

Optional:

- `--trials` — number of timed trials (default `10`).
- `--warmup` — number of untimed warmup runs (default `2`).
- `--workload` — workload size (default: the program's built-in default).
- `--csv` — output CSV path (default `out/results.csv`).
