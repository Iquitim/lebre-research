#!/usr/bin/env python3
"""
bounded_history_providers.py: Modular History Providers for BOUNDED-HISTORY-LAG-INTEGRATION-01.

Implements unified interface:
  write(x_t) -> write_flops
  query(channel, lag) -> (value, available, lookup_type, est_error, lookup_flops)
  get_memory_breakdown() -> dict(persistent_bytes, transient_bytes, metadata_bytes)
"""

import numpy as np
from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple, Optional

class HistoryProvider(ABC):
    @abstractmethod
    def write(self, x_t: np.ndarray) -> int:
        pass

    @abstractmethod
    def query(self, channel: int, lag: int) -> Tuple[float, bool, str, float, int]:
        pass

    @abstractmethod
    def get_memory_breakdown(self) -> Dict[str, int]:
        pass

    @property
    @abstractmethod
    def provider_id(self) -> str:
        pass


# -----------------------------------------------------------------------------
# H0: EXACT_FP32_RING (Reference Baseline)
# -----------------------------------------------------------------------------
class ExactFP32RingProvider(HistoryProvider):
    def __init__(self, d_features: int = 5, l_max: int = 32):
        self.D = d_features
        self.L_max = l_max
        self.buffer = np.zeros((d_features, l_max + 1), dtype=np.float32)
        self.head = 0
        self._meta_bytes = 20
        
    @property
    def provider_id(self) -> str:
        return "H0_EXACT_FP32_RING"
        
    def write(self, x_t: np.ndarray) -> int:
        self.buffer[:, self.head] = x_t.astype(np.float32)
        self.head = (self.head + 1) % (self.L_max + 1)
        return self.D # 1 write per channel
        
    def query(self, channel: int, lag: int) -> Tuple[float, bool, str, float, int]:
        if lag < 1 or lag > self.L_max:
            return 0.0, False, "UNAVAILABLE", 0.0, 1
        idx = (self.head - 1 - lag) % (self.L_max + 1)
        val = float(self.buffer[channel, idx])
        return val, True, "EXACT_POINT_LOOKUP", 0.0, 2 # modulo + array index
        
    def get_memory_breakdown(self) -> Dict[str, int]:
        raw_bytes = self.D * (self.L_max + 1) * 4 # 5 * 33 * 4 = 660 bytes
        return {
            'persistent_bytes': raw_bytes + self._meta_bytes,
            'history_bytes': raw_bytes,
            'metadata_bytes': self._meta_bytes,
            'transient_bytes': 0
        }


# -----------------------------------------------------------------------------
# H1: FP16_EXACT_RING (Precision Reduction)
# -----------------------------------------------------------------------------
class FP16RingProvider(HistoryProvider):
    def __init__(self, d_features: int = 5, l_max: int = 32):
        self.D = d_features
        self.L_max = l_max
        self.buffer = np.zeros((d_features, l_max + 1), dtype=np.float16)
        self.head = 0
        self._meta_bytes = 20
        
    @property
    def provider_id(self) -> str:
        return "H1_FP16_EXACT_RING"
        
    def write(self, x_t: np.ndarray) -> int:
        # Cast to float16: costs 1 conversion FLOP per channel
        self.buffer[:, self.head] = x_t.astype(np.float16)
        self.head = (self.head + 1) % (self.L_max + 1)
        return self.D * 2 # convert + write
        
    def query(self, channel: int, lag: int) -> Tuple[float, bool, str, float, int]:
        if lag < 1 or lag > self.L_max:
            return 0.0, False, "UNAVAILABLE", 0.0, 1
        idx = (self.head - 1 - lag) % (self.L_max + 1)
        val = float(self.buffer[channel, idx]) # cast back to float
        return val, True, "APPROXIMATE_POINT_LOOKUP", 1e-4, 3 # index + unpack
        
    def get_memory_breakdown(self) -> Dict[str, int]:
        raw_bytes = self.D * (self.L_max + 1) * 2 # 5 * 33 * 2 = 330 bytes
        return {
            'persistent_bytes': raw_bytes + self._meta_bytes,
            'history_bytes': raw_bytes,
            'metadata_bytes': self._meta_bytes,
            'transient_bytes': 0
        }


