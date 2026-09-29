"""ttm_run.py — Tiny Time Mixers (granite-timeseries-ttm-r2, context 512) as small-foundation-model comparators, on the
1000-point protocol of the Chronos comparison (chronos_dev.points: 1000 evenly spaced observed test points).
  TTM_ZS      zero-shot, univariate (target only).
  TTM_FT_EXOG target + inputs as channels (prediction channel 0, exogenous channels 1..d, decoder channel mixing,
              forecast channel mixing with the CURRENT input value x_t as known future exogenous, fcm_context_length 1:
              verified that the first-step forecast depends on x_t and not on later exogenous values). The backbone is
              frozen; decoder and head are fine-tuned on the calibration segment only (first min(15%, 5000) steps;
              at most 2000 windows, MSE on the first step). Defaults: Adam lr 1e-3, 5 epochs (first dev check);
              run(..., lr=1e-4, epochs=30, early_stop=True): early stopping on the last 20% of the calibration windows.
Channels are standardised with the calibration segment's mean and s.d. (past only). FLOPs per forecast measured with
torch.utils.flop_counter."""
import numpy as np
import torch

CTX = 512


def _ffill(a):
    a = a.copy()
    for j in range(a.shape[1]):
        last = np.nan
        for i in range(a.shape[0]):
            if np.isfinite(a[i, j]):
                last = a[i, j]
            else:
                a[i, j] = last
    return np.nan_to_num(a)


def _batch(Z, idx, d_exog):
    """past windows (CTX) ending before t, and future exogenous rows (x_t held) for each t in idx"""
    pad = np.concatenate([np.repeat(Z[:1], CTX, 0), Z])
    pv = np.stack([pad[t:t + CTX] for t in idx]).astype(np.float32)
    fv = np.zeros((len(idx), 96, Z.shape[1]), np.float32)
    if d_exog:
        fv[:, :, 1:] = Z[idx, 1:][:, None, :]
    return torch.tensor(pv), torch.tensor(fv)


def run(X, y, calib_idx, points, seed=0, lr=1e-3, epochs=5, early_stop=False):
    from tsfm_public.toolkit.get_model import get_model
    from torch.utils.flop_counter import FlopCounterMode
    torch.manual_seed(seed)
    d = X.shape[1]
    Z = _ffill(np.column_stack([y, X]).astype(float))
    mu = np.nanmean(np.column_stack([y, X])[calib_idx], 0); sd = np.nanstd(np.column_stack([y, X])[calib_idx], 0)
    sd = np.where(sd > 0, sd, 1.0); Zs = (Z - mu) / sd
    out = {}
    # zero-shot, univariate
    m0 = get_model("ibm-granite/granite-timeseries-ttm-r2", context_length=CTX, prediction_length=96).eval()
    pv, _ = _batch(Zs[:, :1], points, 0)
    with torch.no_grad():
        p = torch.cat([m0(past_values=pv[b:b + 256]).prediction_outputs[:, 0, 0] for b in range(0, len(points), 256)]).numpy()
    with FlopCounterMode(display=False) as fc, torch.no_grad():
        m0(past_values=pv[:1])
    out["TTM_ZS"] = (p * sd[0] + mu[0], float(fc.get_total_flops()))
    # fine-tuned with exogenous channels
    m = get_model("ibm-granite/granite-timeseries-ttm-r2", context_length=CTX, prediction_length=96, num_input_channels=d + 1,
                  prediction_channel_indices=[0], exogenous_channel_indices=list(range(1, d + 1)), decoder_mode="mix_channel",
                  enable_forecast_channel_mixing=True, fcm_prepend_past=True, fcm_context_length=1)
    for n_, p_ in m.named_parameters():
        p_.requires_grad = "backbone" not in n_
    tr = np.array([t for t in calib_idx if np.isfinite(y[t]) and t >= 16])
    rng = np.random.default_rng(seed)
    if len(tr) > 2000:
        tr = np.sort(rng.choice(tr, 2000, replace=False))
    opt = torch.optim.Adam([p_ for p_ in m.parameters() if p_.requires_grad], lr=lr)
    pv, fv = _batch(Zs, tr, d); tgt = torch.tensor(Zs[tr, 0].astype(np.float32))
    ntr = int(0.8 * len(tr)) if early_stop else len(tr)          # early stopping: last 20% of the calibration windows
    best, best_state, bad = float("inf"), None, 0
    for _ in range(epochs):
        m.train(); perm = torch.randperm(ntr)
        for b in range(0, ntr, 64):
            i = perm[b:b + 64]
            pred = m(past_values=pv[i], future_values=fv[i], return_loss=False).prediction_outputs[:, 0, 0]
            loss = ((pred - tgt[i]) ** 2).mean(); opt.zero_grad(); loss.backward(); opt.step()
        if early_stop:
            m.eval()
            with torch.no_grad():
                vl = float(((m(past_values=pv[ntr:], future_values=fv[ntr:], return_loss=False).prediction_outputs[:, 0, 0] - tgt[ntr:]) ** 2).mean())
            if vl < best - 1e-6:
                best, bad = vl, 0; best_state = {k_: v_.clone() for k_, v_ in m.state_dict().items()}
            else:
                bad += 1
                if bad >= 3:
                    break
    if best_state is not None:
        m.load_state_dict(best_state)
    m.eval()
    pv, fv = _batch(Zs, points, d)
    with torch.no_grad():
        p = torch.cat([m(past_values=pv[b:b + 256], future_values=fv[b:b + 256], return_loss=False).prediction_outputs[:, 0, 0]
                       for b in range(0, len(points), 256)]).numpy()
    with FlopCounterMode(display=False) as fc, torch.no_grad():
        m(past_values=pv[:1], future_values=fv[:1], return_loss=False)
    out["TTM_FT_EXOG"] = (p * sd[0] + mu[0], float(fc.get_total_flops()))
    return out
