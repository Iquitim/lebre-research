"""ultralight.py — ultra-light batch-trained forecasters as budget-class comparators, in the protocol of the SARIMAX-X
comparator: fitted ONLY on the calibration segment (first min(15%, 5000) steps, comp_dev._calib_n), then one-step-ahead
forecasts with FROZEN weights over the whole series (target windows forward-filled causally). Both are univariate by
design (no exogenous inputs).

FITS (Xu, Zeng & Xu, ICLR 2024): instance normalisation, rFFT of the look-back window, low-pass to `cut` frequencies,
complex linear layer to the up-sampled spectrum of length L+1, irFFT; the forecast is the last point.
SparseTSF (Lin et al., ICML 2024): instance normalisation, aggregation convolution (kernel 1 + 2*(w//2)), down-sampling by
the period w, one linear layer shared across phases mapping L/w -> 1 segment; the forecast of the next w steps, of which
the first is y_t. Period w: 8 (ONS 3-h), 24 (BDG2 hourly), 7 (CAMELS daily; weekly, no natural cycle), 1 otherwise.
Look-back L = 96 (FITS) and L = 4*w*ceil(24/w) (SparseTSF, a multiple of w). Adam, lr 1e-3 (FITS 5e-3), 60 epochs,
batch 128, MSE. FLOPs per forecast are measured with torch.utils.flop_counter plus the FFTs (5/2 N log2 N each)."""
import math

import numpy as np
import torch
import torch.nn as nn

torch.set_num_threads(1)


def windows(y, L, idx):
    """past windows of length L ending before each t in idx (forward-filled, left-padded with the first value)"""
    yf = y.copy(); last = np.nan
    for i in range(len(yf)):
        if np.isfinite(yf[i]):
            last = yf[i]
        else:
            yf[i] = last
    first = yf[np.isfinite(yf)][0] if np.isfinite(yf).any() else 0.0
    yf = np.where(np.isfinite(yf), yf, first)
    pad = np.concatenate([np.full(L, yf[0]), yf])
    return np.stack([pad[t:t + L] for t in idx]).astype(np.float32)


class FITS(nn.Module):
    def __init__(self, L=96, cut=24):
        super().__init__()
        self.L, self.cut = L, cut
        self.up = int(math.ceil(cut * (L + 1) / L))
        self.w = nn.Parameter(torch.zeros(cut, self.up, dtype=torch.cfloat))
        with torch.no_grad():
            self.w.real[:, :cut] = torch.eye(cut) * (L + 1) / L

    def forward(self, x):                                   # x: (B, L)
        m = x.mean(1, keepdim=True); s = x.std(1, keepdim=True) + 1e-5; z = (x - m) / s
        F = torch.fft.rfft(z, dim=1)[:, :self.cut]
        G = F @ self.w
        full = torch.zeros(x.shape[0], (self.L + 1) // 2 + 1, dtype=torch.cfloat)
        full[:, :self.up] = G[:, :full.shape[1]]
        out = torch.fft.irfft(full, n=self.L + 1, dim=1)
        return out[:, -1] * s[:, 0] + m[:, 0]


class SparseTSF(nn.Module):
    def __init__(self, L, w):
        super().__init__()
        self.L, self.w = L, w
        k = 1 + 2 * (w // 2)
        self.conv = nn.Conv1d(1, 1, k, padding=k // 2, bias=False)
        self.lin = nn.Linear(L // w, 1, bias=False)

    def forward(self, x):                                   # x: (B, L)
        m = x.mean(1, keepdim=True); z = x - m
        z = self.conv(z[:, None, :])[:, 0] + z
        seg = z.reshape(x.shape[0], self.L // self.w, self.w).transpose(1, 2)   # (B, w, L/w)
        nxt = self.lin(seg)[:, :, 0]                                            # next period, (B, w)
        return nxt[:, 0] + m[:, 0]


def period(task):
    return 8 if task.startswith("ons") else 24 if task.startswith("bdg2") else 7 if task.startswith("camels") else 1


def fit_predict(model, y, calib_idx, L, lr, epochs=60):
    obs = np.array([t for t in calib_idx if np.isfinite(y[t]) and t >= 8])
    Xw = torch.tensor(windows(y, L, obs)); yt = torch.tensor(y[obs].astype(np.float32))
    sc = float(np.nanstd(y[calib_idx])) or 1.0
    opt = torch.optim.Adam(model.parameters(), lr=lr); g = torch.Generator().manual_seed(0)
    for _ in range(epochs):
        perm = torch.randperm(len(obs), generator=g)
        for b in range(0, len(obs), 128):
            i = perm[b:b + 128]
            loss = (((model(Xw[i]) - yt[i]) / sc) ** 2).mean()
            opt.zero_grad(); loss.backward(); opt.step()
    all_idx = np.arange(len(y)); pred = np.empty(len(y), dtype=float)
    with torch.no_grad():
        for b in range(0, len(y), 4096):
            pred[b:b + 4096] = model(torch.tensor(windows(y, L, all_idx[b:b + 4096]))).numpy()
    return pred


def flops(model, L):
    from torch.utils.flop_counter import FlopCounterMode
    with FlopCounterMode(display=False) as fc, torch.no_grad():
        model(torch.randn(1, L))
    extra = 0.0
    if isinstance(model, FITS):
        extra = 2.5 * L * math.log2(L) + 2.5 * (L + 1) * math.log2(L + 1) + 8 * model.cut * model.up   # rFFT, irFFT, complex matmul
    return float(fc.get_total_flops() + extra + 6 * L)                                                # + normalisation


def run(task, y, calib_idx):
    out = {}
    torch.manual_seed(0)
    f = FITS(96, 24); out["FITS"] = (fit_predict(f, y, calib_idx, 96, 5e-3), flops(f, 96), sum(p.numel() for p in f.parameters()) * 2)
    w = period(task); L = 4 * w * int(math.ceil(24 / w))
    torch.manual_seed(0)
    s = SparseTSF(L, w); out["SPARSETSF"] = (fit_predict(s, y, calib_idx, L, 1e-3), flops(s, L), sum(p.numel() for p in s.parameters()))
    return out
