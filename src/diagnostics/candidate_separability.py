import math
from typing import Dict, Any, List, Set, Tuple, Optional
import numpy as np
import pandas as pd
from scipy.optimize import minimize

class CandidateSnapshotCollector:
    """
    Non-intrusive diagnostic collector for candidate snapshots at n in {1, 2, 3, 4, 5}.
    Operates strictly as an observer:
    - Never mutates learner state, weights, support, or queues.
    - Never calls np.random.
    - Captures candidate snapshots when probe count reaches n in {1, 2, 3, 4, 5}.
    - Records ground truth labels offline without altering causal learner execution.
    """
    def __init__(
        self,
        seed: int,
        d: int = 100,
        shift_step: int = 1000,
        r1_true_indices: Optional[List[int]] = None,
        r2_true_indices: Optional[List[int]] = None,
        target_n: Tuple[int, ...] = (1, 2, 3, 4, 5)
    ):
        self.seed = seed
        self.d = d
        self.shift_step = shift_step
        self.r1_true_indices = set(r1_true_indices or [2, 15, 33, 58, 81])
        self.r2_true_indices = set(r2_true_indices or [7, 24, 49, 66, 92])
        self.target_n = set(target_n)

        # Snapshots container
        self.snapshots: List[Dict[str, Any]] = []

        # Candidate probe history tracking for gap / age features
        self.first_probed_step: Dict[int, int] = {}
        self.probe_history: Dict[int, List[int]] = {i: [] for i in range(d)}
        self.episode_id: Dict[int, int] = {i: 0 for i in range(d)}
        self.last_cand_n: Dict[int, int] = {i: 0 for i in range(d)}

        # Residual smoothing (EMA alpha = 0.05)
        self.smoothed_residual_abs = 0.0
        self.smoothed_residual_sq = 0.0

    def observe_step(
        self,
        step: int,
        error: float,
        probed_candidates: List[int],
        learner_cand_stats: Dict[str, Any],
        active_support: List[int],
        candidate_tiers: Optional[Dict[int, str]] = None
    ):
        """
        Observes a single step of the learner immediately after candidate stats update.
        """
        # Update residual EMAs
        err_abs = abs(error)
        err_sq = error * error
        if step == 1:
            self.smoothed_residual_abs = err_abs
            self.smoothed_residual_sq = err_sq
        else:
            self.smoothed_residual_abs = 0.95 * self.smoothed_residual_abs + 0.05 * err_abs
            self.smoothed_residual_sq = 0.95 * self.smoothed_residual_sq + 0.05 * err_sq

        # Determine ground truth omitted features at this step
        current_true_support = self.r1_true_indices if step <= self.shift_step else self.r2_true_indices
        active_set = set(active_support)
        omitted_true = current_true_support - active_set
        curr_recall = len(active_set & current_true_support) / float(len(current_true_support))
        curr_k = len(active_support)

        cand_n = learner_cand_stats["n"]
        cand_mean = learner_cand_stats["mean"]
        cand_m2 = learner_cand_stats.get("m2")
        cand_pos = learner_cand_stats.get("pos")
        cand_neg = learner_cand_stats.get("neg")

        for c in probed_candidates:
            # Check for candidate reset (e.g. eviction or decay)
            if cand_n[c] < self.last_cand_n[c]:
                self.episode_id[c] += 1
                self.probe_history[c].clear()
            self.last_cand_n[c] = cand_n[c]

            # Record probe step
            self.probe_history[c].append(step)
            if c not in self.first_probed_step:
                self.first_probed_step[c] = step

            n_val = int(cand_n[c])
            if n_val in self.target_n:
                # Calculate timing features
                history = self.probe_history[c]
                if len(history) >= 2:
                    last_gap = history[-1] - history[-2]
                    gaps = [history[i] - history[i - 1] for i in range(1, len(history))]
                    mean_gap = float(np.mean(gaps))
                else:
                    last_gap = step - self.first_probed_step[c]
                    mean_gap = float(last_gap)

                cand_age = step - self.first_probed_step[c]
                time_since_first = step - history[0]

                # Statistical features
                m_val = float(cand_mean[c])
                abs_m = abs(m_val)
                pos_cnt = int(cand_pos[c]) if cand_pos is not None else 0
                neg_cnt = int(cand_neg[c]) if cand_neg is not None else 0
                sign_c = float(max(pos_cnt, neg_cnt) / n_val) if n_val > 0 else 0.0
                pos_frac = float(pos_cnt / n_val) if n_val > 0 else 0.0
                neg_frac = float(neg_cnt / n_val) if n_val > 0 else 0.0

                if cand_m2 is not None and n_val > 1:
                    var_c = float(cand_m2[c] / (n_val - 1))
                else:
                    var_c = 0.0
                std_c = math.sqrt(max(0.0, var_c))

                # Truth label (strictly offline diagnostic)
                # True if candidate is genuinely relevant and omitted at that exact time
                truth_label = 1 if (c in omitted_true) else 0

                # Tier and state
                tier_str = "COLD"
                if candidate_tiers and c in candidate_tiers:
                    tier_str = candidate_tiers[c]

                snap = {
                    "candidate_id": int(c),
                    "seed": int(self.seed),
                    "step": int(step),
                    "episode_id": int(self.episode_id[c]),
                    "probe_count": int(n_val),
                    "truth_label": int(truth_label),
                    "mean_corr": float(m_val),
                    "abs_mean_corr": float(abs_m),
                    "variance_corr": float(var_c),
                    "std_corr": float(std_c),
                    "sign_consistency": float(sign_c),
                    "positive_fraction": float(pos_frac),
                    "negative_fraction": float(neg_frac),
                    "last_probe_gap": int(last_gap),
                    "mean_probe_gap": float(mean_gap),
                    "candidate_age": int(cand_age),
                    "time_since_first_probe": int(time_since_first),
                    "current_residual_abs": float(err_abs),
                    "current_residual_sq": float(err_sq),
                    "smoothed_residual": float(self.smoothed_residual_abs),
                    "smoothed_residual_sq": float(self.smoothed_residual_sq),
                    "candidate_tier": str(tier_str),
                    "candidate_state": "ACTIVE_CANDIDATE",
                    "current_active_support_recall": float(curr_recall),
                    "current_support_size": int(curr_k)
                }
                self.snapshots.append(snap)

    def get_dataframe(self) -> pd.DataFrame:
        df = pd.DataFrame(self.snapshots)
        if df.empty:
            return df
        return compute_diagnostic_scores(df)


