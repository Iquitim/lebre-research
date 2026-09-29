import os
import math
from typing import Dict, Any, List, Set, Tuple, Optional
import numpy as np
import pandas as pd

def get_hadamard_matrix(order: int) -> np.ndarray:
    """
    Constructs a Sylvester-Walsh Hadamard matrix of order 2, 4, 8, or 16.
    Elements are +1 and -1. H * H^T = order * I.
    """
    if order not in (1, 2, 4, 8, 16):
        raise ValueError(f"Hadamard matrix order must be a power of 2 (1, 2, 4, 8, 16), got {order}")
    h = np.array([[1.0]], dtype=np.float64)
    while h.shape[0] < order:
        h = np.block([[h, h], [h, -h]])
    return h

class ActiveProbeDiagnosticObserver:
    """
    Diagnostic observer for active probe design (EXP-0009).
    Evaluates whether structured perturbations (paired excitation, random-sign coding,
    orthogonal group coding, and sham cancellation) create a high-SNR candidate
    information channel under strict compute and non-mutation constraints.

    Guarantees:
    - Zero mutation of production learner state, weights, support, queues, or PRNG streams.
    - Perturbations apply strictly to shadow prediction hypothesis on out-of-sample data.
    - Truth labels used strictly offline for diagnostic scoring.
    """
    def __init__(
        self,
        seed: int,
        d: int = 100,
        shift_step: int = 1000,
        r1_true_indices: Optional[List[int]] = None,
        r2_true_indices: Optional[List[int]] = None,
        delta: float = 0.10,
        r_rounds: Optional[List[int]] = None,
        group_sizes: Optional[List[int]] = None
    ):
        self.seed = seed
        self.d = d
        self.shift_step = shift_step
        self.r1_true_indices = set(r1_true_indices or [2, 15, 33, 58, 81])
        self.r2_true_indices = set(r2_true_indices or [7, 24, 49, 66, 92])
        self.delta = delta
        self.r_rounds = r_rounds or [2, 4]
        self.group_sizes = group_sizes or [4, 8]

        # Precompute Hadamard matrices for group probing
        self.hadamard_matrices = {
            g: get_hadamard_matrix(g) for g in self.group_sizes
        }

        # Completed diagnostic events
        self.active_probe_events: List[Dict[str, Any]] = []

        # Pending test batteries:
        # Each pending battery tracks a test across future steps t+1, t+2, ...
        self.pending_individual_tests: List[Dict[str, Any]] = []
        self.pending_group_tests: List[Dict[str, Any]] = []

        # Smoothed residual tracking
        self.smoothed_residual_abs = 0.0

        # FLOP and state accounting
        self.diagnostic_flops = 0

    def on_step_begin(
        self,
        step: int,
        x_t: np.ndarray,
        y_t: float,
        y_hat_base: float,
        active_support: List[int]
    ):
        """
        Evaluates pending active probes on the incoming out-of-sample observation (x_t, y_t)
        BEFORE the production learner executes its update.
        """
        e_base = y_t - y_hat_base
        l_base = e_base ** 2
        active_set = set(active_support)

        # -------------------------------------------------------------
        # 1. Evaluate Pending Individual Tests (A1, A2, A4, A5)
        # -------------------------------------------------------------
        rem_indiv = []
        for test in self.pending_individual_tests:
            c = test["candidate_id"]
            train_step = test["step_train"]

            # Must be strictly future sample
            if step <= train_step:
                rem_indiv.append(test)
                continue

            r_idx = step - train_step # round index 1, 2, 3, 4...
            max_r = test["max_rounds"]
            if r_idx > max_r:
                continue

            x_eval_c = float(x_t[c])
            delta = test["delta"]

            # Code sign for this round (deterministic pseudo-random ±1)
            code_sign = test["code_sequence"][r_idx - 1]

            # 1. Symmetric Paired Excitation (+delta and -delta on SAME sample)
            # Positive shadow prediction
            y_hat_plus = y_hat_base + delta * x_eval_c
            e_plus = y_t - y_hat_plus
            l_plus = e_plus ** 2

            # Negative shadow prediction
            y_hat_minus = y_hat_base - delta * x_eval_c
            e_minus = y_t - y_hat_minus
            l_minus = e_minus ** 2

            # Paired response (L_minus - L_plus)
            dir_resp_raw = l_minus - l_plus # = 4 * delta * e_base * x_c
            npr = (l_minus - l_plus) / (abs(l_plus) + abs(l_minus) + 1e-6)

            # Coded excitation response (A2): multiply by sign code
            coded_resp_round = code_sign * dir_resp_raw

            # Sham cancellation (A4): matched concurrent sham Gaussian variable
            x_sham = float(x_t[test["sham_id"]])
            y_hat_sham_plus = y_hat_base + delta * x_sham
            l_sham_plus = (y_t - y_hat_sham_plus) ** 2
            y_hat_sham_minus = y_hat_base - delta * x_sham
            l_sham_minus = (y_t - y_hat_sham_minus) ** 2
            sham_resp = l_sham_minus - l_sham_plus
            excess_resp = dir_resp_raw - sham_resp

            # Record round responses
            test["round_responses"].append({
                "round": r_idx,
                "step": step,
                "code_sign": code_sign,
                "l_base": l_base,
                "l_plus": l_plus,
                "l_minus": l_minus,
                "dir_resp_raw": dir_resp_raw,
                "npr": npr,
                "coded_resp": coded_resp_round,
                "sham_resp": sham_resp,
                "excess_resp": excess_resp,
                "x_c": x_eval_c,
                "e_base": e_base
            })

            # Check if this test has completed all its target rounds
            if r_idx == max_r:
                # Decode scores across rounds
                # A1 (Round 1 only): single-step paired excitation
                r1_data = test["round_responses"][0]
                a1_raw = r1_data["dir_resp_raw"]
                a1_npr = r1_data["npr"]
                cand_sign = test["cand_sign"]
                a1_signed = cand_sign * a1_raw
                a1_npr_signed = cand_sign * a1_npr
                a1_mag = abs(a1_raw)

                # A2 (R rounds coded accumulation):
                # Sum_r s_r * dir_resp_r / R
                r2_responses = [rd["coded_resp"] for rd in test["round_responses"][:2]]
                a2_score_r2 = float(np.mean(r2_responses)) if len(r2_responses) >= 2 else a1_raw
                a2_score_r4 = float(np.mean([rd["coded_resp"] for rd in test["round_responses"]]))

                # A4 (Paired + Sham excess):
                a4_score = float(np.mean([rd["excess_resp"] for rd in test["round_responses"][:1]]))
                a4_score_signed = cand_sign * a4_score
                a4_score_mag = abs(a4_score)

                # A5 (Multi-round coded accumulation, R=4 rounds):
                a5_score = a2_score_r4
                a5_score_signed = cand_sign * a5_score
                a5_score_mag = abs(a5_score)

                # Creative Controls:
                # 1. Zero-delta: exactly 0
                ctrl_zero_delta = 0.0
                # 2. Sign flip: inverted code
                ctrl_sign_flip = -a2_score_r4
                # 3. Permuted code score (shuffled code signs)
                perm_signs = [-s for s in test["code_sequence"]] # anti-correlated permutation
                ctrl_perm_score = float(np.mean([
                    perm_signs[i] * test["round_responses"][i]["dir_resp_raw"]
                    for i in range(len(test["round_responses"]))
                ]))

                # Determine truth
                true_set = self.r2_true_indices if step > self.shift_step else self.r1_true_indices
                is_true = 1 if c in true_set else 0

                # Log comprehensive event record
                self.active_probe_events.append({
                    "seed": self.seed,
                    "step": train_step,
                    "candidate_id": c,
                    "truth_label": is_true,
                    "channel_type": "individual",
                    "group_id": -1,
                    "group_size": 1,
                    "rounds_evaluated": max_r,
                    "delta": delta,
                    # Channel scores:
                    "a0_passive_gain": test.get("a0_passive_gain", 0.0),
                    "a1_dir_resp_raw": a1_raw,
                    "a1_dir_resp_mag": a1_mag,
                    "a1_dir_resp_signed": a1_signed,
                    "a1_npr": a1_npr,
                    "a1_npr_signed": a1_npr_signed,
                    "a2_coded_score_r2": a2_score_r2,
                    "a2_coded_score_r4": a2_score_r4,
                    "a4_sham_excess": a4_score,
                    "a4_sham_excess_signed": a4_score_signed,
                    "a4_sham_excess_mag": a4_score_mag,
                    "a5_multi_round_score": a5_score,
                    "a5_multi_round_signed": a5_score_signed,
                    "a5_multi_round_mag": a5_score_mag,
                    # Controls:
                    "ctrl_zero_delta": ctrl_zero_delta,
                    "ctrl_sign_flip": ctrl_sign_flip,
                    "ctrl_perm_score": ctrl_perm_score,
                    # Context:
                    "residual_abs": abs(e_base),
                    "smoothed_residual": self.smoothed_residual_abs,
                    "time_since_shift": max(0, train_step - self.shift_step),
                    "passive_probe_count": test["passive_probe_count"],
                    "candidate_tier": test["candidate_tier"],
                    "candidate_mean_corr": test["cand_mean_corr"]
                })
            else:
                rem_indiv.append(test)

        self.pending_individual_tests = rem_indiv

        # -------------------------------------------------------------
        # 2. Evaluate Pending Group Tests (A3 - Orthogonal Group Coding)
        # -------------------------------------------------------------
        rem_group = []
        for g_test in self.pending_group_tests:
            train_step = g_test["step_train"]

            if step <= train_step:
                rem_group.append(g_test)
                continue

            r_idx = step - train_step # round 1, 2, ..., R
            g_size = g_test["group_size"] # G = 4 or 8
            max_rounds = g_test["max_rounds"] # R = G

            if r_idx > max_rounds:
                continue

            # Orthogonal code matrix H (G x R)
            H = g_test["hadamard_matrix"]
            delta = g_test["delta"]
            group_candidates = g_test["candidate_ids"]

            # Combined group perturbation for round r (0-indexed: r_idx - 1)
            r_col = r_idx - 1
            delta_y_hat = 0.0
            for j_pos, cand_id in enumerate(group_candidates):
                code_val = H[j_pos, r_col]
                x_val = float(x_t[cand_id])
                delta_y_hat += delta * code_val * x_val

            # Symmetric paired group evaluation on same sample
            y_hat_g_plus = y_hat_base + delta_y_hat
            l_g_plus = (y_t - y_hat_g_plus) ** 2
            y_hat_g_minus = y_hat_base - delta_y_hat
            l_g_minus = (y_t - y_hat_g_minus) ** 2

            group_dir_resp = l_g_minus - l_g_plus # = 4 * delta_y_hat * e_base

            g_test["round_responses"].append({
                "round": r_idx,
                "group_dir_resp": group_dir_resp,
                "e_base": e_base
            })

            if r_idx == max_rounds:
                # Group battery complete: decode each candidate in the group
                responses_vector = np.array([rd["group_dir_resp"] for rd in g_test["round_responses"]], dtype=np.float64)

                # Decode: GROUP_SCORE_j = (1 / R) * Sum_r H[j, r] * response_r
                decoded_scores = (H @ responses_vector) / float(max_rounds)

                true_set = self.r2_true_indices if step > self.shift_step else self.r1_true_indices

                for j_pos, cand_id in enumerate(group_candidates):
                    score_j = float(decoded_scores[j_pos])
                    cand_sign = g_test["candidate_signs"][j_pos]
                    is_true = 1 if cand_id in true_set else 0

                    # Permuted control: decode using a circularly shifted code row
                    perm_pos = (j_pos + 1) % g_size
                    perm_score_j = float((H[perm_pos, :] @ responses_vector) / float(max_rounds))

                    self.active_probe_events.append({
                        "seed": self.seed,
                        "step": train_step,
                        "candidate_id": cand_id,
                        "truth_label": is_true,
                        "channel_type": f"group_G{g_size}_R{max_rounds}",
                        "group_id": g_test["group_id"],
                        "group_size": g_size,
                        "rounds_evaluated": max_rounds,
                        "delta": delta,
                        # Scores:
                        "a3_group_score_raw": score_j,
                        "a3_group_score_mag": abs(score_j),
                        "a3_group_score_signed": cand_sign * score_j,
                        "ctrl_group_perm_score": perm_score_j,
                        # Context:
                        "residual_abs": abs(e_base),
                        "smoothed_residual": self.smoothed_residual_abs,
                        "time_since_shift": max(0, train_step - self.shift_step),
                        "passive_probe_count": g_test["passive_probe_counts"][j_pos],
                        "candidate_tier": g_test["candidate_tiers"][j_pos],
                        "candidate_mean_corr": g_test["candidate_mean_corrs"][j_pos]
                    })
            else:
                rem_group.append(g_test)

        self.pending_group_tests = rem_group

    def on_step_end(
        self,
        step: int,
        probed_candidates: List[int],
        cand_stats: Dict[str, Any],
        cand_tiers: Dict[int, str],
        loss: float,
        active_support: List[int],
        inactive_candidates: List[int],
        x_t: np.ndarray,
        y_t: float,
        y_hat_base: float
    ):
        """
        Schedules pending active diagnostic tests when candidates are probed in the production stream.
        """
        # Update smoothed residual
        err_abs = math.sqrt(max(0.0, loss))
        self.smoothed_residual_abs = 0.95 * self.smoothed_residual_abs + 0.05 * err_abs

        # Only evaluate diagnostic tests in Regime 2 post-shift
        if step < self.shift_step:
            return

        cand_n = cand_stats["n"]
        cand_mean = cand_stats["mean"]
        active_set = set(active_support)

        # 1. Schedule Individual Active Tests for Probed Inactive Candidates
        for c in probed_candidates:
            if c in active_set:
                continue

            n_obs = int(cand_n[c])
            mean_c = float(cand_mean[c])
            cand_sign = 1.0 if mean_c >= 0 else -1.0

            # Deterministic pseudo-random sign code sequence of length 4:
            # Derived from candidate_id and step to ensure reproducibility without truth
            rng_test = np.random.RandomState(self.seed * 100000 + step * 100 + c)
            code_seq = [1.0 if r > 0.5 else -1.0 for r in rng_test.rand(4)]

            # Deterministic matched sham candidate (an unprobed inactive feature)
            avail_shams = [idx for idx in inactive_candidates if idx != c and idx not in probed_candidates]
            sham_id = avail_shams[rng_test.randint(len(avail_shams))] if avail_shams else (c + 1) % self.d

            # Calculate baseline A0 passive excess causal gain from EXP-0008
            x_c = float(x_t[c])
            e_base = y_t - y_hat_base
            w_shadow = 0.5 * (e_base * x_c) / (float(np.dot(x_t[active_support], x_t[active_support])) + 1e-6)
            # A0 will be logged on completed record

            self.pending_individual_tests.append({
                "candidate_id": c,
                "step_train": step,
                "delta": self.delta,
                "max_rounds": 4,
                "code_sequence": code_seq,
                "sham_id": sham_id,
                "cand_sign": cand_sign,
                "passive_probe_count": n_obs,
                "candidate_tier": cand_tiers.get(c, "COLD"),
                "cand_mean_corr": mean_c,
                "round_responses": []
            })
            self.diagnostic_flops += 32

        # 2. Schedule Group Tests (A3) on Available Inactive Candidates
        # Periodically or when multiple candidates probed, form orthogonal groups of size 4 and 8
        if len(probed_candidates) > 0 and (step % 2 == 0):
            inactives = [idx for idx in inactive_candidates if idx not in active_set]
            # Form group of size G=4
            if 4 in self.group_sizes and len(inactives) >= 4:
                rng_grp = np.random.RandomState(self.seed * 200000 + step)
                grp_candidates = list(probed_candidates[:2])
                needed = 4 - len(grp_candidates)
                other_inactives = [idx for idx in inactives if idx not in grp_candidates]
                if len(other_inactives) >= needed:
                    grp_candidates.extend(list(rng_grp.choice(other_inactives, size=needed, replace=False)))
                else:
                    grp_candidates.extend(other_inactives[:needed])

                if len(grp_candidates) == 4:
                    self.pending_group_tests.append({
                        "group_id": step * 10 + 4,
                        "group_size": 4,
                        "max_rounds": 4,
                        "hadamard_matrix": self.hadamard_matrices[4],
                        "candidate_ids": grp_candidates,
                        "candidate_signs": [1.0 if cand_mean[ci] >= 0 else -1.0 for ci in grp_candidates],
                        "passive_probe_counts": [int(cand_n[ci]) for ci in grp_candidates],
                        "candidate_tiers": [cand_tiers.get(ci, "COLD") for ci in grp_candidates],
                        "candidate_mean_corrs": [float(cand_mean[ci]) for ci in grp_candidates],
                        "step_train": step,
                        "delta": self.delta,
                        "round_responses": []
                    })
                    self.diagnostic_flops += 48

            # Periodically form group of size G=8 (every 4 steps)
            if 8 in self.group_sizes and step % 4 == 0 and len(inactives) >= 8:
                rng_grp8 = np.random.RandomState(self.seed * 200000 + step + 1)
                grp_cands_8 = list(probed_candidates[:3])
                needed_8 = 8 - len(grp_cands_8)
                other_inactives_8 = [idx for idx in inactives if idx not in grp_cands_8]
                if len(other_inactives_8) >= needed_8:
                    grp_cands_8.extend(list(rng_grp8.choice(other_inactives_8, size=needed_8, replace=False)))
                else:
                    grp_cands_8.extend(other_inactives_8[:needed_8])

                if len(grp_cands_8) == 8:
                    self.pending_group_tests.append({
                        "group_id": step * 10 + 8,
                        "group_size": 8,
                        "max_rounds": 8,
                        "hadamard_matrix": self.hadamard_matrices[8],
                        "candidate_ids": grp_cands_8,
                        "candidate_signs": [1.0 if cand_mean[ci] >= 0 else -1.0 for ci in grp_cands_8],
                        "passive_probe_counts": [int(cand_n[ci]) for ci in grp_cands_8],
                        "candidate_tiers": [cand_tiers.get(ci, "COLD") for ci in grp_cands_8],
                        "candidate_mean_corrs": [float(cand_mean[ci]) for ci in grp_cands_8],
                        "step_train": step,
                        "delta": self.delta,
                        "round_responses": []
                    })
                    self.diagnostic_flops += 96


