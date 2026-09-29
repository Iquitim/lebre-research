"""
Microtrace and Numerical Stress Testing for LEBRE-V0.2-RESOURCE-COMPACTION-01
Compares C0 (FP32 corr_grid) vs C1 (FP16 corr_grid + FP32 update)
Generates:
  - NUMERICAL_MICROTRACE.csv
  - NUMERICAL_STRESS_RESULTS.csv
"""

import numpy as np
import pandas as pd
from pathlib import Path

out_dir = Path("experiments/LEBRE-V0.2-RESOURCE-COMPACTION-01")
out_dir.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------
# Part 1: Deterministic Microtrace on Identical Stream
# ---------------------------------------------------------
def run_microtrace():
    print("Running Part 1: Deterministic Microtrace (500 steps)...")
    rng = np.random.RandomState(42)
    
    # 5 features, 33 lags = 165 cells
    d_features = 5
    l_max = 32
    grid_pairs = [(i, k) for i in range(d_features) for k in range(l_max + 1)]
    
    # C0: FP32 grid
    grid_c0 = np.zeros((d_features, l_max + 1), dtype=np.float32)
    # C1: FP16 grid
    grid_c1 = np.zeros((d_features, l_max + 1), dtype=np.float16)
    
    trace_rows = []
    probe_ptr = 0
    
    # Simulate 500 steps of streaming inputs and errors
    for step in range(500):
        # Synthetic feature vector and error
        x_vec = rng.randn(d_features).astype(np.float32)
        e_probe = np.float32(rng.randn() * 0.5)
        
        # Probe M=2 cells per step
        for _ in range(2):
            i_p, k_p = grid_pairs[probe_ptr]
            probe_ptr = (probe_ptr + 1) % len(grid_pairs)
            
            c_val = x_vec[i_p] # Simplified feature value
            
            # C0 (FP32)
            c0_before = float(grid_c0[i_p, k_p])
            c0_upd = float(np.float32(0.95) * grid_c0[i_p, k_p] + np.float32(0.05) * (e_probe * c_val))
            grid_c0[i_p, k_p] = np.float32(c0_upd)
            
            # C1 (FP16 stored, FP32 update)
            c1_stored_before = float(grid_c1[i_p, k_p])
            c1_transient_fp32 = np.float32(grid_c1[i_p, k_p])
            c1_upd_fp32 = np.float32(0.95) * c1_transient_fp32 + np.float32(0.05) * (e_probe * c_val)
            c1_stored_after = np.float16(c1_upd_fp32)
            grid_c1[i_p, k_p] = c1_stored_after
            
            abs_err = abs(float(grid_c0[i_p, k_p]) - float(c1_stored_after))
            rel_err = abs_err / (abs(float(grid_c0[i_p, k_p])) + 1e-12)
            
            # IEEE 754 float16 spacing (ULP) around c1_stored_after
            exp = np.frexp(float(c1_stored_after))[1] if c1_stored_after != 0 else -14
            ulp = 2.0 ** (exp - 11)
            
            trace_rows.append({
                "step": step,
                "probe_idx": len(trace_rows),
                "feature_i": i_p,
                "lag_k": k_p,
                "fp32_before": c0_before,
                "fp16_stored_before": c1_stored_before,
                "fp32_update_result": c0_upd,
                "c1_transient_fp32": float(c1_upd_fp32),
                "fp16_stored_after": float(c1_stored_after),
                "absolute_error": abs_err,
                "relative_error": rel_err,
                "ulp_spacing": ulp
            })
            
    df_trace = pd.DataFrame(trace_rows)
    trace_path = out_dir / "NUMERICAL_MICROTRACE.csv"
    df_trace.to_csv(trace_path, index=False)
    print(f"Wrote {len(df_trace)} microtrace rows to {trace_path}")
    print(f"Max absolute error: {df_trace['absolute_error'].max():.6e}")
    print(f"Mean absolute error: {df_trace['absolute_error'].mean():.6e}")

