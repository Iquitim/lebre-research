"""heldout2_cfg.py — the frozen canonical configuration of LEBRE v0.52 (copied verbatim from the frozen
LEBRE-V0.52-HELDOUT-02/heldout2_run.py, V052["V052_CORRIGIDA"] = final7.PADRAO + gap_hold + out_contract), importable
without touching the frozen files. A check asserts equality with the frozen definition at import time."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "LEBRE-V0.52-PROTO-01")))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "LEBRE-V0.52-HELDOUT-02")))

CANONICAL = {"scale_floor": 0.1, "peak_persist": True, "evidence": "psiE1", "lazy_halves": True, "screen_skip_active": True,
             "track_groups": True, "mu": 0.05, "stagger": True, "screen_spread": True, "peak_split": True, "peak_until": 200,
             "chal_warm": 250, "gap_hold": True, "out_contract": True}

import heldout2_run as _H  # noqa: E402
assert _H.V052["V052_CORRIGIDA"] == CANONICAL, "canonical configuration differs from the frozen one"