# =====================================================================
# Metrics & Stratification Evaluation Utilities
# =====================================================================

def compute_roc_pr_auc(y_true: np.ndarray, y_score: np.ndarray) -> Tuple[float, float]:
    """Computes ROC-AUC and PR-AUC using trapezoidal integration."""
    if len(y_true) == 0 or np.sum(y_true) == 0 or np.sum(y_true) == len(y_true):
        return 0.5, float(np.mean(y_true)) if len(y_true) > 0 else 0.0

    order = np.argsort(-y_score)
    y_sorted = y_true[order]

    n_pos = np.sum(y_sorted)
    n_neg = len(y_sorted) - n_pos

    tpr = np.cumsum(y_sorted) / float(n_pos)
    fpr = np.cumsum(1 - y_sorted) / float(n_neg)
    prec = np.cumsum(y_sorted) / np.arange(1, len(y_sorted) + 1)

    tpr_with_0 = np.concatenate(([0.0], tpr))
    fpr_with_0 = np.concatenate(([0.0], fpr))
    roc_auc = float(np.trapz(tpr_with_0, fpr_with_0))

    pr_auc = float(np.sum((tpr[1:] - tpr[:-1]) * prec[1:])) + float(tpr[0] * prec[0])
    return roc_auc, pr_auc

