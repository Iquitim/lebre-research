"""Minimal reader for the Monash .tsf format: returns list of (series_name, np.array values)."""
import numpy as np


def read_tsf(path):
    out, data = [], False
    with open(path, encoding="latin-1") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.lower() == "@data":
                data = True
                continue
            if not data:
                continue
            parts = line.split(":")
            vals = [float(v) if v != "?" else np.nan for v in parts[-1].split(",")]
            out.append((parts[0], np.array(vals)))
    return out
