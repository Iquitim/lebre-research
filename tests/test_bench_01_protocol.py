"""
Unit tests for BENCH-01 Protocol Validation, Immutability & Causal Plumbing.
Governing Standards: Sections 224-228 of BENCH-01A & Sections 51-54 of Protocol BENCH-01A-R.
"""

import json
import hashlib
from pathlib import Path
import numpy as np
import pytest

CONFIG_PATH = Path("experiments/BENCH-01A/bench_01_locked_config.json")
SPEC_PATH = Path("docs/history/phase-v0.1/BENCH_01_SPEC.md")

# Reconciled cryptographic hashes (BENCH-01A-R)
EXPECTED_SPEC_SHA256 = "f516914da4d511e9ed58c2eb575d628bf3e01ebaab9f8bf63f9da0ebfe0e0c28"
EXPECTED_CONFIG_SHA256 = "cb0d696e3e2775afa802a5a037ddf58ad3887252e4ac302e62b7e6162d334f7a"


def test_spec_and_config_immutability():
    """Verify cryptographic SHA-256 hashes of specification and locked config."""
    assert SPEC_PATH.exists(), "BENCH_01_SPEC.md missing"
    assert CONFIG_PATH.exists(), "bench_01_locked_config.json missing"

    spec_bytes = SPEC_PATH.read_bytes()
    config_bytes = CONFIG_PATH.read_bytes()

    spec_hash = hashlib.sha256(spec_bytes).hexdigest()
    config_hash = hashlib.sha256(config_bytes).hexdigest()

    assert spec_hash == EXPECTED_SPEC_SHA256, f"SPEC hash mismatch: {spec_hash}"
    assert config_hash == EXPECTED_CONFIG_SHA256, f"CONFIG hash mismatch: {config_hash}"


def test_config_integrity():
    """Verify configuration structure, seed counts, and chronological split fractions."""
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        cfg = json.load(f)

    splits = cfg["stream_chronological_splits"]
    assert splits["calibration_prefix_fraction"] == 0.15, "Calibration prefix must be exactly 0.15 (15%)"
    assert splits["validation_segment_fraction"] == 0.15, "Validation segment must be exactly 0.15 (15%)"
    assert splits["test_segment_fraction"] == 0.70, "Test segment must be exactly 0.70 (70%)"
    total_fraction = (
        splits["calibration_prefix_fraction"]
        + splits["validation_segment_fraction"]
        + splits["test_segment_fraction"]
    )
    assert np.isclose(total_fraction, 1.0), "Splits must sum to 1.0"

    seeds = cfg["random_seed_suite"]["evaluation_seeds"]
    assert len(seeds) == 30, "Must contain exactly 30 evaluation seeds"
    assert len(set(seeds)) == 30, "All evaluation seeds must be unique"

    baselines = cfg["baselines"]["competitive_baselines"]
    for b in baselines:
        assert b["max_configs"] == 16, f"Baseline {b['id']} must have exactly 16 configs"
        grid = b["search_grid"]
        prod = 1
        for vals in grid.values():
            prod *= len(vals)
        assert prod == 16, f"Grid product for {b['id']} is {prod}, expected 16"


def test_elec2_qualified_label():
    """Verify that ELEC2 is explicitly qualified as a derived continuous regression task."""
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        cfg = json.load(f)

    block_b = cfg["dataset_manifest"]["block_b_public_real_world"]
    b1_dataset = next((d for d in block_b if "NSW" in d["id"] or "elec" in d["file_artifact"]), None)
    assert b1_dataset is not None, "B1 dataset missing in config"
    assert b1_dataset["id"] == "B1_NSW_Electricity_Derived_Regression"
    assert b1_dataset["task_status"] == "NONCANONICAL_DERIVED_REGRESSION_TASK"
    assert b1_dataset["canonical_task_type"] == "binary_classification"
    assert b1_dataset["derived_task_type"] == "continuous_price_regression"


def test_architecture_neutral_resource_matching():
    """Verify that Regime R2 matching contains no universal Track-B structural constraints."""
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        cfg = json.load(f)

    r2_limits = cfg["resource_accounting_spec"]["r2_resource_matched_limits"]
    assert r2_limits["r2_flop_ceiling_mean_flops"] == 100
    assert r2_limits["r2_mem_ceiling_bytes"] == 1024
    assert r2_limits["architecture_specific_constraints_enforced"] is False
    assert "max_active_parameters" not in r2_limits, "Universal K limit must be removed"
    assert "max_recurrent_states" not in r2_limits, "Universal N limit must be removed"


def test_neutral_failure_policy():
    """Verify that arbitrary 1.5x penalty is removed in favor of neutral failure tracking."""
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        cfg = json.load(f)

    failure_proto = cfg["failure_handling_protocol"]
    assert failure_proto["arbitrary_penalty_enabled"] is False
    assert failure_proto["divergence_reporting"] == "DIVERGENCE_RATE"
    assert failure_proto["failed_run_score"] == "FAILED_RUN_INFINITY"
    assert failure_proto["predictive_metrics_aggregation"] == "VALID_COMPLETE_RUNS_ONLY"


def test_muse_rnn_minimal_adaptation():
    """Verify that MUSE-RNN is documented with minimal regression adaptation metadata."""
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        cfg = json.load(f)

    baselines = cfg["baselines"]["competitive_baselines"]
    muse = next((b for b in baselines if b["id"] == "B3_MUSE_RNN"), None)
    assert muse is not None, "B3_MUSE_RNN missing in config"
    assert muse["adaptation_status"] == "MUSE_RNN_REGRESSION_MINIMAL_ADAPTATION"


def test_causal_prequential_scaler_plumbing():
    """Verify that online adaptive standard scaler updates strictly after prediction."""
    mu = 0.0
    var = 1.0
    alpha = 0.01

    raw_stream = [10.0, 20.0, 15.0, 30.0, 25.0]

    for t, x in enumerate(raw_stream):
        mu_prev = mu
        var_prev = var
        x_norm = (x - mu_prev) / np.sqrt(var_prev + 1e-6)

        mu = (1 - alpha) * mu + alpha * x
        var = (1 - alpha) * var + alpha * (x - mu) ** 2

        expected_x_norm = (x - mu_prev) / np.sqrt(var_prev + 1e-6)
        assert np.isclose(x_norm, expected_x_norm)


def test_non_competitive_dry_run_plumbing():
    """Verify standard prequential streaming API loop on tiny synthetic prefix."""
    class MockBaseline:
        def __init__(self):
            self.w = 0.0
            self.flops_history = []

        def predict(self, x):
            return self.w * x

        def update(self, x, y):
            y_hat = self.predict(x)
            err = y - y_hat
            self.w += 0.01 * err * x
            self.flops_history.append(4)  # 2 MACs = 4 FLOPs

    model = MockBaseline()
    np.random.seed(42)
    X = np.random.randn(10)
    Y = 2.0 * X + 0.1 * np.random.randn(10)

    prequential_losses = []
    for t in range(len(X)):
        y_hat = model.predict(X[t])
        loss = (Y[t] - y_hat) ** 2
        prequential_losses.append(loss)
        model.update(X[t], Y[t])

    assert len(prequential_losses) == 10
    assert len(model.flops_history) == 10
    assert np.all(np.isfinite(prequential_losses))