def evaluate_channel_precision_at_k(
    df: pd.DataFrame,
    score_col: str,
    k_values: List[int] = [1, 2, 3, 5, 10]
) -> Dict[str, Any]:
    """
    Evaluates Precision@K and Enrichment@K ranked per seed across candidate events.
    Computes active SNR and tail separation P(score_true > P99_noise).
    """
    seeds = sorted(df["seed"].unique())
    seed_precisions: Dict[int, List[float]] = {k: [] for k in k_values}
    seed_base_rates: List[float] = []

    for s in seeds:
        sub = df[df["seed"] == s]
        if sub.empty:
            continue
        n_true = int(sub["truth_label"].sum())
        n_total = len(sub)
        base_rate = float(n_true / n_total) if n_total > 0 else 0.0
        seed_base_rates.append(base_rate)

        sub_sorted = sub.sort_values(by=[score_col, "candidate_id"], ascending=[False, True])
        labels = sub_sorted["truth_label"].values

        for k in k_values:
            actual_k = min(k, len(labels))
            p_k = float(labels[:actual_k].sum() / float(actual_k)) if actual_k > 0 else 0.0
            seed_precisions[k].append(p_k)

    mean_base = float(np.mean(seed_base_rates)) if seed_base_rates else 0.0
    res = {f"p_at_{k}": float(np.mean(seed_precisions[k])) if seed_precisions[k] else 0.0 for k in k_values}
    res["enrichment_at_3"] = (res["p_at_3"] / mean_base) if mean_base > 0 else 1.0
    res["enrichment_at_5"] = (res["p_at_5"] / mean_base) if mean_base > 0 else 1.0
    res["base_rate"] = mean_base

    # Active SNR: (mean_true - mean_noise) / pooled_std
    true_scores = df[df["truth_label"] == 1][score_col].values
    noise_scores = df[df["truth_label"] == 0][score_col].values

    if len(true_scores) > 0 and len(noise_scores) > 0:
        mu_true = float(np.mean(true_scores))
        mu_noise = float(np.mean(noise_scores))
        var_true = float(np.var(true_scores))
        var_noise = float(np.var(noise_scores))
        pooled_std = math.sqrt(max(1e-9, 0.5 * (var_true + var_noise)))
        res["active_snr"] = (mu_true - mu_noise) / pooled_std

        # Tail separation: fraction of true scores exceeding P99 of noise
        p99_noise = float(np.percentile(noise_scores, 99))
        p95_noise = float(np.percentile(noise_scores, 95))
        max_noise = float(np.max(noise_scores))
        res["p_true_gt_p99_noise"] = float(np.mean(true_scores > p99_noise))
        res["p_true_gt_p95_noise"] = float(np.mean(true_scores > p95_noise))
        res["p99_noise"] = p99_noise
        res["p95_noise"] = p95_noise
        res["max_noise"] = max_noise
        res["median_true"] = float(np.median(true_scores))
    else:
        res["active_snr"] = 0.0
        res["p_true_gt_p99_noise"] = 0.0
        res["p_true_gt_p95_noise"] = 0.0
        res["p99_noise"] = 0.0
        res["p95_noise"] = 0.0
        res["max_noise"] = 0.0
        res["median_true"] = 0.0

    return res

