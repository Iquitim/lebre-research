# EXP-0001b: Deep Causal Ablation Report

Detailed mechanistic breakdown of structural churn, feature survival, and candidate evidence.

## 1. Feature Survival Across Horizons

| Model | True Surv @10 | True Surv @50 | True Surv @100 | Noise Surv @10 | Noise Surv @50 | Noise Surv @100 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **B0** | 100.0% | 11.4% | 6.4% | 100.0% | 0.9% | 0.8% |
| **B1** | 100.0% | 38.1% | 31.0% | 100.0% | 2.4% | 1.2% |
| **B2** | 100.0% | 11.8% | 3.0% | 100.0% | 1.6% | 1.1% |
| **B3** | 100.0% | 64.0% | 55.5% | 100.0% | 18.4% | 8.3% |
| **B4** | 100.0% | 51.0% | 45.4% | 100.0% | 4.6% | 0.3% |


## 2. Promotion-to-Eviction Latency (Steps)

| Model | True Median Latency | True Mean Latency | Noise Median Latency | Noise Mean Latency | Redundant Repromotions |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **B0** | 19.8 | 29.9 | 15.0 | 17.0 | 30.2 |
| **B1** | 26.6 | 135.1 | 15.0 | 18.3 | 28.4 |
| **B2** | 20.5 | 31.7 | 17.0 | 19.3 | 24.0 |
| **B3** | 310.1 | 356.7 | 20.6 | 43.9 | 8.2 |
| **B4** | 108.9 | 238.9 | 20.0 | 23.6 | 11.8 |


## 3. Churn and Promotion Purity

| Model | True Promotions | False Promotions | Promotion Precision | Churn / 100 steps |
| :--- | :--- | :--- | :--- | :--- |
| **B0** | 40.2 | 511.6 | 7.3% | 55.2 |
| **B1** | 38.4 | 818.0 | 4.5% | 85.4 |
| **B2** | 33.6 | 427.8 | 7.3% | 46.1 |
| **B3** | 18.0 | 315.0 | 5.6% | 33.0 |
| **B4** | 21.6 | 371.2 | 5.8% | 39.3 |