def compute_diagnostic_scores(df: pd.DataFrame, eps: float = 1e-6) -> pd.DataFrame:
    """
    Computes all candidate diagnostic scores S0 to S5 and Oracle.
    """
    df = df.copy()
    abs_m = df["abs_mean_corr"]
    sign_c = df["sign_consistency"]
    std_c = df["std_corr"]
    sqrt_n = np.sqrt(df["probe_count"].astype(float))

    df["S0"] = abs_m
    df["S1"] = sign_c
    df["S2"] = abs_m * sign_c
    df["S3"] = abs_m / (std_c + eps)
    df["S4"] = sqrt_n * abs_m
    df["S5"] = sqrt_n * abs_m * sign_c
    df["Oracle"] = df["truth_label"].astype(float)

    # Existing EXP-0006 hint rule score indicator (warm entry criteria)
    # Warm hint required: n >= 2, |c| >= 0.15, sign_c >= 0.60
    df["S_current_rule"] = np.where(
        (df["abs_mean_corr"] >= 0.15) & (df["sign_consistency"] >= 0.60),
        df["abs_mean_corr"] * df["sign_consistency"],
        0.0
    )
    return df


def compute_distribution_stats(df: pd.DataFrame, feature: str) -> Dict[str, Any]:
    """
    Computes distribution statistics (mean, median, std, percentiles) for TRUE and NOISE separately,
    plus Cohen's d effect size and rank-biserial / AUC effect size.
    """
    true_vals = df[df["truth_label"] == 1][feature].values
    noise_vals = df[df["truth_label"] == 0][feature].values

    def get_stats(vals: np.ndarray) -> Dict[str, float]:
        if len(vals) == 0:
            return {
                "count": 0, "mean": 0.0, "median": 0.0, "std": 0.0,
                "p10": 0.0, "p25": 0.0, "p50": 0.0, "p75": 0.0,
                "p90": 0.0, "p95": 0.0, "p99": 0.0
            }
        return {
            "count": int(len(vals)),
            "mean": float(np.mean(vals)),
            "median": float(np.median(vals)),
            "std": float(np.std(vals, ddof=1)) if len(vals) > 1 else 0.0,
            "p10": float(np.percentile(vals, 10)),
            "p25": float(np.percentile(vals, 25)),
            "p50": float(np.percentile(vals, 50)),
            "p75": float(np.percentile(vals, 75)),
            "p90": float(np.percentile(vals, 90)),
            "p95": float(np.percentile(vals, 95)),
            "p99": float(np.percentile(vals, 99)),
        }

    t_stats = get_stats(true_vals)
    n_stats = get_stats(noise_vals)

    # Cohen's d
    if t_stats["count"] > 1 and n_stats["count"] > 1:
        s_pooled = math.sqrt(
            ((t_stats["count"] - 1) * (t_stats["std"] ** 2) + (n_stats["count"] - 1) * (n_stats["std"] ** 2))
            / (t_stats["count"] + n_stats["count"] - 2)
        )
        cohens_d = float((t_stats["mean"] - n_stats["mean"]) / s_pooled) if s_pooled > 1e-9 else 0.0
    else:
        cohens_d = 0.0

    # AUC & rank-biserial
    auc, _ = compute_roc_pr_auc(df["truth_label"].values, df[feature].values)
    rank_biserial = float(2.0 * auc - 1.0)

    return {
        "feature": feature,
        "true": t_stats,
        "noise": n_stats,
        "cohens_d": cohens_d,
        "auc": auc,
        "rank_biserial": rank_biserial
    }


