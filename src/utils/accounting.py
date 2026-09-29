from typing import Dict, Any

class ResourceTracker:
    """
    Tracks operation counts, theoretical FLOPs, and memory bounds.
    """
    @staticmethod
    def dot_product_flops(length: int) -> int:
        return max(1, 2 * length - 1)

    @staticmethod
    def norm_sq_flops(length: int) -> int:
        return 2 * length

    @staticmethod
    def vector_update_flops(length: int) -> int:
        # scale + add
        return 2 * length

    @staticmethod
    def candidate_probe_flops(num_probes: int) -> int:
        # dot product with residual error (1 mul), abs (1 op), EMA update (2 ops)
        return 4 * num_probes

    @staticmethod
    def welford_probe_flops(num_probes: int) -> int:
        # For each probed candidate:
        # err * x (1 mul), delta = err*x - mean (1 sub), mean += delta/n (1 div, 1 add),
        # delta2 = err*x - mean (1 sub), M2 += delta*delta2 (1 mul, 1 add)
        # Total = 8 FLOPs per probed candidate
        return 8 * num_probes

    @staticmethod
    def pruning_check_flops(num_active: int) -> int:
        # Abs and comparison for each active feature: 2 ops
        return 2 * num_active

    @staticmethod
    def priority_scoring_flops(num_candidates: int) -> int:
        # 1 abs, 1 add, 1 div, 1 mul = 4 FLOPs per candidate
        return 4 * num_candidates

    @staticmethod
    def protection_check_flops(num_active: int) -> int:
        # age comparison for each active feature: 1 op
        return num_active

    @staticmethod
    def persistence_probe_flops(num_probes: int) -> int:
        # Per probed candidate:
        # Welford (8) + sign comparison & increment (2) + sign consistency (2) + conf factor (2) + score (3)
        # Total = 17 FLOPs/ops per probed candidate
        return 17 * num_probes

    @staticmethod
    def explore_confirm_check_flops(num_confirm_checked: int) -> int:
        # For each checked confirmed candidate: abs(mean) comparison (1) + sign_consistency comparison (1)
        # Total = 2 ops per candidate
        return 2 * num_confirm_checked

    @staticmethod
    def estimate_memory_bytes(active_params: int, candidate_slots: int, d_total: int, is_welford: bool = False, is_extended: bool = False) -> int:
        # 8 bytes per float64, 4 bytes per int32
        # active weights: 8 * active_params
        # active indices: 4 * active_params
        # active ages: 4 * active_params
        active_mem = (8 + 4 + 4) * active_params
        if is_extended:
            # count (4), mean (8), M2 (8), pos (4), neg (4), last_step (4) = 32 bytes per slot
            candidate_mem = 32 * candidate_slots
        elif is_welford:
            # candidate counts (4 bytes) + candidate mean (8 bytes) + candidate M2 (8 bytes)
            candidate_mem = 20 * candidate_slots
        else:
            # candidate EMA (8 bytes)
            candidate_mem = 8 * candidate_slots
        return active_mem + candidate_mem

