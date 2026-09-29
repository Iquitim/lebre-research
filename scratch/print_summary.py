import csv
import numpy as np
from collections import defaultdict

data = defaultdict(lambda: defaultdict(list))
with open("experiments/RESOURCE-ACCOUNTING-RECONCILIATION-01/RESOURCE_ACCOUNTING_01_STEP_COUNTS.csv", "r", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        p = row["provider_id"]
        data[p]["fp"].append(float(row["fp_flops_mean"]))
        data[p]["int"].append(float(row["int_ops_mean"]))
        data[p]["f1"].append(float(row["f1"]))
        data[p]["emse"].append(float(row["emse"]))

print("--- GRAND MEANS ACROSS 60 RUNS (6 TASKS x 10 SEEDS) ---")
for p in ["H0_EXACT_FP32", "H1_FP16", "H2_INT16", "H3_INT8", "H4_MIXED"]:
    print(f"{p:15s} | FP FLOPs: {np.mean(data[p]['fp']):6.2f} | INT Ops: {np.mean(data[p]['int']):6.2f} | F1: {np.mean(data[p]['f1']):.4f} | EMSE: {np.mean(data[p]['emse']):.6f}")