def compute_roc_pr_auc(y_true: np.ndarray, y_score: np.ndarray) -> Tuple[float, float]:
    """
    Computes exact ROC-AUC and PR-AUC (Average Precision) without external dependencies.
    Handles ties deterministically.
    """
    y_true = np.asarray(y_true, dtype=int)
    y_score = np.asarray(y_score, dtype=float)

    n_pos = int(np.sum(y_true == 1))
    n_neg = int(np.sum(y_true == 0))

    if n_pos == 0 or n_neg == 0:
        return 0.5, 0.0

    # Sort by score descending
    order = np.argsort(-y_score, kind="mergesort")
    y_sorted = y_true[order]
    scores_sorted = y_score[order]

    # ROC-AUC via rank-sum with tied ranks
    distinct_indices = np.where(np.diff(scores_sorted))[0]
    threshold_indices = np.concatenate(([0], distinct_indices + 1, [len(scores_sorted)]))

    tps = np.cumsum(y_sorted == 1)
    fps = np.cumsum(y_sorted == 0)

    tps_distinct = tps[threshold_indices[1:] - 1]
    fps_distinct = fps[threshold_indices[1:] - 1]

    tpr = np.concatenate(([0.0], tps_distinct / float(n_pos)))
    fpr = np.concatenate(([0.0], fps_distinct / float(n_neg)))

    if hasattr(np, "trapezoid"):
        roc_auc = float(np.trapezoid(tpr, fpr))
    else:
        roc_auc = float(np.trapz(tpr, fpr))

    # PR-AUC: trapezoid / step integration of precision-recall
    rec = tpr
    prec = np.concatenate(([1.0], tps_distinct / np.maximum(1, (tps_distinct + fps_distinct))))
    # Average precision: sum over distinct points (rec_k - rec_{k-1}) * prec_k
    pr_auc = float(np.sum((rec[1:] - rec[:-1]) * prec[1:]))

    return roc_auc, pr_auc