# -----------------------------------------------------------------------------
# H2: INT16_QUANTIZED_RING (16-bit Fixed-Point Quantization)
# -----------------------------------------------------------------------------
class QuantizedInt16RingProvider(HistoryProvider):
    def __init__(self, d_features: int = 5, l_max: int = 32):
        self.D = d_features
        self.L_max = l_max
        self.buffer = np.zeros((d_features, l_max + 1), dtype=np.int16)
        self.head = 0
        # Per-channel running envelope scale (float32)
        self.scale = np.ones(d_features, dtype=np.float32) * 4.0 # default 4 sigma
        self._meta_bytes = 20 + d_features * 4 # head metadata + scale array
        self.saturation_count = 0
        self.total_writes = 0
        
    @property
    def provider_id(self) -> str:
        return "H2_INT16_QUANTIZED_RING"
        
    def write(self, x_t: np.ndarray) -> int:
        flops = 0
        self.total_writes += self.D
        # Update running peak magnitude scale causally
        for i in range(self.D):
            ax = abs(float(x_t[i]))
            if ax > self.scale[i]:
                self.scale[i] = max(1.0, 0.99 * self.scale[i] + 0.01 * (ax * 1.2))
            flops += 3
            # Quantize: q = clip(round(x * 32767 / scale), -32767, 32767)
            scaled = (x_t[i] / self.scale[i]) * 32767.0
            if abs(scaled) > 32767.0:
                self.saturation_count += 1
            q = int(np.clip(np.round(scaled), -32767, 32767))
            self.buffer[i, self.head] = q
            flops += 4
        self.head = (self.head + 1) % (self.L_max + 1)
        return flops
        
    def query(self, channel: int, lag: int) -> Tuple[float, bool, str, float, int]:
        if lag < 1 or lag > self.L_max:
            return 0.0, False, "UNAVAILABLE", 0.0, 1
        idx = (self.head - 1 - lag) % (self.L_max + 1)
        q = self.buffer[channel, idx]
        # Dequantize: val = q * scale / 32767.0
        val = float(q) * (self.scale[channel] / 32767.0)
        return val, True, "APPROXIMATE_POINT_LOOKUP", float(self.scale[channel] / 32767.0), 4
        
    def get_memory_breakdown(self) -> Dict[str, int]:
        raw_bytes = self.D * (self.L_max + 1) * 2 # 330 bytes
        return {
            'persistent_bytes': raw_bytes + self._meta_bytes,
            'history_bytes': raw_bytes,
            'metadata_bytes': self._meta_bytes,
            'transient_bytes': 0
        }


# -----------------------------------------------------------------------------
# H3: INT8_QUANTIZED_RING (8-bit Quantization)
# -----------------------------------------------------------------------------
class QuantizedInt8RingProvider(HistoryProvider):
    def __init__(self, d_features: int = 5, l_max: int = 32):
        self.D = d_features
        self.L_max = l_max
        self.buffer = np.zeros((d_features, l_max + 1), dtype=np.int8)
        self.head = 0
        self.scale = np.ones(d_features, dtype=np.float32) * 4.0 # default 4 sigma
        self._meta_bytes = 20 + d_features * 4
        self.saturation_count = 0
        self.total_writes = 0
        
    @property
    def provider_id(self) -> str:
        return "H3_INT8_QUANTIZED_RING"
        
    def write(self, x_t: np.ndarray) -> int:
        flops = 0
        self.total_writes += self.D
        for i in range(self.D):
            ax = abs(float(x_t[i]))
            if ax > self.scale[i]:
                self.scale[i] = max(1.0, 0.99 * self.scale[i] + 0.01 * (ax * 1.2))
            flops += 3
            # Quantize to 8-bit signed [-127, 127]
            scaled = (x_t[i] / self.scale[i]) * 127.0
            if abs(scaled) > 127.0:
                self.saturation_count += 1
            q = int(np.clip(np.round(scaled), -127, 127))
            self.buffer[i, self.head] = q
            flops += 4
        self.head = (self.head + 1) % (self.L_max + 1)
        return flops
        
    def query(self, channel: int, lag: int) -> Tuple[float, bool, str, float, int]:
        if lag < 1 or lag > self.L_max:
            return 0.0, False, "UNAVAILABLE", 0.0, 1
        idx = (self.head - 1 - lag) % (self.L_max + 1)
        q = self.buffer[channel, idx]
        val = float(q) * (self.scale[channel] / 127.0)
        return val, True, "APPROXIMATE_POINT_LOOKUP", float(self.scale[channel] / 127.0), 4
        
    def get_memory_breakdown(self) -> Dict[str, int]:
        raw_bytes = self.D * (self.L_max + 1) * 1 # 165 bytes
        return {
            'persistent_bytes': raw_bytes + self._meta_bytes,
            'history_bytes': raw_bytes,
            'metadata_bytes': self._meta_bytes,
            'transient_bytes': 0
        }


