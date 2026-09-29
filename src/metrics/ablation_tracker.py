import numpy as np
from typing import Dict, Any, List, Set, Optional

class PromotionRecord:
    def __init__(self, step: int, feature: int, is_true: bool, score: float, evidence_count: int, victim: Optional[int], victim_is_true: Optional[bool]):
        self.step = step
        self.feature = feature
        self.is_true = is_true
        self.score = score
        self.evidence_count = evidence_count
        self.victim = victim
        self.victim_is_true = victim_is_true
        self.eviction_step: Optional[int] = None
        self.eviction_reason: Optional[str] = None

class AblationTracker:
    """
    Comprehensive tracking engine for EXP-0001b ablation diagnostics.
    """
    def __init__(self, total_steps: int = 2000, shift_step: int = 1000, noise_std: float = 0.1, window_size: int = 50):
        self.total_steps = total_steps
        self.shift_step = shift_step
        self.noise_std = noise_std
        self.window_size = window_size
        
        # Step arrays
        self.steps: List[int] = []
        self.losses: List[float] = []
        self.sliding_mse: List[float] = []
        self.recalls: List[float] = []
        self.precisions: List[float] = []
        self.f1s: List[float] = []
        self.support_sizes: List[int] = []
        self.flops: List[int] = []
        self.probes: List[int] = []
        self.mem_bytes: List[int] = []
        
        # Cumulative tracking
        self.cum_true_promotions: List[int] = []
        self.cum_false_promotions: List[int] = []
        self.cum_churn: List[int] = []
        
        self._loss_window: List[float] = []
        self._total_churn = 0
        self._total_true_prom = 0
        self._total_false_prom = 0
        
        # Promotions and life cycle tracking
        self.promotions: List[PromotionRecord] = []
        # Active features map: feature -> PromotionRecord
        self.active_features: Dict[int, PromotionRecord] = {}
        # History of evicted true features to count redundant repromotions
        self.previously_evicted_true: Set[int] = set()
        self.redundant_repromotions = 0
        
        # Detailed event log rows for CSV export
        self.event_log_rows: List[Dict[str, Any]] = []

    def record_step(
        self,
        t: int,
        step_stats: Dict[str, Any],
        active_support: Set[int],
        true_support: Set[int],
        true_beta: np.ndarray
    ) -> None:
        loss = step_stats["loss"]
        self.steps.append(t)
        self.losses.append(loss)
        
        # Sliding MSE
        self._loss_window.append(loss)
        if len(self._loss_window) > self.window_size:
            self._loss_window.pop(0)
        curr_smse = float(np.mean(self._loss_window))
        self.sliding_mse.append(curr_smse)
        
        # Support metrics
        tp = len(active_support.intersection(true_support))
        rec = tp / max(1, len(true_support))
        prec = tp / max(1, len(active_support))
        f1 = (2 * prec * rec) / max(1e-9, prec + rec)
        
        self.recalls.append(rec)
        self.precisions.append(prec)
        self.f1s.append(f1)
        self.support_sizes.append(len(active_support))
        self.flops.append(step_stats.get("flops", 0))
        self.probes.append(step_stats.get("probes", 0))
        self.mem_bytes.append(step_stats.get("memory_bytes", 0))
        
        # Process evictions / prunings first
        victim = step_stats.get("victim_feat")
        pruned = step_stats.get("pruned_feats", [])
        
        if victim is not None:
            self._total_churn += 1
            if victim in self.active_features:
                rec_v = self.active_features.pop(victim)
                rec_v.eviction_step = t
                rec_v.eviction_reason = "swap"
                if rec_v.is_true:
                    self.previously_evicted_true.add(victim)
                    
        for p in pruned:
            self._total_churn += 1
            if p in self.active_features:
                rec_p = self.active_features.pop(p)
                rec_p.eviction_step = t
                rec_p.eviction_reason = "pruned"
                if rec_p.is_true:
                    self.previously_evicted_true.add(p)
                    
        # Process promotion
        promoted = step_stats.get("promoted_feat")
        if promoted is not None:
            self._total_churn += 1
            is_true = promoted in true_support
            if is_true:
                self._total_true_prom += 1
                if promoted in self.previously_evicted_true:
                    self.redundant_repromotions += 1
            else:
                self._total_false_prom += 1
                
            victim_is_true = (victim in true_support) if victim is not None else None
            
            p_rec = PromotionRecord(
                step=t,
                feature=promoted,
                is_true=is_true,
                score=step_stats.get("cand_score", 0.0),
                evidence_count=step_stats.get("cand_evidence_count", 0),
                victim=victim,
                victim_is_true=victim_is_true
            )
            self.promotions.append(p_rec)
            self.active_features[promoted] = p_rec
            
            # Event log entry
            self.event_log_rows.append({
                "step": t,
                "candidate": promoted,
                "candidate_truth_status": is_true,
                "candidate_evidence_count": p_rec.evidence_count,
                "candidate_score": p_rec.score,
                "promotion_event": True,
                "victim": victim if victim is not None else -1,
                "victim_truth_status": victim_is_true if victim_is_true is not None else False,
                "new_feature_age": 0,
                "eviction_time": -1  # populated post-hoc if evicted
            })
            
        self.cum_true_promotions.append(self._total_true_prom)
        self.cum_false_promotions.append(self._total_false_prom)
        self.cum_churn.append(self._total_churn)

    def finalize(self) -> None:
        # Populate eviction_time in event log for seed 42 export
        # Map (step, feature) -> eviction_step
        eviction_map = {}
        for p in self.promotions:
            evict_step = p.eviction_step if p.eviction_step is not None else self.total_steps
            eviction_map[(p.step, p.feature)] = evict_step
            
        for row in self.event_log_rows:
            key = (row["step"], row["candidate"])
            if key in eviction_map:
                row["eviction_time"] = eviction_map[key]

    def compute_summary(self) -> Dict[str, Any]:
        self.finalize()
        total_steps = len(self.steps)
        if total_steps == 0:
            return {}
            
        overall_mse = float(np.mean(self.losses))
        
        # Steady state errors
        r1_losses = [l for t, l in zip(self.steps, self.losses) if 800 <= t <= self.shift_step]
        r1_mse = float(np.mean(r1_losses)) if r1_losses else float("nan")
        
        r2_losses = [l for t, l in zip(self.steps, self.losses) if 1800 <= t <= total_steps]
        r2_mse = float(np.mean(r2_losses)) if r2_losses else float("nan")
        
        # Recovery latency post shift
        target_mse = 2.5 * (self.noise_std ** 2)
        rec_step = None
        for t, smse, rec in zip(self.steps, self.sliding_mse, self.recalls):
            if t > self.shift_step and smse <= target_mse and rec >= 0.8:
                rec_step = t
                break
        recovery_latency = (rec_step - self.shift_step) if rec_step is not None else (total_steps - self.shift_step)
        
        # Promotion metrics
        true_proms = self._total_true_prom
        false_proms = self._total_false_prom
        total_proms = true_proms + false_proms
        prom_precision = (true_proms / total_proms) if total_proms > 0 else 0.0
        
        # Survival metrics
        # For horizon H: was feature still active at step + H?
        def calc_survival(records: List[PromotionRecord], horizon: int) -> float:
            if not records:
                return 0.0
            survived = 0
            for r in records:
                target_s = r.step + horizon
                # Survived if not evicted before target_s
                if r.eviction_step is None or r.eviction_step >= target_s:
                    survived += 1
            return survived / len(records)
            
        true_records = [r for r in self.promotions if r.is_true]
        noise_records = [r for r in self.promotions if not r.is_true]
        
        true_surv_10 = calc_survival(true_records, 10)
        true_surv_50 = calc_survival(true_records, 50)
        true_surv_100 = calc_survival(true_records, 100)
        
        noise_surv_10 = calc_survival(noise_records, 10)
        noise_surv_50 = calc_survival(noise_records, 50)
        noise_surv_100 = calc_survival(noise_records, 100)
        
        # Promotion-to-eviction latency
        def calc_latencies(records: List[PromotionRecord]) -> Dict[str, float]:
            if not records:
                return {"mean": 0.0, "median": 0.0, "p10": 0.0, "p90": 0.0}
            lats = [
                ((r.eviction_step - r.step) if r.eviction_step is not None else (total_steps - r.step))
                for r in records
            ]
            return {
                "mean": float(np.mean(lats)),
                "median": float(np.median(lats)),
                "p10": float(np.percentile(lats, 10)),
                "p90": float(np.percentile(lats, 90))
            }
            
        true_lats = calc_latencies(true_records)
        noise_lats = calc_latencies(noise_records)
        
        # Churn per 100 steps
        churn_per_100 = (self._total_churn / (total_steps / 100.0))
        
        total_flops = int(np.sum(self.flops))
        flops_per_step = total_flops / total_steps
        peak_mem = int(np.max(self.mem_bytes)) if self.mem_bytes else 0
        
        return {
            "overall_mse": overall_mse,
            "regime1_mse": r1_mse,
            "regime2_mse": r2_mse,
            "recovery_latency": recovery_latency,
            "recovered": rec_step is not None,
            "final_recall": self.recalls[-1],
            "final_precision": self.precisions[-1],
            "final_f1": self.f1s[-1],
            "true_promotions": true_proms,
            "false_promotions": false_proms,
            "total_promotions": total_proms,
            "promotion_precision": prom_precision,
            "true_survival_10": true_surv_10,
            "true_survival_50": true_surv_50,
            "true_survival_100": true_surv_100,
            "noise_survival_10": noise_surv_10,
            "noise_survival_50": noise_surv_50,
            "noise_survival_100": noise_surv_100,
            "true_latency_mean": true_lats["mean"],
            "true_latency_median": true_lats["median"],
            "noise_latency_mean": noise_lats["mean"],
            "noise_latency_median": noise_lats["median"],
            "redundant_repromotions": self.redundant_repromotions,
            "churn_per_100": churn_per_100,
            "total_flops": total_flops,
            "flops_per_step": flops_per_step,
            "peak_memory_bytes": peak_mem
        }
