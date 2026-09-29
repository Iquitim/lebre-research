#!/usr/bin/env python3
"""
run_resource_accounting_audit.py: Standardized Execution Engine for RESOURCE-ACCOUNTING-RECONCILIATION-01.
Executes the standardized 300 runs (5 providers x 6 tasks x 10 audit seeds),
measures detailed resource distributions, host microbenchmarks, and exports all CSVs.
"""

import os
import sys
import time
import math
import csv
import platform
import numpy as np
from pathlib import Path

# Add project root to sys.path
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from collections import defaultdict
from scratch.run_bounded_history_experiments import create_provider
from scratch.bench_bounded_history import generate_stream
from scratch.resource_accounting_instrumentation import (
    ResourceCounter, InstrumentedAdaptiveFilter
)

EXP_DIR = Path("experiments/RESOURCE-ACCOUNTING-RECONCILIATION-01")
FIG_DIR = EXP_DIR / "figures"
EXP_DIR.mkdir(parents=True, exist_ok=True)
FIG_DIR.mkdir(parents=True, exist_ok=True)

PROVIDERS = [
    ("H0_EXACT_FP32", "H0: Exact FP32"),
    ("H1_FP16", "H1: FP16"),
    ("H2_INT16", "H2: INT16"),
    ("H3_INT8", "H3: INT8"),
    ("H4_MIXED", "H4: Mixed FP16/INT8")
]

TASKS = [
    ("BH1", "Static Single Delay"),
    ("BH4", "Support Relocation / Shift"),
    ("BH10", "Channel Quiescence & Silence"),
    ("BH9", "Memoryless Negative Control"),
    ("BH11", "Continuous Linear State-Space"),
    ("BH8", "Complex Multi-Lag Stress")
]

SEEDS = list(range(1201, 1211)) # 10 audit seeds

def run_simulation(provider_key, task_id, seed, T=5000):
    D = 5
    L_max = 32
    sigma_v = 0.1
    
    # Generate stream
    X, y, meta = generate_stream(task_id, seed=seed, T=T, D=D, L_max=L_max, sigma_v=sigma_v)
    
    # Initialize provider
    prov = create_provider(provider_key, d_features=D, l_max=L_max)
    model = InstrumentedAdaptiveFilter(prov, d_features=D, l_max=L_max, k_max=4)
    
    # Tracking buffers
    step_fp_flops = np.zeros(T, dtype=np.int32)
    step_int_ops = np.zeros(T, dtype=np.int32)
    step_bytes_read = np.zeros(T, dtype=np.int32)
    step_bytes_written = np.zeros(T, dtype=np.int32)
    step_bytes_moved = np.zeros(T, dtype=np.int32)
    step_branches = np.zeros(T, dtype=np.int32)
    sq_errors = np.zeros(T, dtype=np.float32)
    
    comp_totals = defaultdict(ResourceCounter)
    
    for t in range(T):
        y_hat, e_live, comp_counters = model.step(X[t], y[t], t)
        sq_errors[t] = e_live ** 2
        
        # Aggregate step totals
        step_counter = ResourceCounter()
        for c_name, c_obj in comp_counters.items():
            step_counter.add(c_obj)
            comp_totals[c_name].add(c_obj)
            
        step_fp_flops[t] = step_counter.total_fp_flops_standardized
        step_int_ops[t] = step_counter.total_integer_ops
        step_bytes_read[t] = step_counter.bytes_read
        step_bytes_written[t] = step_counter.bytes_written
        step_bytes_moved[t] = step_counter.total_bytes_moved
        step_branches[t] = step_counter.branches
        
    # Evaluation post-warmup (steps 1000..5000)
    eval_slice = sq_errors[1000:]
    mse_eval = float(np.mean(eval_slice))
    emse_eval = max(0.0, mse_eval - meta["noise_var"])
    
    # Tap support recovery at t=T
    final_active_set = set((t_['i'], t_['k']) for t_ in model.active_taps)
    gt_taps = meta.get("active_taps", [])
    gt_active_set = set((t_[0], t_[1]) for t_ in gt_taps)
    
    if len(gt_active_set) == 0:
        f1 = 1.0 if len(final_active_set) == 0 else 0.0
        win = 1 if len(final_active_set) == 0 else 0
    else:
        tp = len(final_active_set.intersection(gt_active_set))
        prec = tp / len(final_active_set) if len(final_active_set) > 0 else 0.0
        rec = tp / len(gt_active_set) if len(gt_active_set) > 0 else 0.0
        f1 = (2 * prec * rec / (prec + rec)) if (prec + rec) > 0 else 0.0
        win = 1 if final_active_set == gt_active_set else 0

    mem = prov.get_memory_breakdown()
    
    result = {
        'provider_id': provider_key,
        'task_id': task_id,
        'seed': seed,
        'mse': mse_eval,
        'emse': emse_eval,
        'f1': f1,
        'win': win,
        'persistent_bytes': mem['persistent_bytes'],
        'history_bytes': mem['history_bytes'],
        # Per-step statistics
        'fp_flops_mean': float(np.mean(step_fp_flops)),
        'fp_flops_median': float(np.median(step_fp_flops)),
        'fp_flops_p95': float(np.percentile(step_fp_flops, 95)),
        'fp_flops_p99': float(np.percentile(step_fp_flops, 99)),
        'fp_flops_max': int(np.max(step_fp_flops)),
        'int_ops_mean': float(np.mean(step_int_ops)),
        'int_ops_median': float(np.median(step_int_ops)),
        'int_ops_p95': float(np.percentile(step_int_ops, 95)),
        'int_ops_max': int(np.max(step_int_ops)),
        'bytes_read_mean': float(np.mean(step_bytes_read)),
        'bytes_written_mean': float(np.mean(step_bytes_written)),
        'bytes_moved_mean': float(np.mean(step_bytes_moved)),
        'bytes_moved_p95': float(np.percentile(step_bytes_moved, 95)),
        'bytes_moved_max': int(np.max(step_bytes_moved)),
        'branches_mean': float(np.mean(step_branches)),
        'comp_totals': comp_totals,
        'T': T
    }
    return result


