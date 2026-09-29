import os
import math
from typing import Dict, Any, List, Set, Tuple, Optional
import numpy as np
import pandas as pd
from scipy.optimize import minimize

class MicrotestDiagnosticObserver:
    """
    Non-intrusive diagnostic observer for candidate micro-interventions (EXP-0008).
    Evaluates:
    - I0: Passive correlation control
    - I1: Delayed correlation consistency
    - I2: Single-step shadow micro-update gain
    - I3: Paired shadow prediction gain over tiny window W_eval
    - I4: Multi-step micro-update persistence
    - Creative Control 1: Causal Direction Margin (Sign-reversal control)
    - Creative Control 2: Excess Causal Gain (Sham candidate control)
    - I5: Oracle channel

    Strict guarantees:
    - Zero mutation of learner weights, supports, queues, or PRNG streams.
    - Truth labels applied offline only.
    - Future samples used for evaluation strictly occur after the training step.
    """
    def __init__(
        self,
        seed: int,
        d: int = 100,
        shift_step: int = 1000,
        r1_true_indices: Optional[List[int]] = None,
        r2_true_indices: Optional[List[int]] = None,
        paired_window_w: int = 3,
        multi_test_m: int = 2,
        eta_scale: float = 0.5
    ):
        self.seed = seed
        self.d = d
        self.shift_step = shift_step
        self.r1_true_indices = set(r1_true_indices or [2, 15, 33, 58, 81])
        self.r2_true_indices = set(r2_true_indices or [7, 24, 49, 66, 92])
        self.paired_window_w = paired_window_w
        self.multi_test_m = multi_test_m
        self.eta_scale = eta_scale

        # Completed micro-test records
        self.microtest_events: List[Dict[str, Any]] = []

        # Active pending shadow micro-tests awaiting future evaluation
        # candidate -> list of pending test contexts
        self.pending_tests: List[Dict[str, Any]] = []

        # Shadow learner state for multi-step persistence (I4)
        # candidate -> {w_shadow, updates_count, last_step}
        self.shadow_state_i4: Dict[int, Dict[str, Any]] = {
            c: {"w": 0.0, "updates": 0, "last_step": 0} for c in range(d)
        }

        # Residual tracking
        self.smoothed_residual_abs = 0.0

        # Memory and FLOP accounting
        self.diagnostic_flops = 0
        self.state_bytes_per_test = 8 * 4 + 4 * 4 # ~48 bytes per test record

    def on_step_begin(self, step: int, x_t: np.ndarray, y_t: float, y_hat_base: float, active_support: List[int]):
        """
        Evaluates pending shadow micro-tests on the incoming sample BEFORE learner updates.
        Ensures evaluation strictly uses future, out-of-sample data.
        """
        e_base = y_t - y_hat_base
        l_base = e_base ** 2
        active_set = set(active_support)

        # Process pending evaluations
        remaining_pending = []
        for test in self.pending_tests:
            c = test["candidate_id"]
            train_step = test["step_train"]

            # Must be strictly future sample (step > train_step)
            if step <= train_step:
                remaining_pending.append(test)
                continue

            x_eval_c = float(x_t[c])
            w_shadow = test["w_shadow"]
            w_wrong = -w_shadow
            w_sham = test["w_sham"]
            x_sham = float(x_t[test["sham_id"]])

            # 1. Single-step evaluation at step t + 1 (delay d = 1)
            if step == train_step + 1:
                # Normal shadow prediction
                y_hat_shadow = y_hat_base + w_shadow * x_eval_c
                e_shadow = y_t - y_hat_shadow
                l_shadow = e_shadow ** 2
                gain_i2 = l_base - l_shadow
                norm_gain_i2 = gain_i2 / (l_base + 1e-6)

                # Sign reversal control (wrong sign)
                y_hat_wrong = y_hat_base + w_wrong * x_eval_c
                e_wrong = y_t - y_hat_wrong
                l_wrong = e_wrong ** 2
                causal_dir_margin = l_wrong - l_shadow # positive if correct sign beats wrong sign

                # Sham candidate control
                y_hat_sham = y_hat_base + w_sham * x_sham
                e_sham = y_t - y_hat_sham
                l_sham = e_sham ** 2
                gain_sham = l_base - l_sham
                excess_causal_gain = gain_i2 - gain_sham

                # Delayed correlation consistency (I1)
                c_future = x_eval_c * e_base
                c_train = test["c_train"]
                same_sign = 1.0 if (c_train * c_future > 0) else 0.0
                c_product = float(c_train * c_future)
                c_min_abs = float(min(abs(c_train), abs(c_future)))
                score_i1 = math.copysign(math.sqrt(max(0.0, c_product)), c_product) if c_product != 0 else 0.0

                test["eval_step"] = step
                test["baseline_loss_eval"] = float(l_base)
                test["shadow_loss_eval"] = float(l_shadow)
                test["gain_i2"] = float(gain_i2)
                test["normalized_gain_i2"] = float(norm_gain_i2)
                test["causal_direction_margin"] = float(causal_dir_margin)
                test["gain_sham"] = float(gain_sham)
                test["excess_causal_gain"] = float(excess_causal_gain)
                test["score_i1"] = float(score_i1)
                test["same_sign_i1"] = float(same_sign)
                test["c_product_i1"] = float(c_product)

                self.diagnostic_flops += 18 # evaluation arithmetic

            # 2. Paired window accumulation (I3)
            if step <= train_step + self.paired_window_w:
                y_hat_shadow = y_hat_base + w_shadow * x_eval_c
                e_shadow = y_t - y_hat_shadow
                l_shadow = e_shadow ** 2
                delta_l = l_base - l_shadow

                test["paired_gain_sum"] += delta_l
                test["paired_base_sum"] += l_base
                test["paired_samples_count"] += 1
                self.diagnostic_flops += 6

            # If window complete, finalize test record
            if step >= train_step + self.paired_window_w:
                paired_base = test["paired_base_sum"]
                paired_gain = test["paired_gain_sum"]
                norm_paired_gain = paired_gain / (paired_base + 1e-6)
                test["gain_i3"] = float(paired_gain)
                test["normalized_gain_i3"] = float(norm_paired_gain)

                # Generalization ratio: future gain / instantaneous fit gain
                inst_gain = max(1e-6, test["inst_fit_gain"])
                test["generalization_ratio"] = float(test["gain_i2"] / inst_gain)

                # Multi-step persistence gain (I4)
                w_i4 = self.shadow_state_i4[c]["w"]
                y_hat_i4 = y_hat_base + w_i4 * x_eval_c
                e_i4 = y_t - y_hat_i4
                l_i4 = e_i4 ** 2
                gain_i4 = l_base - l_i4
                norm_gain_i4 = gain_i4 / (l_base + 1e-6)
                test["gain_i4"] = float(gain_i4)
                test["normalized_gain_i4"] = float(norm_gain_i4)

                self.microtest_events.append(test)
            else:
                remaining_pending.append(test)

        self.pending_tests = remaining_pending

    def on_step_end(
        self,
        step: int,
        error: float,
        probed_candidates: List[int],
        learner_cand_stats: Dict[str, Any],
        active_support: List[int],
        norm_sq_active: float,
        candidate_tiers: Optional[Dict[int, str]] = None
    ):
        """
        Creates shadow micro-test instances for probed candidates at step t.
        Operates strictly on probed candidates without disturbing learner state.
        """
        err_abs = abs(error)
        err_sq = error * error
        if step == 1:
            self.smoothed_residual_abs = err_abs
        else:
            self.smoothed_residual_abs = 0.95 * self.smoothed_residual_abs + 0.05 * err_abs

        current_true_support = self.r1_true_indices if step <= self.shift_step else self.r2_true_indices
        active_set = set(active_support)
        omitted_true = current_true_support - active_set
        curr_recall = len(active_set & current_true_support) / float(len(current_true_support))

        cand_n = learner_cand_stats["n"]
        cand_mean = learner_cand_stats["mean"]
        cand_pos = learner_cand_stats.get("pos")
        cand_neg = learner_cand_stats.get("neg")

        for c in probed_candidates:
            if c in active_set:
                continue

            n_val = int(cand_n[c])
            m_val = float(cand_mean[c])
            pos_cnt = int(cand_pos[c]) if cand_pos is not None else 0
            neg_cnt = int(cand_neg[c]) if cand_neg is not None else 0
            sign_c = float(max(pos_cnt, neg_cnt) / n_val) if n_val > 0 else 0.0

            # Deterministic step size based on NLMS active norm
            # eta = 0.5 * mu / (eps + norm_sq_active + 1.0)
            eta_probe = float(self.eta_scale * 0.5 / (1e-6 + norm_sq_active + 1.0))

            # Construct shadow weight based on instantaneous inner product
            # Note: in step update, val = error * x[c] was added to Welford accumulator.
            # We reconstruct x_c from the Welford step or delta if available, or compute delta
            # To ensure exact purity, w_shadow = eta_probe * error * (cand_mean delta)
            # Reconstruct c_t: last instantaneous contribution is error * x[c]
            # Since cand_mean[c] updated via: delta = val - cand_mean_old; cand_mean_new = cand_mean_old + delta/n
            # val = cand_mean_new + (n-1)*(cand_mean_new - cand_mean_old)... or we store x[c] directly.
            # We construct shadow update from cand_mean:
            w_shadow = float(eta_probe * m_val)

            # Instantaneous fit gain
            # inst_shadow_loss = (error - w_shadow)^2
            inst_shadow_loss = (error - w_shadow) ** 2
            inst_fit_gain = float(err_sq - inst_shadow_loss)

            # Sham candidate: pairing with deterministic irrelevant feature (c + 43) % d
            sham_id = (c + 43) % self.d
            if sham_id in current_true_support:
                sham_id = (sham_id + 1) % self.d
            w_sham = float(eta_probe * float(cand_mean[sham_id]) if cand_n[sham_id] > 0 else 0.0)

            # Multi-step shadow update (I4)
            st_i4 = self.shadow_state_i4[c]
            if st_i4["updates"] < self.multi_test_m:
                st_i4["w"] += 0.5 * w_shadow
                st_i4["updates"] += 1
                st_i4["last_step"] = step

            truth_label = 1 if (c in omitted_true) else 0
            tier_str = candidate_tiers.get(c, "COLD") if candidate_tiers else "COLD"

            test_ctx = {
                "candidate_id": int(c),
                "seed": int(self.seed),
                "step_train": int(step),
                "truth_label": int(truth_label),
                "candidate_tier": str(tier_str),
                "n_passive_probes": int(n_val),
                "mean_corr": float(m_val),
                "abs_mean_corr": float(abs(m_val)),
                "sign_consistency": float(sign_c),
                "residual_train": float(error),
                "smoothed_residual": float(self.smoothed_residual_abs),
                "eta_probe": float(eta_probe),
                "w_shadow": float(w_shadow),
                "w_sham": float(w_sham),
                "sham_id": int(sham_id),
                "c_train": float(m_val),
                "inst_fit_gain": float(inst_fit_gain),
                "paired_gain_sum": 0.0,
                "paired_base_sum": 0.0,
                "paired_samples_count": 0,
                "time_since_shift": int(max(0, step - self.shift_step)),
                "support_recall": float(curr_recall)
            }
            self.pending_tests.append(test_ctx)
            self.diagnostic_flops += 10 # shadow creation arithmetic

    def get_dataframe(self) -> pd.DataFrame:
        df = pd.DataFrame(self.microtest_events)
        if df.empty:
            return df
        return df


