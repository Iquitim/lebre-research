/* lebre052.h — C99 port of the FROZEN LEBRE v0.52 canonical configuration (lebre_v052h.LebreV052H with
 * scale_floor=0.1, peak_persist, evidence=psiE1, lazy_halves, screen_skip_active, track_groups, mu=0.05, stagger,
 * screen_spread, peak_split, peak_until=200, chal_warm=250, gap_hold, out_contract; other constructor defaults).
 * Only the canonical path is ported. Dynamic Python containers become fixed-capacity arrays (overflow is flagged).
 * REAL is double (host equivalence of the logic) or float (single precision, the microcontroller build). */
#ifndef LEBRE052_H
#define LEBRE052_H

#ifndef REAL
#define REAL double
#endif
typedef REAL real;

#define LB_DMAX 8          /* inputs including the target's own past */
#define LB_L 31            /* longest lag */
#define LB_NB 5            /* octave bands */
#define LB_NP 2            /* residual poles */
#define LB_UMAX (LB_DMAX + 1)
#define LB_SEGMAX 24
#define LB_ACTMAX 4
#define LB_TRKMAX 96
#define LB_HYPMAX 160
#define LB_SPMAX 96
#define LB_LTMAX 256
#define LB_EVMAX 512
#define LB_NW 8
#define LB_LBMAX 176

typedef struct { signed char type, i, lo, hi; } lb_key;   /* type: 0 none, 1 input unit, 2 residual unit, 3 split */

typedef struct {
    int used; int dir; lb_key key;                          /* dir 0 = "in" (add/swap/split), 1 = "out" (removal) */
    real eps, c, log_thr; real S, V, mean; long n; int idx; real lam[8], psi[8];
    int has_peak; real cxy[LB_L], cxx[LB_L];
} lb_hyp;

typedef struct {
    int kind;                                                /* 0 add, 1 swap, 2 rem, 3 split */
    lb_key add, rem; int hyp; long t0, k, n; real S; real eps;
    int nw; real w[LB_NW]; real P[LB_NW][LB_NW];
    int kstar; real rprev; int peak_init;
} lb_ex;

typedef struct { int used; lb_key unit; int nseg; signed char lo[LB_SEGMAX], hi[LB_SEGMAX]; int nw; real w[LB_SEGMAX];
                 int has_ce; real ce; } lb_act;

typedef struct {
    int s, s2, Lb, n; real buf[LB_LBMAX]; int mew_ok; real mew; real G[24];
    int nf; real w[7], phi[7]; int phi_ok; int ppe_ok; real pp_ema; int y2_ok; real y2;
} lb_mem;

typedef struct {
    int d, dx; long t;                                       /* d = inputs incl. own past; dx = exogenous inputs */
    real ylast, ym, yv; long quar_until;
    real hbuf[LB_L + 2][LB_DMAX]; int hpos;
    real bs[LB_NB][LB_DMAX];
    int ntrk; signed char trk_i[LB_TRKMAX], trk_lo[LB_TRKMAX], trk_hi[LB_TRKMAX]; real trk_sum[LB_TRKMAX];
    real r[LB_NP]; real base[LB_DMAX + 1];
    int nact; lb_act act[LB_ACTMAX];                        /* insertion-ordered active units */
    real a_c0[LB_DMAX], a_c1[LB_DMAX], res_prev;
    real sc_xy[LB_NB][LB_DMAX], sc_xx[LB_NB][LB_DMAX], sc_yy[LB_DMAX];
    real sr_xy[LB_NP], sr_xx[LB_NP], sr_yy;
    int nsp; lb_key sp_key[LB_SPMAX]; real sp[LB_SPMAX][3];
    real g_m[LB_DMAX], g_c[LB_DMAX][LB_DMAX];
    lb_hyp hyp[LB_HYPMAX]; int n_hyp, n_accepted; long k_started;
    int nslot; lb_ex slot[2];
    int nlt; lb_key lt_key[LB_LTMAX]; long lt_t[LB_LTMAX];  /* last_tested */
    int nlr; lb_key lr_key[LB_LTMAX]; long lr_t[LB_LTMAX];  /* last_rem */
    int e2_ok; real e2; real sig; int e2r_ok; real e2r; real sigr; int res2_ok; real res2;
    real D, wS; int qhat_ok; real qhat, qacc; long hits_obs, hits_ok;
    int ysm_ok; real y_sm, y_sv; long n_y;
    int lastobs_ok; real last_obs; int env_ok; real env_hi, env_lo, env_m; long env_n; long n_clipped;
    lb_mem M;
    int overflow;                                            /* capacity exceeded somewhere (should stay 0) */
    int nev; long ev_t[LB_EVMAX]; signed char ev_kind[LB_EVMAX]; lb_key ev_add[LB_EVMAX], ev_rem[LB_EVMAX];
} lebre052;

void lebre052_init(lebre052 *m, int dx, int season, int season2);
real lebre052_step(lebre052 *m, const real *x, real y, int y_ok, int quarantine);

#endif
