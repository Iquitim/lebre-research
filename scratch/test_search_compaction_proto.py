import sys
import os
import time
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.abspath('.'))

from scratch.bench_v02_integration import BENCHMARK_TASKS, generate_v02_stream
from scratch.run_v02_corrective_confirmation import (
    ResourceVector,
    CausalStandardScaler,
    FP16HistoryRingBuffer,
    LinearBasePredictor,
    RecurrentScalarUnit
)

print("Testing search compaction prototype imports and basic benchmark generation...")
stream = generate_v02_stream("I3_Single_Exact_Delay", seed=1801)
print(f"Generated stream: X shape = {stream['X'].shape}, y shape = {stream['y'].shape}")