def evaluate_precision_at_k(
    df: pd.DataFrame,
    score_col: str,
    k_values: Tuple[int, ...] = (1, 2, 3, 5, 10),
    post_shift_only: bool = True
) -> Dict[str, Any]:
    """
    Evaluates Precision@K, Recall@K, and Enrichment@K within each seed's candidate pool,
    and returns both the seed-level breakdown and aggregate means.
    """
    data = df[df["step"] > 1000] if post_shift_only else df
    seeds = sorted(data["seed"].unique())

    seed_precisions: Dict[int, Dict[int, float]] = {k: {} for k in k_values}
    seed_recalls: Dict[int, Dict[int, float]] = {k: {} for k in k_values}
    seed_enrichments: Dict[int, Dict[int, float]] = {k: {} for k in k_values}
    seed_base_rates: Dict[int, float] = {}

    for s in seeds:
        sub = data[data["seed"] == s]
        if sub.empty:
            continue
        n_true = int(np.sum(sub["truth_label"] == 1))
        n_total = len(sub)
        base_rate = float(n_true / n_total) if n_total > 0 else 0.0
        seed_base_rates[s] = base_rate

        # Sort by score descending (breaking ties randomly or with candidate_id)
        sub_sorted = sub.sort_values(by=[score_col, "candidate_id"], ascending=[False, True])
        labels = sub_sorted["truth_label"].values

        for k in k_values:
            top_k_labels = labels[:k]
            top_k_true = int(np.sum(top_k_labels == 1))
            prec = float(top_k_true / float(k))
            rec = float(top_k_true / float(n_true)) if n_true > 0 else 0.0
            enrich = float(prec / base_rate) if base_rate > 0 else 0.0

            seed_precisions[k][s] = prec
            seed_recalls[k][s] = rec
            seed_enrichments[k][s] = enrich

    mean_prec = {k: float(np.mean(list(seed_precisions[k].values()))) if seed_precisions[k] else 0.0 for k in k_values}
    mean_rec = {k: float(np.mean(list(seed_recalls[k].values()))) if seed_recalls[k] else 0.0 for k in k_values}
    mean_enrich = {k: float(np.mean(list(seed_enrichments[k].values()))) if seed_enrichments[k] else 0.0 for k in k_values}
    mean_base = float(np.mean(list(seed_base_rates.values()))) if seed_base_rates else 0.0

    return {
        "score": score_col,
        "mean_base_rate": mean_base,
        "precision_at_k": mean_prec,
        "recall_at_k": mean_rec,
        "enrichment_at_k": mean_enrich,
        "seed_precisions": seed_precisions,
        "seed_recalls": seed_recalls,
        "seed_enrichments": seed_enrichments,
        "seed_base_rates": seed_base_rates
    }