def run_host_microbenchmark():
    print("\n[HOST BENCHMARK] Executing host diagnostic latency microbenchmark...")
    D = 5
    L_max = 32
    T_bench = 10000
    N_repeats = 10
    
    np.random.seed(42)
    X = np.random.randn(T_bench, D).astype(np.float32)
    y = np.random.randn(T_bench).astype(np.float32)
    
    bench_results = []
    
    for p_key, p_label in [("H0_EXACT_FP32", "H0: Exact FP32"), ("H3_INT8", "H3: INT8")]:
        latencies = []
        # Warm-up (1,000 steps)
        prov_warm = create_provider(p_key, d_features=D, l_max=L_max)
        mod_warm = InstrumentedAdaptiveFilter(prov_warm, d_features=D, l_max=L_max)
        for t in range(1000):
            mod_warm.step(X[t % T_bench], y[t % T_bench], t)
            
        # Benchmark runs
        for rep in range(N_repeats):
            prov = create_provider(p_key, d_features=D, l_max=L_max)
            mod = InstrumentedAdaptiveFilter(prov, d_features=D, l_max=L_max)
            t0 = time.perf_counter()
            for t in range(T_bench):
                mod.step(X[t], y[t], t)
            t1 = time.perf_counter()
            us_per_step = ((t1 - t0) / T_bench) * 1e6
            latencies.append(us_per_step)
            
        bench_results.append({
            'provider_id': p_key,
            'label': p_label,
            'mean_us': float(np.mean(latencies)),
            'median_us': float(np.median(latencies)),
            'p95_us': float(np.percentile(latencies, 95)),
            'min_us': float(np.min(latencies)),
            'max_us': float(np.max(latencies)),
            'std_us': float(np.std(latencies)),
            'cpu': platform.processor(),
            'machine': platform.machine(),
            'os': platform.platform(),
            'python_version': platform.python_version(),
            'numpy_version': np.__version__
        })
        print(f"  {p_label:20s}: Median = {np.median(latencies):.2f} us/step (P95 = {np.percentile(latencies, 95):.2f} us/step)")
        
    return bench_results