def compute_roc_pr_auc(y_true: np.ndarray, y_score: np.ndarray) -> Tuple[float, float]:
    """
    Computes exact ROC-AUC and PR-AUC (Average Precision) without external dependencies.
    """
    y_true = np.asarray(y_true, dtype=int)
    y_score = np.asarray(y_score, dtype=float)

    n_pos = int(np.sum(y_true == 1))
    n_neg = int(np.sum(y_true == 0))

    if n_pos == 0 or n_neg == 0:
        return 0.5, 0.0

    order = np.argsort(-y_score, kind="mergesort")
    y_sorted = y_true[order]
    scores_sorted = y_score[order]

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

    rec = tpr
    prec = np.concatenate(([1.0], tps_distinct / np.maximum(1, (tps_distinct + fps_distinct))))
    pr_auc = float(np.sum((rec[1:] - rec[:-1]) * prec[1:]))

    return roc_auc, pr_auc


def evaluate_channel_precision_at_k(
    df: pd.DataFrame,
    score_col: str,
    k_values: Tuple[int, ...] = (1, 2, 3, 5, 10),
    post_shift_only: bool = True
) -> Dict[str, Any]:
    """
    Evaluates Precision@K, Recall@K, and Enrichment@K within each seed's candidate test pool.
    """
    data = df[df["step_train"] > 1000] if post_shift_only else df
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