def evaluate_temporal_stratification(
    df: pd.DataFrame,
    scores: List[str],
    windows: Optional[Dict[str, Tuple[int, int]]] = None
) -> pd.DataFrame:
    """
    Evaluates candidate separability stratified by post-shift time windows:
    A: 0-20 steps (1000-1020)
    B: 21-50 steps (1021-1050)
    C: 51-100 steps (1051-1100)
    D: 101-250 steps (1101-1250)
    E: >250 steps (1251-2000)
    """
    if windows is None:
        windows = {
            "A (0-20)": (1000, 1020),
            "B (21-50)": (1021, 1050),
            "C (51-100)": (1051, 1100),
            "D (101-250)": (1101, 1250),
            "E (>250)": (1251, 2000)
        }

    rows = []
    for w_name, (t_start, t_end) in windows.items():
        w_df = df[(df["step"] >= t_start) & (df["step"] <= t_end)]
        n_true = int(np.sum(w_df["truth_label"] == 1))
        n_noise = int(np.sum(w_df["truth_label"] == 0))
        base_rate = float(n_true / len(w_df)) if len(w_df) > 0 else 0.0

        if n_true == 0 or len(w_df) == 0:
            rows.append({
                "window": w_name,
                "n_true": n_true,
                "n_noise": n_noise,
                "base_rate": base_rate,
                "best_score": "NONE",
                "best_precision_k3": 0.0,
                "best_precision_k5": 0.0,
                "best_pr_auc": 0.0,
                "false_positive_rate_k3": 0.0
            })
            continue

        best_score = "S0"
        best_p3 = -1.0
        best_p5 = -1.0
        best_pr = -1.0

        for sc in scores:
            res = evaluate_precision_at_k(w_df, sc, k_values=(3, 5), post_shift_only=False)
            p3 = res["precision_at_k"][3]
            p5 = res["precision_at_k"][5]
            _, pr_auc = compute_roc_pr_auc(w_df["truth_label"].values, w_df[sc].values)
            if p3 > best_p3 or (p3 == best_p3 and pr_auc > best_pr):
                best_p3 = p3
                best_p5 = p5
                best_pr = pr_auc
                best_score = sc

        fpr_k3 = 1.0 - best_p3
        rows.append({
            "window": w_name,
            "n_true": n_true,
            "n_noise": n_noise,
            "base_rate": base_rate,
            "best_score": best_score,
            "best_precision_k3": best_p3,
            "best_precision_k5": best_p5,
            "best_pr_auc": best_pr,
            "false_positive_rate_k3": fpr_k3
        })

    return pd.DataFrame(rows)


def evaluate_residual_stratification(
    df: pd.DataFrame,
    scores: List[str]
) -> pd.DataFrame:
    """
    Evaluates candidate separability stratified by quartiles Q1-Q4 of smoothed residual.
    """
    data = df[df["step"] > 1000].copy()
    if data.empty:
        return pd.DataFrame()

    q_labels = ["Q1", "Q2", "Q3", "Q4"]
    try:
        data["residual_quantile"] = pd.qcut(data["smoothed_residual"], q=4, labels=q_labels)
    except ValueError:
        data["residual_quantile"] = pd.cut(data["smoothed_residual"], bins=4, labels=q_labels)

    rows = []
    for q in q_labels:
        q_df = data[data["residual_quantile"] == q]
        n_true = int(np.sum(q_df["truth_label"] == 1))
        n_noise = int(np.sum(q_df["truth_label"] == 0))
        base_rate = float(n_true / len(q_df)) if len(q_df) > 0 else 0.0

        if n_true == 0 or len(q_df) == 0:
            rows.append({
                "residual_quantile": q,
                "n_true": n_true,
                "n_noise": n_noise,
                "base_rate": base_rate,
                "best_score": "NONE",
                "best_precision_k3": 0.0,
                "best_precision_k5": 0.0,
                "best_pr_auc": 0.0,
                "false_positive_rate_k3": 0.0
            })
            continue

        best_score = "S0"
        best_p3 = -1.0
        best_p5 = -1.0
        best_pr = -1.0

        for sc in scores:
            res = evaluate_precision_at_k(q_df, sc, k_values=(3, 5), post_shift_only=False)
            p3 = res["precision_at_k"][3]
            p5 = res["precision_at_k"][5]
            _, pr_auc = compute_roc_pr_auc(q_df["truth_label"].values, q_df[sc].values)
            if p3 > best_p3 or (p3 == best_p3 and pr_auc > best_pr):
                best_p3 = p3
                best_p5 = p5
                best_pr = pr_auc
                best_score = sc

        fpr_k3 = 1.0 - best_p3
        rows.append({
            "residual_quantile": q,
            "n_true": n_true,
            "n_noise": n_noise,
            "base_rate": base_rate,
            "best_score": best_score,
            "best_precision_k3": best_p3,
            "best_precision_k5": best_p5,
            "best_pr_auc": best_pr,
            "false_positive_rate_k3": fpr_k3
        })

    return pd.DataFrame(rows)


