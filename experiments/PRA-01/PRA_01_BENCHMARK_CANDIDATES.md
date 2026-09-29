# PRA-01: External Benchmark Candidates & Baseline Feasibility

**Audit ID:** PRA-01  
**Auditor:** Adversarial Literature Reviewer & Novelty Analyst  
**Date:** September 19, 2026  

---

## 1. Overview and Benchmarking Rules

Per Section 77 and Section 90 of the audit protocol:
- **PRA-01 does NOT run benchmarks**. It identifies and screens candidate external baselines for future evaluation.
- **Rule of Non-Favoritism**: Benchmarks must not be designed artificially to favor Track B; they must include standard public tasks alongside controlled mechanistic streams.
- **Applicability Classifications**: `APPLICABLE` | `PARTIALLY_APPLICABLE` | `NOT_APPLICABLE`.

---

## 2. Baseline Candidate Evaluations by Family

### Family A: Adaptive Filters & Sparse LMS
- **Candidate 1**: **Dense NLMS** (Widrow & Hoff 1960)
  - *Applicability*: **`APPLICABLE`** (Standard sanity ceiling for predictive convergence)
  - *Code Availability*: Standard implementation exists in repository (`src/models/`).
  - *License*: Permissive (MIT / Apache-2.0).
  - *Implementation Difficulty*: Low ($< 50$ lines of Python/NumPy).
  - *CPU Feasible*: Yes ($< 1$ ms/step).
  - *GPU Required*: No.
  - *Supports Streaming*: Yes (pure single-pass online).
- **Candidate 2**: **Zero-Attracting LMS (ZA-LMS / RZA-LMS)** (Chen et al. 2009; Gu et al. 2009)
  - *Applicability*: **`APPLICABLE`** (Direct competitor for sparse linear feature tracking)
  - *Code Availability*: Clean mathematical formulation; simple Python implementation.
  - *License*: Public academic literature.
  - *Implementation Difficulty*: Low ($< 60$ lines).
  - *CPU Feasible*: Yes.
  - *GPU Required*: No.
  - *Supports Streaming*: Yes (pure online update).
- **Candidate 3**: **Variable-Tap-Length LMS (VLMS)** (Zhao et al. 2008)
  - *Applicability*: **`APPLICABLE`** (Direct competitor for feature-lag adaptation)
  - *Code Availability*: Algorithms published in IEEE TSP; easily implementable.
  - *License*: Public academic literature.
  - *Implementation Difficulty*: Medium ($< 120$ lines).
  - *CPU Feasible*: Yes.
  - *GPU Required*: No.
  - *Supports Streaming*: Yes.

---

### Family B: Evolving / Structural Plasticity Recurrent Networks
- **Candidate 4**: **MUSE-RNN** (Das, Pratama et al. 2019)
  - *Applicability*: **`APPLICABLE`** (Primary nearest architectural neighbor)
  - *Code Availability*: MATLAB/Python implementations available in authors' repositories and research group archives.
  - *License*: Academic / Open-source.
  - *Implementation Difficulty*: Medium-High (requires Network Significance formula, drift detection module, and teacher forcing).
  - *CPU Feasible*: Yes for small node counts ($< 10$ nodes); slower if layers expand.
  - *GPU Required*: No.
  - *Supports Streaming*: Yes (prequential single-pass streaming).
- **Candidate 5**: **Minimal Resource Allocation Network (MRAN)** (Sundararajan et al. 1999)
  - *Applicability*: **`PARTIALLY_APPLICABLE`** (Establishes spatial baseline for error-triggered birth and pruning, but lacks recurrence)
  - *Code Availability*: Widely available in public academic repositories.
  - *License*: Academic open-source.
  - *Implementation Difficulty*: Medium (Extended Kalman Filter updates).
  - *CPU Feasible*: Yes for $K < 20$ units ($O(K^2)$ per step).
  - *GPU Required*: No.
  - *Supports Streaming*: Yes.

---