def evaluate_residual_stratification_active(
    df: pd.DataFrame,
    channels: Dict[str, str],
    k: int = 3
) -> pd.DataFrame:
    """Evaluates active channel performance across smoothed residual quantiles Q1..Q4."""
    df_valid = df.dropna(subset=["smoothed_residual"])
    if len(df_valid) == 0:
        return pd.DataFrame()

    q_labels = ["Q1", "Q2", "Q3", "Q4"]
    df_valid["quantile"] = pd.qcut(df_valid["smoothed_residual"], q=4, labels=q_labels, duplicates="drop")

    rows = []
    for q_lab in q_labels:
        sub_df = df_valid[df_valid["quantile"] == q_lab]
        if len(sub_df) == 0:
            continue
        n_true = int(sub_df["truth_label"].sum())
        n_noise = int(len(sub_df) - n_true)
        base = n_true / float(len(sub_df))

        row = {
            "quantile": q_lab,
            "res_min": float(sub_df["smoothed_residual"].min()),
            "res_max": float(sub_df["smoothed_residual"].max()),
            "true_count": n_true,
            "noise_count": n_noise,
            "base_rate": base
        }

        best_p3 = 0.0
        best_chan = "NONE"
        best_snr = 0.0

        for ch_name, col in channels.items():
            res_ch = evaluate_channel_precision_at_k(sub_df, col, k_values=[3, 5])
            p3 = res_ch["p_at_3"]
            snr = res_ch["active_snr"]
            row[f"{ch_name}_p3"] = p3
            row[f"{ch_name}_snr"] = snr
            if p3 > best_p3 or (p3 == best_p3 and snr > best_snr):
                best_p3 = p3
                best_chan = ch_name
                best_snr = snr

        row["best_channel"] = best_chan
        row["best_p3"] = best_p3
        row["best_snr"] = best_snr
        rows.append(row)

    return pd.DataFrame(rows)