def evaluate_rank_stability(df: pd.DataFrame, score_col: str = "S2") -> pd.DataFrame:
    """
    Evaluates rank persistence and volatility for TRUE vs NOISE candidates across n = 1 -> 2 -> 3 -> 4 -> 5.
    Computes the rank change |rank_{n+1} - rank_n| across successive probe counts.
    """
    data = df[df["step"] > 1000].copy()
    rows = []

    # Filter to candidates that have snapshots at multiple n
    transitions = [(1, 2), (2, 3), (3, 4), (4, 5)]

    for n_curr, n_next in transitions:
        df_curr = data[data["probe_count"] == n_curr].copy()
        df_next = data[data["probe_count"] == n_next].copy()

        true_volatilities = []
        noise_volatilities = []

        for s in df_curr["seed"].unique():
            s_curr = df_curr[df_curr["seed"] == s].copy()
            s_next = df_next[df_next["seed"] == s].copy()

            s_curr["rank"] = s_curr[score_col].rank(ascending=False, method="average")
            s_next["rank"] = s_next[score_col].rank(ascending=False, method="average")

            merged = pd.merge(
                s_curr[["candidate_id", "truth_label", "rank"]],
                s_next[["candidate_id", "rank"]],
                on="candidate_id",
                suffixes=("_curr", "_next")
            )
            if merged.empty:
                continue

            merged["volatility"] = np.abs(merged["rank_curr"] - merged["rank_next"])
            t_vol = merged[merged["truth_label"] == 1]["volatility"].values
            n_vol = merged[merged["truth_label"] == 0]["volatility"].values

            true_volatilities.extend(t_vol)
            noise_volatilities.extend(n_vol)

        rows.append({
            "transition": f"n={n_curr}->{n_next}",
            "true_mean_volatility": float(np.mean(true_volatilities)) if len(true_volatilities) > 0 else 0.0,
            "true_median_volatility": float(np.median(true_volatilities)) if len(true_volatilities) > 0 else 0.0,
            "noise_mean_volatility": float(np.mean(noise_volatilities)) if len(noise_volatilities) > 0 else 0.0,
            "noise_median_volatility": float(np.median(noise_volatilities)) if len(noise_volatilities) > 0 else 0.0,
            "true_count": len(true_volatilities),
            "noise_count": len(noise_volatilities)
        })

    return pd.DataFrame(rows)


def evaluate_counterfactual_elevation(
    df: pd.DataFrame,
    scores: List[str],
    k_elevated: int = 5
) -> pd.DataFrame:
    """
    Offline counterfactual: If top-K candidates were elevated based on each diagnostic ranking,
    what fraction of elevated probe opportunities would go to TRUE omitted variables vs NOISE?
    """
    data = df[df["step"] > 1000].copy()
    rows = []

    for sc in scores:
        prec_res = evaluate_precision_at_k(data, sc, k_values=(k_elevated,), post_shift_only=True)
        useful_elev_prec = prec_res["precision_at_k"][k_elevated]
        false_elev_rate = 1.0 - useful_elev_prec
        enrichment = prec_res["enrichment_at_k"][k_elevated]

        # Estimated useful elevated probes out of observed J4 elevated probes (~2600 probes)
        # J4 elevated probes ~2688 probes across 2000 steps
        est_useful_probes = 2688.0 * useful_elev_prec
        est_wasted_probes = 2688.0 * false_elev_rate

        rows.append({
            "score": sc,
            "k_elevated": k_elevated,
            "useful_elevation_precision": float(useful_elev_prec),
            "false_elevation_rate": float(false_elev_rate),
            "enrichment_at_k": float(enrichment),
            "est_useful_elevated_probes": float(est_useful_probes),
            "est_wasted_elevated_probes": float(est_wasted_probes)
        })

    return pd.DataFrame(rows)


