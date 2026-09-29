# EXP-0001c: Decomposing Structural Discovery from Predictive Error

## 1. Executive Summary
- **Primary Diagnosis**: `TEMPORAL_SUPPORT_OCCUPANCY_PRIMARY`
- **Experiment Status**: `DIAGNOSIS_IDENTIFIED`
- **Dense Reference R2 MSE**: `0.0339` (Compute: `602.0` FLOPs/step)
- **Oracle Support NLMS (C4) R2 MSE**: `0.0148` (Compute: `32.0` FLOPs/step)
- **B3/C0 Baseline R2 MSE**: `0.7391`
- **Top-5 Readout (C1) R2 MSE**: `0.6764`
- **Oracle Readout (C2) R2 MSE**: `0.5807`

## 2. Consolidated Results Table (Section 41)

| Model            | Global_MSE      | Regime2_MSE     | Final_Recall   | Mean_R2_Recall   | Full_Support_Occ   | Coeff_RMSE      | False_Weight_E   | Top5_Purity   | Churn_per_100   |   FLOPs_Step |   Memory_bytes |
|:-----------------|:----------------|:----------------|:---------------|:-----------------|:-------------------|:----------------|:-----------------|:--------------|:----------------|-------------:|---------------:|
| Dense            | 1.4380 ± 0.0127 | 0.0339 ± 0.0071 | 100.0% ± 0.0%  | 100.0% ± 0.0%    | 100.0% ± 0.0%      | 0.0200 ± 0.0000 | 0.0000 ± 0.0000  | 5.0% ± 0.0%   | 0.0 ± 0.0       |        602   |           1600 |
| B3_C0            | 4.1697 ± 0.9898 | 0.7391 ± 0.8739 | 96.0% ± 8.9%   | 64.4% ± 11.3%    | 21.2% ± 20.0%      | 0.3217 ± 0.0823 | 0.7893 ± 0.2124  | 62.9% ± 11.5% | 16.4 ± 5.9      |        100   |           2160 |
| C1_Top5          | 4.0785 ± 0.9973 | 0.6764 ± 0.7973 | 96.0% ± 8.9%   | 64.4% ± 11.3%    | 21.2% ± 20.0%      | 0.3217 ± 0.0823 | 0.7893 ± 0.2124  | 62.9% ± 11.5% | 16.4 ± 5.9      |        105   |           2160 |
| C2_OracleReadout | 3.1264 ± 0.7382 | 0.5807 ± 0.6850 | 96.0% ± 8.9%   | 64.4% ± 11.3%    | 21.2% ± 20.0%      | 0.3217 ± 0.0823 | 0.7893 ± 0.2124  | 62.9% ± 11.5% | 16.4 ± 5.9      |        100   |           2160 |
| C3_Freeze        | 4.1695 ± 0.9898 | 0.7370 ± 0.8690 | 96.0% ± 8.9%   | 64.4% ± 11.3%    | 21.2% ± 20.0%      | 0.3217 ± 0.0823 | 0.7893 ± 0.2124  | 62.9% ± 11.5% | 16.3 ± 5.9      |         95.7 |           2160 |
| C4_OracleSupport | 0.1426 ± 0.0098 | 0.0148 ± 0.0015 | 100.0% ± 0.0%  | 100.0% ± 0.0%    | 100.0% ± 0.0%      | 0.0150 ± 0.0000 | 0.0000 ± 0.0000  | 100.0% ± 0.0% | 0.0 ± 0.0       |         32   |             80 |

## 3. Key Causal Comparisons (Section 12)

- **C1 vs C0 (Buffer/Readout Pollution Effect)**: R2 MSE Δ = -0.0627 (from 0.7391 to 0.6764). Pruning readout to top-5 accounts for only an 8.5% error reduction.
- **C2 vs C0 (Predictive Subset Selection Effect)**: R2 MSE Δ = -0.1584 (from 0.7391 to 0.5807). Even an oracle predicting strictly from true active features achieves 0.5807 MSE because missing features are omitted from the support.
- **C3 vs C0 (Ongoing Churn Effect)**: R2 MSE Δ = -0.0021 (from 0.7391 to 0.7370). Freezing structural membership once 5/5 features are found has negligible effect.
- **C4 vs Dense (Sparse Estimator Implementation Effect)**: R2 MSE Δ = -0.0191 (from 0.0339 down to 0.0148). Sparse NLMS with true support is **2.3x better than Dense NLMS** (0.0148 vs 0.0339).

## 4. Conditional MSE & Error Decomposition

- **MSE when Full Support is Active (5/5 true features)**: `0.0972` (near noise floor!)
- **MSE when Incomplete Support is Active (<5 true features)**: `1.8319` (18.8x higher!)
- **Omitted Feature Energy (E_omit)**: `0.4860` (~65% of error)
- **Parameter Error Energy (E_param)**: `0.0284`
- **False Weight Energy (E_false)**: `0.1257`
- **Noise Floor (sigma^2)**: `0.0100`