# -----------------------------------------------------------------------------
# H4: AGE_AWARE_MIXED_PRECISION (Recent FP16, Older INT8)
# -----------------------------------------------------------------------------
class AgeAwareMixedPrecisionProvider(HistoryProvider):
    def __init__(self, d_features: int = 5, l_max: int = 32, split_lag: int = 8):
        self.D = d_features
        self.L_max = l_max
        self.split = split_lag # lags 1..8 in FP16, 9..32 in INT8
        self.buf_recent = np.zeros((d_features, split_lag + 1), dtype=np.float16)
        self.buf_older = np.zeros((d_features, (l_max - split_lag) + 1), dtype=np.int8)
        self.head = 0
        self.scale = np.ones(d_features, dtype=np.float32) * 4.0
        self._meta_bytes = 24 + d_features * 4
        
    @property
    def provider_id(self) -> str:
        return "H4_AGE_AWARE_MIXED_PRECISION"
        
    def write(self, x_t: np.ndarray) -> int:
        flops = 0
        evict_idx = self.head % (self.split + 1)
        # 1. Evict sample at lag (split + 1) to older buffer BEFORE overwriting
        for i in range(self.D):
            val_evict = float(self.buf_recent[i, evict_idx])
            ax = abs(val_evict)
            if ax > self.scale[i]:
                self.scale[i] = max(1.0, 0.99 * self.scale[i] + 0.01 * (ax * 1.2))
            flops += 3
            q = int(np.clip(np.round((val_evict / self.scale[i]) * 127.0), -127, 127))
            idx_old = self.head % ((self.L_max - self.split) + 1)
            self.buf_older[i, idx_old] = q
            flops += 4
            
        # 2. Write new incoming sample to recent FP16 buffer
        self.buf_recent[:, evict_idx] = x_t.astype(np.float16)
        flops += self.D * 2
        self.head += 1
        return flops
        
    def query(self, channel: int, lag: int) -> Tuple[float, bool, str, float, int]:
        if lag < 1 or lag > self.L_max:
            return 0.0, False, "UNAVAILABLE", 0.0, 1
        if lag <= self.split:
            idx = (self.head - 1 - lag) % (self.split + 1)
            val = float(self.buf_recent[channel, idx])
            return val, True, "APPROXIMATE_POINT_LOOKUP", 1e-4, 3
        else:
            # Older INT8 section: lag relative to split+1
            lag_rel = lag - (self.split + 1)
            idx_old = (self.head - 1 - lag_rel) % ((self.L_max - self.split) + 1)
            q = self.buf_older[channel, idx_old]
            val = float(q) * (self.scale[channel] / 127.0)
            return val, True, "APPROXIMATE_POINT_LOOKUP", float(self.scale[channel] / 127.0), 5
            
    def get_memory_breakdown(self) -> Dict[str, int]:
        bytes_rec = self.D * (self.split + 1) * 2 # 5 * 9 * 2 = 90 bytes
        bytes_old = self.D * ((self.L_max - self.split) + 1) * 1 # 5 * 25 * 1 = 125 bytes
        raw_bytes = bytes_rec + bytes_old # 215 bytes
        return {
            'persistent_bytes': raw_bytes + self._meta_bytes,
            'history_bytes': raw_bytes,
            'metadata_bytes': self._meta_bytes,
            'transient_bytes': 0
        }