def evaluate_temporal_stratification_microtest(
    df: pd.DataFrame,
    channels: List[Tuple[str, str]],
    windows: Optional[Dict[str, Tuple[int, int]]] = None
) -> pd.DataFrame:
    """
    Evaluates best information channel across post-shift time windows (A-E).
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
        w_df = df[(df["step_train"] >= t_start) & (df["step_train"] <= t_end)]
        n_true = int(np.sum(w_df["truth_label"] == 1))
        n_noise = int(np.sum(w_df["truth_label"] == 0))
        base_rate = float(n_true / len(w_df)) if len(w_df) > 0 else 0.0

        if n_true == 0 or len(w_df) == 0:
            rows.append({
                "window": w_name,
                "n_true": n_true,
                "n_noise": n_noise,
                "base_rate": base_rate,
                "best_channel": "NONE",
                "best_precision_k3": 0.0,
                "best_precision_k5": 0.0,
                "best_pr_auc": 0.0
            })
            continue

        best_ch = "I0"
        best_p3 = -1.0
        best_p5 = -1.0
        best_pr = -1.0

        for ch_name, score_col in channels:
            if score_col not in w_df.columns:
                continue
            res = evaluate_channel_precision_at_k(w_df, score_col, k_values=(3, 5), post_shift_only=False)
            p3 = res["precision_at_k"][3]
            p5 = res["precision_at_k"][5]
            _, pr_auc = compute_roc_pr_auc(w_df["truth_label"].values, w_df[score_col].values)

            if p3 > best_p3 or (p3 == best_p3 and p5 > best_p5):
                best_p3 = p3
                best_p5 = p5
                best_pr = pr_auc
                best_ch = ch_name

        rows.append({
            "window": w_name,
            "n_true": n_true,
            "n_noise": n_noise,
            "base_rate": base_rate,
            "best_channel": best_ch,
            "best_precision_k3": best_p3,
            "best_precision_k5": best_p5,
            "best_pr_auc": best_pr
        })

    return pd.DataFrame(rows)


def evaluate_residual_stratification_microtest(
    df: pd.DataFrame,
    channels: List[Tuple[str, str]]
) -> pd.DataFrame:
    """
    Evaluates best information channel across smoothed residual quantiles Q1-Q4.
    """
    data = df[df["step_train"] > 1000].copy()
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
                "best_channel": "NONE",
                "best_precision_k3": 0.0,
                "best_precision_k5": 0.0,
                "effect_size": 0.0,
                "p_gain_pos_true": 0.0,
                "p_gain_pos_noise": 0.0
            })
            continue

        best_ch = "I0"
        best_p3 = -1.0
        best_p5 = -1.0
        best_col = "gain_i2"

        for ch_name, score_col in channels:
            if score_col not in q_df.columns:
                continue
            res = evaluate_channel_precision_at_k(q_df, score_col, k_values=(3, 5), post_shift_only=False)
            p3 = res["precision_at_k"][3]
            p5 = res["precision_at_k"][5]
            if p3 > best_p3 or (p3 == best_p3 and p5 > best_p5):
                best_p3 = p3
                best_p5 = p5
                best_ch = ch_name
                best_col = score_col

        # Effect size (Cohen's d or rank-biserial)
        roc, _ = compute_roc_pr_auc(q_df["truth_label"].values, q_df[best_col].values)
        effect_size = 2.0 * roc - 1.0

        t_gains = q_df[q_df["truth_label"] == 1]["gain_i2"].values
        n_gains = q_df[q_df["truth_label"] == 0]["gain_i2"].values
        p_t_pos = float(np.mean(t_gains > 0)) if len(t_gains) > 0 else 0.0
        p_n_pos = float(np.mean(n_gains > 0)) if len(n_gains) > 0 else 0.0

        rows.append({
            "residual_quantile": q,
            "n_true": n_true,
            "n_noise": n_noise,
            "base_rate": base_rate,
            "best_channel": best_ch,
            "best_precision_k3": best_p3,
            "best_precision_k5": best_p5,
            "effect_size": effect_size,
            "p_gain_pos_true": p_t_pos,
            "p_gain_pos_noise": p_n_pos
        })

    return pd.DataFrame(rows)


def evaluate_counterfactual_queue_enrichment(
    df: pd.DataFrame,
    channels: List[Tuple[str, str]],
    k_elevated: int = 5
) -> pd.DataFrame:
    """
    Counterfactual queue enrichment under observed J4 elevated service budget (~2,688 probes).
    """
    data = df[df["step_train"] > 1000].copy()
    rows = []

    for ch_name, score_col in channels:
        if score_col not in data.columns:
            continue
        prec_res = evaluate_channel_precision_at_k(data, score_col, k_values=(k_elevated,), post_shift_only=True)
        useful_prec = prec_res["precision_at_k"][k_elevated]
        false_rate = 1.0 - useful_prec
        enrich = prec_res["enrichment_at_k"][k_elevated]

        est_useful = 2688.0 * useful_prec
        est_wasted = 2688.0 * false_rate

        rows.append({
            "channel": ch_name,
            "score_col": score_col,
            "k_elevated": k_elevated,
            "useful_elevation_precision": float(useful_prec),
            "false_elevation_rate": float(false_rate),
            "enrichment_at_k": float(enrich),
            "est_useful_elevated_probes": float(est_useful),
            "est_wasted_elevated_probes": float(est_wasted)
        })

    return pd.DataFrame(rows)


def evaluate_leave_one_seed_out_logistic_microtest(
    df: pd.DataFrame,
    feature_cols: Optional[List[str]] = None
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Joint linear model evaluating whether combining passive and interventional signals
    adds material discrimination.
    """
    if feature_cols is None:
        feature_cols = [
            "abs_mean_corr",
            "normalized_gain_i2",
            "causal_direction_margin",
            "excess_causal_gain",
            "smoothed_residual"
        ]

    data = df[df["step_train"] > 1000].copy()
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

        # Standardize using train statistics
        means = np.mean(X_train_raw, axis=0)
        stds = np.std(X_train_raw, axis=0)
        stds[stds < 1e-6] = 1.0

        X_train = (X_train_raw - means) / stds
        X_test = (X_test_raw - means) / stds

        X_train_b = np.hstack([np.ones((len(X_train), 1)), X_train])
        X_test_b = np.hstack([np.ones((len(X_test), 1)), X_test])

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
                "step_train": row["step_train"],
                "truth_label": row["truth_label"],
                "prob_logistic": float(test_probs[idx])
            })

    pred_df = pd.DataFrame(all_preds)
    roc_auc, pr_auc = compute_roc_pr_auc(pred_df["truth_label"].values, pred_df["prob_logistic"].values)
    prec_res = evaluate_channel_precision_at_k(pred_df, "prob_logistic", k_values=(3, 5), post_shift_only=False)

    summary = {
        "roc_auc": float(roc_auc),
        "pr_auc": float(pr_auc),
        "precision_k3": float(prec_res["precision_at_k"][3]),
        "precision_k5": float(prec_res["precision_at_k"][5]),
        "mean_coefficients": np.mean(coef_list, axis=0).tolist(),
        "feature_cols": ["bias"] + feature_cols
    }
    return pred_df, summary