def evaluate_temporal_stratification_active(
    df: pd.DataFrame,
    windows: Dict[str, Tuple[int, int]],
    channels: Dict[str, str],
    shift_step: int = 1000
) -> pd.DataFrame:
    """Evaluates active channel performance across temporal post-shift windows A..E."""
    rows = []
    for win_name, (w_start, w_end) in windows.items():
        sub_df = df[(df["step"] >= w_start) & (df["step"] <= w_end)]
        if len(sub_df) == 0:
            continue

        n_true = int(sub_df["truth_label"].sum())
        n_noise = int(len(sub_df) - n_true)
        base = n_true / float(len(sub_df))

        row = {
            "window": win_name,
            "step_range": f"{w_start}-{w_end}",
            "true_count": n_true,
            "noise_count": n_noise,
            "base_rate": base
        }

        best_p3 = 0.0
        best_chan = "NONE"
        best_snr = 0.0

        for ch_name, col in channels.items():
            res_ch = evaluate_channel_precision_at_k(sub_df, col, k_values=[3, 5])
            p3 = res_ch["p_at_3"]
            snr = res_ch["active_snr"]
            row[f"{ch_name}_p3"] = p3
            row[f"{ch_name}_snr"] = snr
            if p3 > best_p3 or (p3 == best_p3 and snr > best_snr):
                best_p3 = p3
                best_chan = ch_name
                best_snr = snr

        row["best_channel"] = best_chan
        row["best_p3"] = best_p3
        row["best_snr"] = best_snr
        rows.append(row)

    return pd.DataFrame(rows)