# -----------------------------------------------------------------------------
# H5: MULTIRATE_HISTORY (Recent Dense, Older Decimated)
# -----------------------------------------------------------------------------
class MultirateRingProvider(HistoryProvider):
    def __init__(self, d_features: int = 5, l_max: int = 32, use_anti_alias: bool = False):
        self.D = d_features
        self.L_max = l_max
        self.use_anti_alias = use_anti_alias
        # Tier 1 (lags 1..8): 9 samples dense ring (lags 0..8)
        self.buf_dense = np.zeros((d_features, 9), dtype=np.float32)
        # Tier 2 (lags 9..16): 5 samples downsampled by 2
        self.buf_m2 = np.zeros((d_features, 5), dtype=np.float32)
        # Tier 3 (lags 17..32): 5 samples downsampled by 4
        self.buf_m4 = np.zeros((d_features, 5), dtype=np.float32)
        self.head = 0
        self.head_m2 = 0
        self.head_m4 = 0
        self._meta_bytes = 28
        
    @property
    def provider_id(self) -> str:
        return "H5_MULTIRATE_ANTI_ALIAS" if self.use_anti_alias else "H5_MULTIRATE_NAIVE_DECIMATION"
        
    def write(self, x_t: np.ndarray) -> int:
        flops = 0
        # 1. Update Tier 2: when sample reaches age 8, transfer every 2 steps
        if self.head % 2 == 0 and self.head >= 8:
            idx_s8 = (self.head - 8) % 9
            if self.use_anti_alias:
                idx_s7 = (self.head - 7) % 9
                s_m2 = 0.5 * (self.buf_dense[:, idx_s8] + self.buf_dense[:, idx_s7])
                flops += self.D * 3
            else:
                s_m2 = self.buf_dense[:, idx_s8].copy()
                flops += self.D
            self.buf_m2[:, self.head_m2 % 5] = s_m2
            self.head_m2 += 1
            
        # 2. Update Tier 3: when sample reaches age 16 in Tier 2, transfer every 4 steps
        if self.head % 4 == 0 and self.head >= 16:
            idx_s16 = (self.head_m2 - 1 - 4) % 5
            if self.use_anti_alias:
                idx_s14 = (self.head_m2 - 1 - 3) % 5
                s_m4 = 0.5 * (self.buf_m2[:, idx_s16] + self.buf_m2[:, idx_s14])
                flops += self.D * 3
            else:
                s_m4 = self.buf_m2[:, idx_s16].copy()
                flops += self.D
            self.buf_m4[:, self.head_m4 % 5] = s_m4
            self.head_m4 += 1
            
        # 3. Write new sample into dense Tier 1
        self.buf_dense[:, self.head % 9] = x_t.astype(np.float32)
        flops += self.D
        self.head += 1
        return flops
        
    def query(self, channel: int, lag: int) -> Tuple[float, bool, str, float, int]:
        if lag < 1 or lag > self.L_max:
            return 0.0, False, "UNAVAILABLE", 0.0, 1
            
        if lag <= 8:
            idx = (self.head - 1 - lag) % 9
            val = float(self.buf_dense[channel, idx])
            return val, True, "EXACT_POINT_LOOKUP", 0.0, 2
        elif lag <= 16:
            # Tier 2 (downsample 2x)
            phase2 = (self.head - 1) % 2
            k_step = int(np.clip(np.round((lag - (8 + phase2)) / 2.0), 0, 4))
            idx = (self.head_m2 - 1 - k_step) % 5
            val = float(self.buf_m2[channel, idx])
            is_exact = ((lag - (8 + phase2)) % 2 == 0 and not self.use_anti_alias)
            return val, True, "EXACT_POINT_LOOKUP" if is_exact else "APPROXIMATE_POINT_LOOKUP", 0.0 if is_exact else 0.2, 4
        else:
            # Tier 3 (downsample 4x)
            phase4 = (self.head - 1) % 4
            k_step = int(np.clip(np.round((lag - (16 + phase4)) / 4.0), 0, 4))
            idx = (self.head_m4 - 1 - k_step) % 5
            val = float(self.buf_m4[channel, idx])
            is_exact = ((lag - (16 + phase4)) % 4 == 0 and not self.use_anti_alias)
            return val, True, "EXACT_POINT_LOOKUP" if is_exact else "APPROXIMATE_POINT_LOOKUP", 0.0 if is_exact else 0.35, 5
            
    def get_memory_breakdown(self) -> Dict[str, int]:
        # Dense (9) + Tier 2 (5) + Tier 3 (5) = 19 samples * 5 channels * 4 bytes = 380 bytes
        raw_bytes = self.D * (9 + 5 + 5) * 4
        return {
            'persistent_bytes': raw_bytes + self._meta_bytes,
            'history_bytes': raw_bytes,
            'metadata_bytes': self._meta_bytes,
            'transient_bytes': 0
        }