def evaluate_leave_one_seed_out_logistic(
    df: pd.DataFrame,
    feature_cols: Optional[List[str]] = None
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Fits a tiny logistic regression using leave-one-seed-out validation.
    Inputs: mean_corr, std_corr, sign_consistency, probe_count, smoothed_residual.
    Optimizes L2-regularized binary cross-entropy using scipy.optimize.minimize.
    """
    if feature_cols is None:
        feature_cols = ["abs_mean_corr", "std_corr", "sign_consistency", "probe_count", "smoothed_residual"]

    data = df[df["step"] > 1000].copy()
    seeds = sorted(data["seed"].unique())

    all_preds = []
    coef_list = []

    def sigmoid(z: np.ndarray) -> np.ndarray:
        return 1.0 / (1.0 + np.exp(-np.clip(z, -30.0, 30.0)))

    for test_seed in seeds:
        train_df = data[data["seed"] != test_seed]
        test_df = data[data["seed"] == test_seed]

        X_train_raw = train_df[feature_cols].values.astype(float)
        y_train = train_df["truth_label"].values.astype(float)

        X_test_raw = test_df[feature_cols].values.astype(float)
        y_test = test_df["truth_label"].values.astype(float)

        # Standardize using train mean and std
        means = np.mean(X_train_raw, axis=0)
        stds = np.std(X_train_raw, axis=0)
        stds[stds < 1e-6] = 1.0

        X_train = (X_train_raw - means) / stds
        X_test = (X_test_raw - means) / stds

        # Add bias column
        X_train_b = np.hstack([np.ones((len(X_train), 1)), X_train])
        X_test_b = np.hstack([np.ones((len(X_test), 1)), X_test])

        # Optimize logistic loss with L2 penalty (alpha = 1.0)
        alpha = 1.0
        def loss_and_grad(weights: np.ndarray) -> Tuple[float, np.ndarray]:
            p = sigmoid(X_train_b @ weights)
            loss = -np.mean(y_train * np.log(p + 1e-12) + (1.0 - y_train) * np.log(1.0 - p + 1e-12))
            loss += 0.5 * alpha * np.sum(weights[1:] ** 2)
            grad = (X_train_b.T @ (p - y_train)) / len(y_train)
            grad[1:] += alpha * weights[1:]
            return loss, grad

        w0 = np.zeros(X_train_b.shape[1])
        res = minimize(loss_and_grad, w0, method="L-BFGS-B", jac=True)
        w_opt = res.x
        coef_list.append(w_opt)

        test_probs = sigmoid(X_test_b @ w_opt)
        for idx, (_, row) in enumerate(test_df.iterrows()):
            all_preds.append({
                "candidate_id": row["candidate_id"],
                "seed": test_seed,
                "step": row["step"],
                "probe_count": row["probe_count"],
                "truth_label": row["truth_label"],
                "prob_logistic": float(test_probs[idx])
            })

    pred_df = pd.DataFrame(all_preds)
    roc_auc, pr_auc = compute_roc_pr_auc(pred_df["truth_label"].values, pred_df["prob_logistic"].values)
    prec_res = evaluate_precision_at_k(pred_df, "prob_logistic", k_values=(3, 5), post_shift_only=False)

    summary = {
        "roc_auc": float(roc_auc),
        "pr_auc": float(pr_auc),
        "precision_k3": float(prec_res["precision_at_k"][3]),
        "precision_k5": float(prec_res["precision_at_k"][5]),
        "mean_coefficients": np.mean(coef_list, axis=0).tolist(),
        "feature_cols": ["bias"] + feature_cols
    }
    return pred_df, summary