def main():
    print("==================================================")
    print("STARTING RESOURCE-ACCOUNTING-RECONCILIATION-01 AUDIT")
    print(f"Audit Configuration: 5 Providers x 6 Tasks x 10 Seeds = {len(PROVIDERS)*len(TASKS)*len(SEEDS)} Runs")
    print("==================================================")
    
    all_results = []
    run_idx = 0
    t_start = time.time()
    
    for p_key, p_label in PROVIDERS:
        for task_id, task_name in TASKS:
            for seed in SEEDS:
                res = run_simulation(p_key, task_id, seed)
                all_results.append(res)
                run_idx += 1
                if run_idx % 50 == 0:
                    print(f"  Completed {run_idx}/{len(PROVIDERS)*len(TASKS)*len(SEEDS)} runs ({time.time() - t_start:.1f}s)...")
                    
    print(f"\nAll {len(all_results)} simulations completed in {time.time() - t_start:.2f}s.")
    
    # -------------------------------------------------------------
    # 1. Export RESOURCE_ACCOUNTING_01_STEP_COUNTS.csv
    # -------------------------------------------------------------
    step_csv_path = EXP_DIR / "RESOURCE_ACCOUNTING_01_STEP_COUNTS.csv"
    with open(step_csv_path, 'w', newline='', encoding='utf-8') as f:
        fieldnames = [
            'provider_id', 'task_id', 'seed', 'emse', 'f1', 'win', 'persistent_bytes',
            'fp_flops_mean', 'fp_flops_median', 'fp_flops_p95', 'fp_flops_max',
            'int_ops_mean', 'int_ops_median', 'int_ops_p95', 'int_ops_max',
            'bytes_read_mean', 'bytes_written_mean', 'bytes_moved_mean', 'bytes_moved_p95',
            'branches_mean'
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in all_results:
            row_dict = {k: r[k] for k in fieldnames}
            writer.writerow(row_dict)
    print(f"  -> Exported {step_csv_path}")

    # -------------------------------------------------------------
    # 2. Export RESOURCE_ACCOUNTING_01_COMPONENT_COUNTS.csv
    # -------------------------------------------------------------
    # Aggregate component totals across seeds per (provider, task)
    comp_csv_path = EXP_DIR / "RESOURCE_ACCOUNTING_01_COMPONENT_COUNTS.csv"
    comp_names = [
        'HISTORY_WRITE', 'BASE_FORWARD', 'ACTIVE_FORWARD', 'RECURRENT_FORWARD',
        'SHADOW_SCORING', 'BASE_UPDATE', 'ACTIVE_UPDATE', 'RECURRENT_UPDATE',
        'CANDIDATE_PROBING', 'PROMOTION_EVICTION'
    ]
    
    with open(comp_csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'provider_id', 'component', 'fp_flops_mean', 'mac_count_mean',
            'int_ops_mean', 'bytes_read_mean', 'bytes_written_mean', 'bytes_moved_mean'
        ])
        
        for p_key, _ in PROVIDERS:
            p_runs = [r for r in all_results if r['provider_id'] == p_key]
            total_steps = sum(r['T'] for r in p_runs)
            for c_name in comp_names:
                total_c = ResourceCounter()
                for r in p_runs:
                    total_c.add(r['comp_totals'][c_name])
                writer.writerow([
                    p_key,
                    c_name,
                    round(total_c.total_fp_flops_standardized / total_steps, 4),
                    round(total_c.mac_count / total_steps, 4),
                    round(total_c.total_integer_ops / total_steps, 4),
                    round(total_c.bytes_read / total_steps, 4),
                    round(total_c.bytes_written / total_steps, 4),
                    round(total_c.total_bytes_moved / total_steps, 4)
                ])
    print(f"  -> Exported {comp_csv_path}")

    # -------------------------------------------------------------
    # 3. Export RESOURCE_ACCOUNTING_01_MEMORY_TRAFFIC.csv
    # -------------------------------------------------------------
    mem_csv_path = EXP_DIR / "RESOURCE_ACCOUNTING_01_MEMORY_TRAFFIC.csv"
    with open(mem_csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'provider_id', 'persistent_bytes', 'history_buffer_bytes',
            'bytes_read_per_step', 'bytes_written_per_step', 'total_bytes_moved_per_step',
            'fp_ops_per_byte', 'arithmetic_ops_per_byte', 'memory_traffic_reduction_vs_h0'
        ])
        
        # Get baseline H0 bytes moved
        h0_runs = [r for r in all_results if r['provider_id'] == 'H0_EXACT_FP32']
        h0_moved = np.mean([r['bytes_moved_mean'] for r in h0_runs])
        
        for p_key, _ in PROVIDERS:
            p_runs = [r for r in all_results if r['provider_id'] == p_key]
            p_bytes = p_runs[0]['persistent_bytes']
            h_bytes = p_runs[0]['history_bytes']
            b_read = np.mean([r['bytes_read_mean'] for r in p_runs])
            b_write = np.mean([r['bytes_written_mean'] for r in p_runs])
            b_moved = np.mean([r['bytes_moved_mean'] for r in p_runs])
            fp_flops = np.mean([r['fp_flops_mean'] for r in p_runs])
            int_ops = np.mean([r['int_ops_mean'] for r in p_runs])
            
            fp_intensity = fp_flops / b_moved
            arith_intensity = (fp_flops + int_ops) / b_moved
            reduction = (h0_moved - b_moved) / h0_moved * 100.0
            
            writer.writerow([
                p_key, p_bytes, h_bytes,
                round(b_read, 2), round(b_write, 2), round(b_moved, 2),
                round(fp_intensity, 4), round(arith_intensity, 4),
                f"{reduction:+.1f}%"
            ])
    print(f"  -> Exported {mem_csv_path}")

    # -------------------------------------------------------------
    # 4. Export H3_INCREMENTAL_COST.csv
    # -------------------------------------------------------------
    # Decompose H3 INT8 relative to H0 FP32 across specific categories
    h3_runs = [r for r in all_results if r['provider_id'] == 'H3_INT8']
    
    h0_fp = np.mean([r['fp_flops_mean'] for r in h0_runs])
    h0_int = np.mean([r['int_ops_mean'] for r in h0_runs])
    h0_moved = np.mean([r['bytes_moved_mean'] for r in h0_runs])
    
    h3_fp = np.mean([r['fp_flops_mean'] for r in h3_runs])
    h3_int = np.mean([r['int_ops_mean'] for r in h3_runs])
    h3_moved = np.mean([r['bytes_moved_mean'] for r in h3_runs])
    
    h3_inc_path = EXP_DIR / "H3_INCREMENTAL_COST.csv"
    with open(h3_inc_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'Overhead_Category', 'Operations_Per_Step', 'Data_Type', 'Operation_Type',
            'Incremental_FLOPs', 'Incremental_Int_Ops', 'Incremental_Bytes_Moved', 'Explanation'
        ])
        
        # Write operations: dynamic scale tracking & quantization
        # D=5 channels:
        # Scale check: 5 abs + 5 compare.
        # Scale update (when active): ~0.15 updates/step * 3 FP ops.
        # Quantization: 5 div + 5 mul (10 FP), 5 round + 10 clip + 5 cast (20 Int).
        writer.writerow([
            'Input Scale Checking & Update', '5 abs + 5 cmp + 0.5 update', 'FLOAT32', 'SCALE_UPDATE',
            '+0.5', '+10.0', '0.0', 'Causal peak amplitude tracking'
        ])
        writer.writerow([
            'Input Quantization (Scaled Clip/Round)', '5 div + 5 mul + 5 round + 10 clip', 'INT8', 'QUANTIZE',
            '+10.0', '+20.0', '0.0', 'Conversion from float32 to int8'
        ])
        writer.writerow([
            'Quantized History Buffer Store', '5 int8 byte writes', 'INT8', 'STORE_BYTES',
            '0.0', '0.0', '-15.0', 'Saved 15 bytes written vs FP32'
        ])
        
        # Query operations: dequantization
        # Queries occur for active taps (K_bar ~ 1.5) + candidates (C_bar ~ 2.0) + probes (M=2)
        # Total queries ~ 5.5 / step.
        # Dequantization per query: 1 cast_int_to_fp + 1 fp_mul (q * scale / 127).
        writer.writerow([
            'Dequantization on Query', '~5.5 cast + 5.5 fp_mul', 'INT8_TO_FP', 'DEQUANTIZE',
            '+5.5', '+5.5', '-16.5', 'Unpacking queried values with 3x memory traffic saving'
        ])
        writer.writerow([
            'Scale Metadata Reads', '~5.5 scale reads', 'FLOAT32', 'LOAD_BYTES',
            '0.0', '0.0', '+22.0', 'Amortized / register-cached scale access'
        ])
        writer.writerow([
            'TOTAL_H3_INCREMENTAL_DELTA', 'Sum of all categories', 'MIXED', 'TOTAL',
            f"{h3_fp - h0_fp:+.2f}", f"{h3_int - h0_int:+.2f}", f"{h3_moved - h0_moved:+.2f}",
            'Total net incremental delta of H3 relative to H0'
        ])
    print(f"  -> Exported {h3_inc_path}")

    # -------------------------------------------------------------
    # 5. Run & Export Host Benchmark
    # -------------------------------------------------------------
    bench_data = run_host_microbenchmark()
    bench_csv_path = EXP_DIR / "RESOURCE_ACCOUNTING_01_HOST_BENCHMARK.csv"
    with open(bench_csv_path, 'w', newline='', encoding='utf-8') as f:
        fieldnames = [
            'provider_id', 'label', 'mean_us', 'median_us', 'p95_us',
            'min_us', 'max_us', 'std_us', 'cpu', 'machine', 'os',
            'python_version', 'numpy_version'
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for b in bench_data:
            writer.writerow(b)
    print(f"  -> Exported {bench_csv_path}")

    print("\nAudit Data Generation Complete!")

if __name__ == "__main__":
    main()
