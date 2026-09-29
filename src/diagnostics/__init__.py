"""
Diagnostics module for Track B empirical investigations.
"""
from .candidate_separability import (
    CandidateSnapshotCollector,
    compute_diagnostic_scores,
    compute_distribution_stats,
    compute_roc_pr_auc,
    evaluate_precision_at_k,
    evaluate_temporal_stratification,
    evaluate_residual_stratification,
    evaluate_rank_stability,
    evaluate_counterfactual_elevation,
    evaluate_leave_one_seed_out_logistic
)

from .candidate_microtest import (
    MicrotestDiagnosticObserver,
    evaluate_channel_precision_at_k,
    evaluate_temporal_stratification_microtest,
    evaluate_residual_stratification_microtest,
    evaluate_counterfactual_queue_enrichment,
    evaluate_leave_one_seed_out_logistic_microtest
)

from .active_probe_diagnostic import (
    ActiveProbeDiagnosticObserver,
    get_hadamard_matrix,
    evaluate_residual_stratification_active,
    evaluate_temporal_stratification_active
)

from .frontier_evaluator import (
    compute_gamma,
    compute_gamma_resource,
    compute_energy_metrics,
    classify_regime_identifiability,
    classify_prediction_sufficient,
    classify_2x2_matrix,
    compute_metric_correlations
)

__all__ = [
    "CandidateSnapshotCollector",
    "compute_diagnostic_scores",
    "compute_distribution_stats",
    "compute_roc_pr_auc",
    "evaluate_precision_at_k",
    "evaluate_temporal_stratification",
    "evaluate_residual_stratification",
    "evaluate_rank_stability",
    "evaluate_counterfactual_elevation",
    "evaluate_leave_one_seed_out_logistic",
    "MicrotestDiagnosticObserver",
    "evaluate_channel_precision_at_k",
    "evaluate_temporal_stratification_microtest",
    "evaluate_residual_stratification_microtest",
    "evaluate_counterfactual_queue_enrichment",
    "evaluate_leave_one_seed_out_logistic_microtest",
    "ActiveProbeDiagnosticObserver",
    "get_hadamard_matrix",
    "evaluate_residual_stratification_active",
    "evaluate_temporal_stratification_active",
    "compute_gamma",
    "compute_gamma_resource",
    "compute_energy_metrics",
    "classify_regime_identifiability",
    "classify_prediction_sufficient",
    "classify_2x2_matrix",
    "compute_metric_correlations"
]


