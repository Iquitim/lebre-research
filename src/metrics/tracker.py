import numpy as np
from typing import Dict, Any, List, Set

class ExperimentTracker:
    """
    Records per-step metrics and computes summary statistics for an online experiment.
    """
    def __init__(self, window_size: int = 50, noise_std: float = 0.1, shift_step: int = 1000):
        self.window_size = window_size
        self.noise_std = noise_std
        self.shift_step = shift_step
        
        self.steps: List[int] = []
        self.losses: List[float] = []
        self.sliding_mse: List[float] = []
        self.recalls: List[float] = []
        self.precisions: List[float] = []
        self.f1s: List[float] = []
        self.omitted_burdens: List[float] = []
        self.step_flops: List[int] = []
        self.step_probes: List[int] = []
        self.step_swaps: List[int] = []
        self.memory_bytes: List[int] = []
        
        self._loss_window: List[float] = []

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
        curr_sliding_mse = float(np.mean(self._loss_window))
        self.sliding_mse.append(curr_sliding_mse)
        
        # Support metrics
        tp = len(active_support.intersection(true_support))
        recall = tp / max(1, len(true_support))
        precision = tp / max(1, len(active_support))
        f1 = (2 * precision * recall) / max(1e-9, precision + recall)
        
        self.recalls.append(recall)
        self.precisions.append(precision)
        self.f1s.append(f1)
        
        # Omitted burden (energy of missed active features)
        omitted = true_support - active_support
        burden = float(np.sum([true_beta[j] ** 2 for j in omitted])) if omitted else 0.0
        self.omitted_burdens.append(burden)
        
        self.step_flops.append(step_stats.get("flops", 0))
        self.step_probes.append(step_stats.get("probes", 0))
        self.step_swaps.append(step_stats.get("swaps", 0))
        self.memory_bytes.append(step_stats.get("memory_bytes", 0))

    def compute_summary(self) -> Dict[str, Any]:
        total_steps = len(self.steps)
        if total_steps == 0:
            return {}
            
        overall_mse = float(np.mean(self.losses))
        
        # Regime 1 steady state (t in [800, 1000])
        r1_losses = [l for t, l in zip(self.steps, self.losses) if 800 <= t <= self.shift_step]
        r1_mse = float(np.mean(r1_losses)) if r1_losses else float("nan")
        
        # Regime 2 steady state (t in [1800, 2000])
        r2_losses = [l for t, l in zip(self.steps, self.losses) if 1800 <= t <= total_steps]
        r2_mse = float(np.mean(r2_losses)) if r2_losses else float("nan")
        
        # Recovery latency after shift_step:
        # Step where sliding MSE <= 2 * noise_std^2 and recall >= 0.8
        target_mse = 2.5 * (self.noise_std ** 2)
        recovery_step = None
        for t, smse, rec in zip(self.steps, self.sliding_mse, self.recalls):
            if t > self.shift_step and smse <= target_mse and rec >= 0.8:
                recovery_step = t
                break
                
        recovery_latency = (recovery_step - self.shift_step) if recovery_step is not None else (total_steps - self.shift_step)
        
        total_flops = int(np.sum(self.step_flops))
        total_probes = int(np.sum(self.step_probes))
        total_swaps = int(np.sum(self.step_swaps))
        peak_memory = int(np.max(self.memory_bytes)) if self.memory_bytes else 0
        
        final_recall = self.recalls[-1]
        final_precision = self.precisions[-1]
        final_f1 = self.f1s[-1]
        
        return {
            "overall_mse": overall_mse,
            "regime1_mse": r1_mse,
            "regime2_mse": r2_mse,
            "recovery_latency": recovery_latency,
            "recovered": recovery_step is not None,
            "final_recall": final_recall,
            "final_precision": final_precision,
            "final_f1": final_f1,
            "total_flops": total_flops,
            "flops_per_step": total_flops / total_steps,
            "total_probes": total_probes,
            "total_swaps": total_swaps,
            "peak_memory_bytes": peak_memory
        }