# -----------------------------------------------------------------------------
# H7: HIPPO_POLYNOMIAL_HISTORY (Shifted Legendre Polynomial Projection)
# -----------------------------------------------------------------------------
class PolynomialHistoryProvider(HistoryProvider):
    def __init__(self, d_features: int = 5, l_max: int = 32, n_poly: int = 6):
        self.D = d_features
        self.L_max = l_max
        self.N_p = n_poly # Order 6 Legendre polynomials
        # State: m in R^{D x N_p}
        self.state = np.zeros((d_features, n_poly), dtype=np.float32)
        # Precompute discrete transition matrices for sliding window of length L_max
        # A in R^{N_p x N_p}, B in R^{N_p}
        self.A = np.zeros((n_poly, n_poly), dtype=np.float32)
        self.B = np.zeros(n_poly, dtype=np.float32)
        theta = float(l_max)
        for n in range(n_poly):
            self.B[n] = np.sqrt(2 * n + 1) / theta
            for m in range(n_poly):
                if n > m:
                    self.A[n, m] = ((-1)**(n - m)) * np.sqrt(2 * n + 1) * np.sqrt(2 * m + 1) / theta
                elif n == m:
                    self.A[n, m] = -(n + 1) / theta
                else:
                    self.A[n, m] = 0.0
        # Discretize: I + dt * A
        self.dt = 1.0
        self.A_d = np.eye(n_poly, dtype=np.float32) + self.dt * self.A
        self.B_d = self.dt * self.B
        self._meta_bytes = 40 + (n_poly * n_poly + n_poly) * 4 # matrix parameters
        
    @property
    def provider_id(self) -> str:
        return "H7_HIPPO_POLYNOMIAL_HISTORY"
        
    def write(self, x_t: np.ndarray) -> int:
        flops = 0
        for i in range(self.D):
            # state update: m_next = A_d * m + B_d * x_t[i]
            # Matrix-vector multiply (N_p x N_p): 2 * N_p^2 FLOPs
            self.state[i] = np.dot(self.A_d, self.state[i]) + self.B_d * float(x_t[i])
            flops += 2 * (self.N_p ** 2) + 2 * self.N_p
        return flops
        
    def query(self, channel: int, lag: int) -> Tuple[float, bool, str, float, int]:
        if lag < 1 or lag > self.L_max:
            return 0.0, False, "UNAVAILABLE", 0.0, 1
        # Reconstruct via Legendre basis at normalized coordinate u = lag / L_max
        u = float(lag) / float(self.L_max)
        # Evaluate Legendre polynomials P_n(2u - 1)
        p_eval = np.zeros(self.N_p, dtype=np.float32)
        z = 2.0 * u - 1.0
        p_eval[0] = 1.0
        if self.N_p > 1:
            p_eval[1] = z
        for n in range(1, self.N_p - 1):
            p_eval[n + 1] = ((2 * n + 1) * z * p_eval[n] - n * p_eval[n - 1]) / (n + 1)
        # Apply orthonormal normalization sqrt((2n + 1) / 2)
        basis = p_eval * np.sqrt((2 * np.arange(self.N_p) + 1) / 2.0)
        val = float(np.dot(self.state[channel], basis))
        flops = 3 * self.N_p + 2 * self.N_p
        return val, True, "APPROXIMATE_POINT_LOOKUP", 0.15, flops
        
    def get_memory_breakdown(self) -> Dict[str, int]:
        # D * N_p * 4 = 5 * 6 * 4 = 120 bytes state
        raw_bytes = self.D * self.N_p * 4
        return {
            'persistent_bytes': raw_bytes + self._meta_bytes,
            'history_bytes': raw_bytes,
            'metadata_bytes': self._meta_bytes,
            'transient_bytes': 0
        }