### Family C: Fixed-Dimension Recurrent Models (Constant Compute)
- **Candidate 6**: **Minimal Gated Recurrent Unit (Minimal GRU / 1D GRU)** (Cho et al. 2014; Zhou et al. 2016)
  - *Applicability*: **`APPLICABLE`** (Establishes the fixed-capacity neural baseline)
  - *Code Availability*: Standard PyTorch / NumPy implementations.
  - *License*: MIT.
  - *Implementation Difficulty*: Low.
  - *CPU Feasible*: Yes.
  - *GPU Required*: No for small dimensions ($d \le 8$).
  - *Supports Streaming*: Trained via online Truncated BPTT or RTRL.
- **Candidate 7**: **Linear Recurrent Unit (LRU) / S4D** (Orvieto et al. 2023; Gu et al. 2022)
  - *Applicability*: **`PARTIALLY_APPLICABLE`** (State space model baseline with linear recurrence)
  - *Code Availability*: Official PyTorch/JAX code available (`alexpolman/LRU`, `state-spaces/s4`).
  - *License*: Apache-2.0.
  - *Implementation Difficulty*: Medium.
  - *CPU Feasible*: Yes for small state sizes ($N \le 8$).
  - *GPU Required*: Only for large sequence pre-training.
  - *Supports Streaming*: Yes at inference; online training requires forward sensitivity or online gradient approximations.

---

### Family D: Echo State Networks / Reservoir Computing
- **Candidate 8**: **Online Echo State Network (ESN)** (Jaeger 2001; Lukosevicius 2012)
  - *Applicability*: **`PARTIALLY_APPLICABLE`** (Fixed random recurrent reservoir with online recursive least squares readout)
  - *Code Availability*: `pyESN` / `ReservoirPy`.
  - *License*: MIT / GPL-3.0.
  - *Implementation Difficulty*: Low ($< 100$ lines).
  - *CPU Feasible*: Yes.
  - *GPU Required*: No.
  - *Supports Streaming*: Yes (readout updates via RLS/LMS online).
  - *Limitation*: Fixed state size (e.g., $N=50$ or $100$ reservoir neurons); cannot reclaim memory or compute during state-free regimes.

---

### Family E: Continual Learning Dynamic Architectures
- **Candidate 9**: **Dynamically Expandable Network (DEN)** (Yoon et al. ICLR 2018)
  - *Applicability*: **`NOT_APPLICABLE`**
  - *Rationale*: Requires explicit task identifiers, discrete task boundaries, and offline multi-epoch retraining with selective weight retraining. Incompatible with unannounced streaming regression.
- **Candidate 10**: **Active Feature Acquisition (AFA - ACO / SEFA)** (Valancius et al. 2024; Norcliffe et al. 2025)
  - *Applicability*: **`NOT_APPLICABLE` for Streaming Adaptation**
  - *Rationale*: Requires offline batch pre-training of decision policies to acquire missing features at test time. Cannot adapt model parameters to non-stationary continuous streams.

---

## 3. Recommended Mandatory Benchmark Suite for Milestone M3 / BENCH-01

For future external validation, the following **4 mandatory baselines** provide direct, adversarial comparison without strawmen:

1. **Baseline 1 (Online Sparse Filtering)**: **Reweighted Zero-Attracting LMS (RZA-LMS)** (Gu et al. 2009). Evaluates whether Track B's budgeted probe bank delivers real FLOP savings over classic continuous shrinkage.
2. **Baseline 2 (Evolving Recurrent Neural Network)**: **MUSE-RNN** (Das et al. 2019). Evaluates whether Track B's probation period and two-timescale retention outperform statistical variance-based node pruning on streams with silent intervals.
3. **Baseline 3 (Fixed-Capacity Neural Memory)**: **Online Minimal GRU ($d=1$ and $d=4$)** trained via online RTRL. Evaluates whether autonomous birth and eviction reduce energy compared to a permanently active recurrent unit.
4. **Baseline 4 (Reservoir Computing)**: **Online Echo State Network (ESN, $N=20$)** with RLS readout. Evaluates whether learned minimal recurrence outperforms a static random recurrent reservoir.
