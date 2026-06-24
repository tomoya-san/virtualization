"""Summarize mean and error of each experiment setting in results.csv."""

import pandas as pd

df = pd.read_csv("out/results.csv")

# Each experiment setting is identified by (label, program, workload).
grouped = df.groupby(["label", "program", "workload"])["seconds"]

summary = grouped.agg(
    n="count",
    mean="mean",
    std="std",      # sample standard deviation
).reset_index()

# Standard error of the mean = std / sqrt(n)
summary["sem"] = summary["std"] / summary["n"] ** 0.5

# 95% confidence interval half-width (normal approximation)
summary["ci95"] = 1.96 * summary["sem"]

# Format for readable output
pd.set_option("display.float_format", lambda v: f"{v:.6f}")

print(summary.to_string(index=False))

summary.to_csv("out/summary.csv", index=False)
print("\nWrote out/summary.csv")
