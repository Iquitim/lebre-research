"""misadj_verify.py — dev-only empirical check of the misadjustment proposition (MISADJUSTMENT_NOTE.md).

Targets with NO structure (y = e Gaussian, or t3/sqrt(3)); real inputs (development river); frozen LebreV052H with the
canonical configuration except the base step mu in {0.1, 0.05, 0.03}. Here f* = E[y_t | past] = 0, so the reference's
estimation error is eta_t = -S_t (S = structural expert, the reference of every experiment).
For each candidate unit u, z_{u,t} = its challenger regressors (5 octave-band means + current value of the input); the
proposition's quantity is
    D_u = mean_t [ (P_u eta)_t^2 / B_t^2 ] - eps,      P_u = least-squares projection of eta on z_u (test region),
the best achievable drift (per sample, unclipped normalised loss) of a challenger built from z_u. Prediction: units with
D_u > 0 can be (and eventually are) accepted although there is no structure; with D_u <= 0 for all units, none should be.
Also reported: empirical excess error M_emp = mean(eta^2)/sigma^2 against the NLMS misadjustment mu/(2-mu).
Seeds 7201-7240 (development)."""
import os
import sys
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
PROTO = os.path.abspath(os.path.join(HERE, "..", "LEBRE-V0.52-PROTO-01"))
sys.path.insert(0, PROTO); sys.path.insert(0, HERE)
import comp_dev as C  # noqa: E402
import heldout2_cfg as CFG  # noqa: E402
import semi_synth6 as S6  # noqa: E402
from lebre_v052h import BANDS  # noqa: E402

EPS = 0.002


def job(a):
    kind, seed, mu = a
    from lebre_v052h import LebreV052H
    X = S6.inputs(); y = S6.generate(kind, seed, X); Xs = C._scaled_inputs(X); T = len(y)
    m = LebreV052H(d=X.shape[1], **dict(CFG.CANONICAL, mu=mu))
    S = np.empty(T); Bv = np.empty(T); Z = np.empty((T, m.d, len(BANDS) + 1))
    orig = m._struct_pred

    def sp(x):
        s, xb = orig(x); sp.s = s; return s, xb
    m._struct_pred = sp
    widths = np.array([hi - lo + 1 for lo, hi in BANDS])[:, None]
    for t in range(T):
        Bv[t] = m.clip_k * m.sigr                                   # scale used by the evidence at step t (before update)
        m.step(Xs[t], float(y[t]))
        S[t] = sp.s
        Z[t, :, :len(BANDS)] = (m.bs / widths).T; Z[t, :, -1] = m.H[0]
    ts = int(0.3 * T); eta = -S[ts:]; B2 = Bv[ts:] ** 2
    out = {"kind": kind, "seed": seed, "mu": mu, "M_emp": float(np.mean(eta ** 2) / np.var(y[ts:])),
           "M_theory": mu / (2 - mu),
           "accepted": str(sorted({str(e[3]) for e in m.events if e[1] == "accepted"}))}
    from change_engine import Hypothesis
    yt = y[ts:]; St = S[ts:]; Bt = np.maximum(np.sqrt(B2), 1e-12)
    for i in range(m.d):
        F = np.column_stack([np.ones(T - ts), Z[ts:, i, :]]); b = np.linalg.lstsq(F, eta, rcond=None)[0]; P = F @ b
        out[f"D_in{i}"] = float(np.mean(P ** 2 / B2)) - EPS
        out[f"rho2_in{i}"] = float(np.sum(P ** 2) / np.sum(eta ** 2))
        # ORACLE: the same one-sided e-process on the REALISED clipped-loss improvement of the best challenger built from
        # z_i (the projection of eta), over the test region; max log-e over time vs the first-hypothesis threshold
        h = Hypothesis(EPS, 0.05 / (2 * len(m.units)), 1, "psiE1"); best = -np.inf
        dd = np.minimum((yt - St) ** 2 / Bt ** 2, 1) - np.minimum((yt - St - P) ** 2 / Bt ** 2, 1) - EPS
        for t_, v in enumerate(dd):
            h.observe(float(v))
            if t_ % 20 == 19:
                best = max(best, h.log_e())
        out[f"orac_in{i}"] = float(best); out["log_thr"] = h.log_thr
    return out


if __name__ == "__main__":
    jobs = [(k, s, mu) for mu in (0.1, 0.05, 0.03) for k, s0 in (("white", 7201), ("heavy", 7221)) for s in range(s0, s0 + 20)]
    with ProcessPoolExecutor(15) as ex:
        R = pd.DataFrame(list(ex.map(job, jobs, chunksize=1)))
    R.to_csv(os.path.join(HERE, "MISADJ_VERIFY2.csv"), index=False)
    d = [c for c in R.columns if c.startswith("D_in")]
    R["D_max"] = R[d].max(axis=1); R["any_acc"] = R.accepted != "[]"
    R["argmax_unit"] = R[d].idxmax(axis=1).str.replace("D_in", "")
    pd.set_option("display.width", 220)
    print(R.groupby("mu")[["M_emp", "M_theory", "D_max"]].agg(["mean", "max"]).round(4))
    print(R.groupby("mu").apply(lambda g: pd.Series({"runs_with_acceptance": int(g.any_acc.sum()), "runs_with_Dmax>0": int((g.D_max > 0).sum()),
                                                     "acc_and_D>0": int((g.any_acc & (g.D_max > 0)).sum()),
                                                     "acc_and_D<=0": int((g.any_acc & (g.D_max <= 0)).sum())})))
    o = [c for c in R.columns if c.startswith("orac_in")]
    R["orac_cross"] = (R[o].max(axis=1) >= R.log_thr); R["orac_unit"] = R[o].idxmax(axis=1).str.replace("orac_in", "")
    print(R.groupby("mu").apply(lambda g: pd.Series({"oracle_crosses": int(g.orac_cross.sum()), "accepted": int(g.any_acc.sum()),
                                                     "acc_and_oracle_crosses": int((g.any_acc & g.orac_cross).sum()),
                                                     "acc_without_oracle_cross": int((g.any_acc & ~g.orac_cross).sum())})))
    print(R[R.any_acc | R.orac_cross][["kind", "seed", "mu", "accepted", "orac_unit", "D_max"] + o].round(2).to_string(index=False))
