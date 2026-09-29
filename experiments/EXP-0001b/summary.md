# EXP-0001b: Causal Ablation of Structural Churn and Noisy Evidence

## 1. Executive Summary
- **Primary Diagnosis**: `ZERO_SLACK_CHURN_PRIMARY`
- **Best Variant**: `B3`
- **Status**: `PARTIAL_GO`
- **Dense Reference (MSE R2)**: `0.0339` (Compute: `602.0` FLOPs/step)
- **Best Variant (MSE R2)**: `0.7364` (Compute: `100.0` FLOPs/step, `0.166x` of Dense)

## 2. Consolidated Results Table (Mean ± Std over 5 seeds)

| Model   | Global_MSE         | R1_MSE           | R2_MSE           | Recovery_Latency   | Final_Recall   | Final_Precision   | Support_F1    | True_Prom   | False_Prom    | Prom_Precision   | True_Surv_10   | True_Surv_50   | True_Surv_100   | Noise_Surv_10   | Noise_Surv_50   | Noise_Surv_100   | Churn_per_100   |   FLOPs_step | Compute_vs_Dense   |   Memory_bytes |
|:--------|:-------------------|:-----------------|:-----------------|:-------------------|:---------------|:------------------|:--------------|:------------|:--------------|:-----------------|:---------------|:---------------|:----------------|:----------------|:----------------|:-----------------|:----------------|-------------:|:-------------------|---------------:|
| Dense   | 1.4380 ± 0.0127    | 0.0218 ± 0.0028  | 0.0339 ± 0.0071  | 931.2 ± 41.2       | 100.0% ± 0.0%  | 5.0% ± 0.0%       | 0.095 ± 0.000 | 0.0 ± 0.0   | 0.0 ± 0.0     | 0.0% ± 0.0%      | 0.0%           | 0.0%           | 0.0%            | 0.0%            | 0.0%            | 0.0%             | 0.0 ± 0.0       |        602   | 1.000x             |           1600 |
| Fixed   | 11.1320 ± 0.7589   | 11.1002 ± 2.3175 | 12.2683 ± 2.3760 | 1000.0 ± 0.0       | 4.0% ± 8.9%    | 4.0% ± 8.9%       | 0.040 ± 0.089 | 0.0 ± 0.0   | 0.0 ± 0.0     | 0.0% ± 0.0%      | 0.0%           | 0.0%           | 0.0%            | 0.0%            | 0.0%            | 0.0%             | 0.0 ± 0.0       |         32   | 0.053x             |             80 |
| B0      | 9.2093 ± 0.1715    | 9.4332 ± 2.0358  | 9.6363 ± 0.9518  | 1000.0 ± 0.0       | 16.0% ± 21.9%  | 16.0% ± 21.9%     | 0.160 ± 0.219 | 40.2 ± 2.7  | 511.6 ± 17.3  | 7.3% ± 0.6%      | 100.0%         | 11.4%          | 6.4%            | 100.0%          | 0.9%            | 0.8%             | 55.2 ± 1.5      |         52   | 0.086x             |            880 |
| B1      | 4.5632 ± 0.9807    | 1.2644 ± 1.1630  | 2.1234 ± 2.5417  | 823.8 ± 276.3      | 84.0% ± 35.8%  | 42.0% ± 17.9%     | 0.560 ± 0.239 | 38.4 ± 4.7  | 818.0 ± 121.1 | 4.5% ± 0.5%      | 100.0%         | 38.1%          | 31.0%           | 100.0%          | 2.4%            | 1.2%             | 85.4 ± 12.4     |         81.9 | 0.136x             |            960 |
| B2      | 9.8668 ± 0.3745    | 9.6753 ± 2.3096  | 11.6243 ± 1.8690 | 1000.0 ± 0.0       | 8.0% ± 11.0%   | 8.0% ± 11.0%      | 0.080 ± 0.110 | 33.6 ± 3.4  | 427.8 ± 27.0  | 7.3% ± 0.8%      | 100.0%         | 11.8%          | 3.0%            | 100.0%          | 1.6%            | 1.1%             | 46.1 ± 2.7      |         72   | 0.120x             |           2080 |
| B3      | 4.1697 ± 0.9898    | 1.6352 ± 2.4660  | 0.7364 ± 0.8698  | 856.4 ± 173.1      | 96.0% ± 8.9%   | 48.0% ± 4.5%      | 0.640 ± 0.060 | 18.0 ± 4.9  | 315.0 ± 114.3 | 5.6% ± 1.2%      | 100.0%         | 64.0%          | 55.5%           | 100.0%          | 18.4%           | 8.3%             | 33.0 ± 11.8     |        100   | 0.166x             |           2160 |
| B4      | 89.2787 ± 175.6818 | 1.3234 ± 1.3352  | 0.8467 ± 1.4344  | 782.2 ± 240.1      | 92.0% ± 17.9%  | 88.6% ± 25.6%     | 0.900 ± 0.224 | 21.6 ± 1.1  | 371.2 ± 101.6 | 5.8% ± 1.3%      | 100.0%         | 51.0%          | 45.4%           | 100.0%          | 4.6%            | 0.3%             | 39.3 ± 10.2     |         98.7 | 0.164x             |           2160 |

## 3. Primary Causal Contrasts

- **Slack Effect (B1 - B0)**: R2 MSE Δ = -7.5129, Final Recall Δ = +68.0%
- **Evidence Effect (B2 - B0)**: R2 MSE Δ = +1.9879, Final Recall Δ = -8.0%
- **Interaction Effect (B3 vs min(B1, B2))**: R2 MSE Δ = -1.3870, Final Recall Δ = +12.0%
- **Pruning Effect (B4 - B3)**: R2 MSE Δ = +0.1102, Final Recall Δ = -4.0%

## 4. Required Decisions & Component Disposition

- **STRUCTURAL_SLACK**: `KEEP`
- **MULTIPROBE_EVIDENCE**: `REMOVE`
- **MATURITY_PRUNING**: `REMOVE`

## 5. Required Practical Answers

### Q64: Can the sparse online learner now recover dynamic true structure with >= 80% recall, R2 error <= 2x Dense, and <= 25% compute?
**Answer: NO**

### Q65: Which minimal intervention explains the improvement?
**Answer**: `ZERO_SLACK_CHURN_PRIMARY`. Detailed justification in ablation report.

### Q66: Did we fix the original failure, or merely hide it with extra capacity?
**Answer**: Evidence suggests capacity absorption played a significant role.