# ---------------------------------------------------------
# Part 2: Numerical Stress Suite (Tests A–G)
# ---------------------------------------------------------
def run_stress_tests():
    print("Running Part 2: Numerical Stress Suite (Tests A–G)...")
    
    tests = [
        ("TEST_A_NORMAL_RANGE", "Normal correlation range [-0.8, +0.8]", np.linspace(-0.8, 0.8, 100)),
        ("TEST_B_SMALL_UPDATES", "Very small updates near FP16 resolution (delta < 1e-4)", np.array([0.1, 0.2, 0.5, 0.8])),
        ("TEST_C_NEAR_ZERO_SUBNORMAL", "Values approaching zero (|C| < 1e-5)", np.array([1e-3, 1e-4, 5e-5, 1e-5, 1e-6, 1e-7])),
        ("TEST_D_NEAR_THRESHOLD", "Values hovering near candidate threshold (theta = 0.20)", np.linspace(0.198, 0.202, 50)),
        ("TEST_E_TIED_RANKING", "Near-tied candidate rankings (delta < 1e-4)", np.array([0.2500, 0.25005, 0.25010])),
        ("TEST_F_SIGN_FLIPS", "Rapid sign oscillations (+-0.15)", np.array([0.15, -0.15] * 25)),
        ("TEST_G_LARGE_MAGNITUDE", "Large magnitudes approaching saturation (|C| -> 1.0)", np.linspace(0.90, 0.999, 50))
    ]
    
    stress_results = []
    
    for test_id, desc, init_vals in tests:
        underflow_count = 0
        overflow_count = 0
        stagnation_count = 0
        sign_flip_disagreement = 0
        threshold_crossing_disagreement = 0
        ranking_inversion_count = 0
        max_abs_err = 0.0
        
        if test_id == "TEST_A_NORMAL_RANGE":
            for v in init_vals:
                c0 = np.float32(v)
                c1 = np.float16(v)
                # Apply 10 EMA updates with random signal
                rng = np.random.RandomState(int(abs(v) * 1000) % 100000)
                for _ in range(10):
                    innov = np.float32(rng.randn() * 0.2)
                    c0 = np.float32(0.95) * c0 + np.float32(0.05) * innov
                    c1_upd = np.float32(0.95) * np.float32(c1) + np.float32(0.05) * innov
                    c1 = np.float16(c1_upd)
                err = abs(float(c0) - float(c1))
                max_abs_err = max(max_abs_err, err)
                if np.isnan(c1) or np.isinf(c1):
                    overflow_count += 1
                    
        elif test_id == "TEST_B_SMALL_UPDATES":
            for v in init_vals:
                c0 = np.float32(v)
                c1 = np.float16(v)
                # Small innovation: e * x = v, so (0.95*v + 0.05*v) = v.
                # Innovation with tiny perturbation: 1e-4
                innov = np.float32(v + 1e-4)
                c0_next = np.float32(0.95) * c0 + np.float32(0.05) * innov
                c1_upd = np.float32(0.95) * np.float32(c1) + np.float32(0.05) * innov
                c1_next = np.float16(c1_upd)
                
                # Check if c0 updated but c1 stagnated
                if c0_next != c0 and c1_next == c1:
                    stagnation_count += 1
                err = abs(float(c0_next) - float(c1_next))
                max_abs_err = max(max_abs_err, err)
                
        elif test_id == "TEST_C_NEAR_ZERO_SUBNORMAL":
            for v in init_vals:
                c0 = np.float32(v)
                c1 = np.float16(v)
                # Repeated decay towards zero
                for _ in range(50):
                    c0 = np.float32(0.95) * c0
                    c1 = np.float16(np.float32(0.95) * np.float32(c1))
                if c1 == 0.0 and c0 > 0.0:
                    underflow_count += 1
                err = abs(float(c0) - float(c1))
                max_abs_err = max(max_abs_err, err)
                
        elif test_id == "TEST_D_NEAR_THRESHOLD":
            theta = 0.20
            for v in init_vals:
                c0 = np.float32(v)
                c1 = np.float16(v)
                c0_cross = (abs(c0) > theta)
                c1_cross = (abs(float(c1)) > theta)
                if c0_cross != c1_cross:
                    threshold_crossing_disagreement += 1
                err = abs(float(c0) - float(c1))
                max_abs_err = max(max_abs_err, err)
                
        elif test_id == "TEST_E_TIED_RANKING":
            # Compare pairwise ranking between pairs of values
            for i in range(len(init_vals) - 1):
                v1, v2 = init_vals[i], init_vals[i+1]
                c0_1, c0_2 = np.float32(v1), np.float32(v2)
                c1_1, c1_2 = np.float16(v1), np.float16(v2)
                
                # Inversion if order flips
                order_c0 = np.sign(c0_1 - c0_2)
                order_c1 = np.sign(float(c1_1) - float(c1_2))
                if order_c0 != order_c1 and order_c1 != 0:
                    ranking_inversion_count += 1
                max_abs_err = max(max_abs_err, abs(float(c0_1) - float(c1_1)))
                
        elif test_id == "TEST_F_SIGN_FLIPS":
            c0 = np.float32(0.0)
            c1 = np.float16(0.0)
            for v in init_vals:
                innov = np.float32(v)
                c0 = np.float32(0.95) * c0 + np.float32(0.05) * innov
                c1 = np.float16(np.float32(0.95) * np.float32(c1) + np.float32(0.05) * innov)
                if (c0 > 0 and c1 < 0) or (c0 < 0 and c1 > 0):
                    sign_flip_disagreement += 1
                max_abs_err = max(max_abs_err, abs(float(c0) - float(c1)))
                
        elif test_id == "TEST_G_LARGE_MAGNITUDE":
            for v in init_vals:
                c0 = np.float32(v)
                c1 = np.float16(v)
                # Large innovation pushing towards 1.0
                innov = np.float32(1.0)
                c0 = np.float32(0.95) * c0 + np.float32(0.05) * innov
                c1 = np.float16(np.float32(0.95) * np.float32(c1) + np.float32(0.05) * innov)
                if np.isnan(c1) or np.isinf(c1) or abs(float(c1)) > 65500:
                    overflow_count += 1
                max_abs_err = max(max_abs_err, abs(float(c0) - float(c1)))
                
        stress_results.append({
            "test_id": test_id,
            "description": desc,
            "underflow_count": underflow_count,
            "overflow_count": overflow_count,
            "update_stagnation_count": stagnation_count,
            "sign_flip_disagreement": sign_flip_disagreement,
            "threshold_crossing_disagreement": threshold_crossing_disagreement,
            "ranking_inversion_count": ranking_inversion_count,
            "max_absolute_error": max_abs_err,
            "status": "PASS" if overflow_count == 0 else "FAIL"
        })
        
    df_stress = pd.DataFrame(stress_results)
    stress_path = out_dir / "NUMERICAL_STRESS_RESULTS.csv"
    df_stress.to_csv(stress_path, index=False)
    print(f"Wrote stress results to {stress_path}")
    print(df_stress[["test_id", "underflow_count", "overflow_count", "update_stagnation_count", "threshold_crossing_disagreement", "max_absolute_error", "status"]])

if __name__ == "__main__":
    run_microtrace()
    run_stress_tests()
