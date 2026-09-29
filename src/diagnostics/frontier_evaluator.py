import math
from typing import Dict, Any, List, Set, Tuple, Optional
import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr

def compute_gamma(
    beta_min: float,
    sigma_residual: float,
    d_noise: int,
    n_effective: float
) -> float:
    """
    Computes the diagnostic structural difficulty index Gamma:
    Gamma = beta_min / (sigma_residual * sqrt(2 * ln(D_noise) / n_effective))
    """
    d_n = max(2, d_noise)
    n_eff = max(0.5, n_effective)
    sig_res = max(1e-6, sigma_residual)
    denom = sig_res * math.sqrt(2.0 * math.log(d_n) / n_eff)
    return float(beta_min / denom) if denom > 0 else 0.0

def compute_gamma_resource(
    gamma: float,
    total_budget: int,
    d_noise: int
) -> float:
    """
    Computes resource-normalized difficulty index:
    Gamma_resource = Gamma * sqrt(probe_budget_per_candidate)
    """
    d_n = max(2, d_noise)
    budget_per_cand = float(total_budget) / float(d_n)
    return float(gamma * math.sqrt(budget_per_cand))

def compute_energy_metrics(
    active_support: List[int],
    true_support: Set[int],
    true_beta: np.ndarray
) -> Tuple[float, float, float]:
    r"""
    Computes:
    1. Omitted true energy: sum_{j in S* \ S_t} beta_j^2
    2. Energy-weighted recall: sum_{j in S* cap S_t} beta_j^2 / sum_{j in S*} beta_j^2
    3. Raw support recall: |S* cap S_t| / |S*|
    """
    active_set = set(active_support)
    total_true_energy = 0.0
    recovered_true_energy = 0.0
    omitted_true_energy = 0.0

    for idx in true_support:
        val_sq = float(true_beta[idx] ** 2)
        total_true_energy += val_sq
        if idx in active_set:
            recovered_true_energy += val_sq
        else:
            omitted_true_energy += val_sq

    energy_weighted_recall = (recovered_true_energy / total_true_energy) if total_true_energy > 0 else 1.0
    overlap = len(active_set.intersection(true_support))
    raw_recall = float(overlap / len(true_support)) if len(true_support) > 0 else 1.0

    return omitted_true_energy, energy_weighted_recall, raw_recall

def classify_regime_identifiability(
    full_support_occupancy: float,
    t_evidence: float,
    t_post: float,
    final_recall: float,
    post_shift_mse: float,
    dense_mse: float,
    pct_dense_compute: float
) -> str:
    """
    Classifies an environment regime into:
    - IDENTIFIABLE: Occupancy >= 75% AND T_evidence <= 70 AND T_post <= 80 AND compute <= 25% Dense
    - PARTIALLY_IDENTIFIABLE: Final Recall >= 90% AND MSE <= Dense, but identification gate not fully met
    - NON_IDENTIFIABLE_UNDER_BUDGET: Poor structural recovery
    """
    if (full_support_occupancy >= 0.75 and 
        t_evidence <= 70.0 and 
        t_post <= 80.0 and 
        pct_dense_compute <= 25.0):
        return "IDENTIFIABLE"
    elif final_recall >= 0.90 and post_shift_mse <= dense_mse * 1.5:
        return "PARTIALLY_IDENTIFIABLE"
    else:
        return "NON_IDENTIFIABLE_UNDER_BUDGET"

def classify_prediction_sufficient(
    post_shift_mse: float,
    dense_mse: float,
    sparse_oracle_mse: float,
    pct_dense_compute: float
) -> Tuple[bool, bool]:
    """
    Evaluates:
    - is_sufficient: MSE <= Dense MSE AND compute <= 25% Dense
    - is_strong: MSE <= Sparse Oracle * 1.25 AND compute <= 25% Dense
    """
    compute_ok = (pct_dense_compute <= 25.0)
    is_sufficient = (post_shift_mse <= dense_mse and compute_ok)
    is_strong = (post_shift_mse <= sparse_oracle_mse * 1.25 and compute_ok)
    return is_sufficient, is_strong

def classify_2x2_matrix(
    identifiability_label: str,
    is_prediction_sufficient: bool
) -> str:
    """
    Returns cell A, B, C, or D:
    A: Identification Good, Prediction Good
    B: Identification Poor, Prediction Good
    C: Identification Good, Prediction Poor
    D: Identification Poor, Prediction Poor
    """
    id_good = (identifiability_label == "IDENTIFIABLE")
    if id_good and is_prediction_sufficient:
        return "A"
    elif not id_good and is_prediction_sufficient:
        return "B"
    elif id_good and not is_prediction_sufficient:
        return "C"
    else:
        return "D"

def compute_metric_correlations(
    df_regimes: pd.DataFrame
) -> pd.DataFrame:
    """
    Computes Pearson and Spearman correlation between post_shift_mse and:
    - full_support_occupancy
    - raw_recall
    - energy_weighted_recall
    - omitted_true_energy
    - t_total
    """
    metrics = [
        ("full_support_occupancy", "Full-Support Occupancy"),
        ("mean_regime_recall", "Raw Support Recall"),
        ("energy_weighted_recall", "Energy-Weighted Recall"),
        ("omitted_true_energy", "Omitted True Energy"),
        ("t_total", "Structural Latency (T_total)")
    ]

    rows = []
    mse_vals = df_regimes["post_shift_mse"].values

    for col, display_name in metrics:
        if col not in df_regimes.columns:
            continue
        col_vals = df_regimes[col].values
        # Filter out NaN
        valid_mask = ~np.isnan(col_vals) & ~np.isnan(mse_vals)
        if np.sum(valid_mask) < 3:
            continue

        c_v = col_vals[valid_mask]
        m_v = mse_vals[valid_mask]

        p_corr, p_val = pearsonr(c_v, m_v)
        s_corr, s_val = spearmanr(c_v, m_v)

        rows.append({
            "metric_column": col,
            "metric_name": display_name,
            "pearson_r": float(p_corr),
            "pearson_p_value": float(p_val),
            "spearman_rho": float(s_corr),
            "spearman_p_value": float(s_val),
            "sample_size": int(np.sum(valid_mask))
        })

    return pd.DataFrame(rows)
