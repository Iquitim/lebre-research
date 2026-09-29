/* lebre052.c — C99 port of the frozen LEBRE v0.52 canonical configuration. Each function mirrors the Python method
 * named in its comment (lebre_v052h.py, change_engine.py, lebre_v052.py Memory / MemoryW). */
#include "lebre052.h"
#include <math.h>
#include <string.h>

#if defined(LB_FLOAT)
#define RSQRT sqrtf
#define RLOG logf
#define REXP expf
#define RFABS fabsf
#define RTINY 1e-37f
#else
#define RSQRT sqrt
#define RLOG log
#define REXP exp
#define RFABS fabs
#define RTINY 1e-300
#endif

static const int BLO[LB_NB] = {1, 2, 4, 8, 16}, BHI[LB_NB] = {1, 3, 7, 15, 31};
static const real POLE[LB_NP] = {(real)0.8, (real)0.95};
static const double GAMMA_C = 0.2951824282491513;
/* canonical constants */
#define MU ((real)0.05)
#define ALPHA 0.05
#define EPS_ADD ((real)0.002)
#define EPS_REM ((real)-0.002)
#define CLIPK ((real)2.0)
#define DECIDE 10
#define NMIN 100
#define TMAX 5000
#define COOLDOWN 2000
#define REMPER 2000
#define LAM ((real)0.99)
#define ETA ((real)0.5)
#define ACOV ((real)0.1)
#define GAMQ ((real)0.1)
#define EVERY 8
#define CLIPX ((real)8.0)
#define WARM 250
#define PEAKU 200
#define SE 4
#define SW ((real)0.02)
#define SQ ((real)15.09)
#define SPQ ((real)6.63)
#define P0 ((real)10.0)
#define MMAX 4
#define FLOORF ((real)0.1)
#define OMARGIN ((real)0.5)
#define ORHO ((real)1e-3)

static int keq(lb_key a, lb_key b) { return a.type == b.type && a.i == b.i && a.lo == b.lo && a.hi == b.hi; }
static lb_key knone(void) { lb_key k = {0, 0, 0, 0}; return k; }
static lb_key kin(int i) { lb_key k = {1, (signed char)i, 0, 0}; return k; }
static lb_key kres(void) { lb_key k = {2, 0, 0, 0}; return k; }
static lb_key unit_of(lb_key k) { return k.type == 3 ? kin(k.i) : k; }

/* H[k][i] = x_{t-k}, ring buffer of L+2 rows */
static real H(const lebre052 *m, int k, int i) { int r = m->hpos - k; if (r < 0) r += LB_L + 2; return m->hbuf[r][i]; }

/* ------------------------------------------------------------------ Memory / MemoryW (lebre_v052.py) */
static real mb(const lb_mem *M, int k) { int r = (M->n - k) % M->Lb; if (r < 0) r += M->Lb; return M->buf[r]; }

static void mem_init(lb_mem *M, int s, int s2) {
    memset(M, 0, sizeof(*M)); M->s = s; M->s2 = s2;
    M->Lb = s ? 2 * s + 2 : 3;
    if (s2 && s2 + 2 > M->Lb) M->Lb = s2 + 2;
    M->nf = 2 + (s ? 3 : 0) + (s2 ? 2 : 0);
}

static real mem_predict(lb_mem *M) {
    if (M->n < M->Lb) { M->phi_ok = 0; return M->n ? mb(M, 1) : 0; }
    real last = mb(M, 1); int j = 0;
    M->phi[j++] = M->mew_ok ? M->mew - last : 0;
    M->phi[j++] = last - mb(M, 2);
    if (M->s) { M->phi[j++] = mb(M, M->s) - last; M->phi[j++] = mb(M, M->s - 1) - mb(M, M->s); M->phi[j++] = M->G[M->n % M->s]; }
    if (M->s2) { M->phi[j++] = mb(M, M->s2) - last; M->phi[j++] = mb(M, M->s2 - 1) - mb(M, M->s2); }
    M->phi_ok = 1; real f = last; for (int q = 0; q < M->nf; q++) f += M->w[q] * M->phi[q];
    return f;
}

static void mem_update(lb_mem *M, real y, int y_ok, real yhat, int learn) {
    if (!y_ok || !isfinite(y)) { y = yhat; learn = 0; }
    if (learn && M->phi_ok) {
        real pp = 0; for (int q = 0; q < M->nf; q++) pp += M->phi[q] * M->phi[q];
        if (!M->ppe_ok) { M->pp_ema = pp; M->ppe_ok = 1; } else M->pp_ema += (real)0.01 * (pp - M->pp_ema);
        if (!M->y2_ok) { M->y2 = y * y; M->y2_ok = 1; } else M->y2 += (real)1e-4 * (y * y - M->y2);
        real den = pp + (real)1e-3 * M->pp_ema + (real)1e-4 * M->y2;
        if (den > 0) { real g = (real)0.05 * (y - yhat) / den; for (int q = 0; q < M->nf; q++) M->w[q] += g * M->phi[q]; }
    }
    if (learn && M->s && M->n >= 1) { int ph = M->n % M->s; M->G[ph] += (real)0.1 * ((y - mb(M, 1)) - M->G[ph]); }
    if (learn) { if (!M->mew_ok) { M->mew = y; M->mew_ok = 1; } else M->mew += (real)0.01 * (y - M->mew); }
    M->buf[M->n % M->Lb] = y; M->n++;
}

/* ------------------------------------------------------------------ small tables */
static long lt_get(const lb_key *ks, const long *ts, int n, lb_key k) { for (int j = 0; j < n; j++) if (keq(ks[j], k)) return ts[j]; return -1000000000L; }
static void lt_set(lebre052 *m, lb_key *ks, long *ts, int *n, lb_key k, long t) {
    for (int j = 0; j < *n; j++) if (keq(ks[j], k)) { ts[j] = t; return; }
    if (*n >= LB_LTMAX) { m->overflow |= 1; return; }
    ks[*n] = k; ts[*n] = t; (*n)++;
}

static int act_find(const lebre052 *m, lb_key u) { for (int j = 0; j < m->nact; j++) if (keq(m->act[j].unit, u)) return j; return -1; }

/* segment sums (_track, _mean, _retrack) */
static int trk_find(const lebre052 *m, int i, int lo, int hi) {
    for (int j = 0; j < m->ntrk; j++) if (m->trk_i[j] == i && m->trk_lo[j] == lo && m->trk_hi[j] == hi) return j;
    return -1;
}
static real hsum(const lebre052 *m, int i, int lo, int hi) { real s = 0; for (int k = lo; k <= hi; k++) s += H(m, k, i); return s; }
static real seg_mean(const lebre052 *m, int i, int lo, int hi) {
    int j = trk_find(m, i, lo, hi);
    if (j >= 0) return m->trk_sum[j] / (real)(hi - lo + 1);
    return hsum(m, i, lo, hi) / (real)(hi - lo + 1);
}
static void retrack(lebre052 *m) {       /* lazy halves: keep exactly the active segments */
    int need_i[LB_TRKMAX], need_lo[LB_TRKMAX], need_hi[LB_TRKMAX], nn = 0;
    for (int a = 0; a < m->nact; a++) if (m->act[a].unit.type == 1)
        for (int q = 0; q < m->act[a].nseg; q++) {
            int i = m->act[a].unit.i, lo = m->act[a].lo[q], hi = m->act[a].hi[q], dup = 0;
            for (int z = 0; z < nn; z++) if (need_i[z] == i && need_lo[z] == lo && need_hi[z] == hi) dup = 1;
            if (!dup) { if (nn >= LB_TRKMAX) { m->overflow |= 2; continue; } need_i[nn] = i; need_lo[nn] = lo; need_hi[nn] = hi; nn++; }
        }
    /* new table: keep running sums of segments already tracked; initialise new ones from the history */
    signed char ti[LB_TRKMAX], tlo[LB_TRKMAX], thi[LB_TRKMAX]; real ts[LB_TRKMAX];
    for (int z = 0; z < nn; z++) {
        int j = trk_find(m, need_i[z], need_lo[z], need_hi[z]);
        ti[z] = (signed char)need_i[z]; tlo[z] = (signed char)need_lo[z]; thi[z] = (signed char)need_hi[z];
        ts[z] = j >= 0 ? m->trk_sum[j] : hsum(m, need_i[z], need_lo[z], need_hi[z]);
    }
    for (int z = 0; z < nn; z++) { m->trk_i[z] = ti[z]; m->trk_lo[z] = tlo[z]; m->trk_hi[z] = thi[z]; m->trk_sum[z] = ts[z]; }
    m->ntrk = nn;
}

/* ------------------------------------------------------------------ features */
static int block(const lebre052 *m, lb_key u, real *out) {     /* block(unit) */
    if (u.type == 1) {
        int a = act_find(m, u);
        if (a < 0) { for (int b = 0; b < LB_NB; b++) out[b] = m->bs[b][u.i] / (real)(BHI[b] - BLO[b] + 1); return LB_NB; }
        for (int q = 0; q < m->act[a].nseg; q++) out[q] = seg_mean(m, u.i, m->act[a].lo[q], m->act[a].hi[q]);
        return m->act[a].nseg;
    }
    out[0] = m->r[0]; out[1] = m->r[1]; return LB_NP;
}
static void halves(int lo, int hi, int *l0, int *l1, int *r0, int *r1) { int mid = (lo + hi) / 2; *l0 = lo; *l1 = mid; *r0 = mid + 1; *r1 = hi; }

static int cfeat(const lebre052 *m, const lb_ex *ex, real *f) {  /* _cf(ex) */
    lb_key k = ex->add;
    if (k.type == 3) { int l0, l1, r0, r1; halves(k.lo, k.hi, &l0, &l1, &r0, &r1); f[0] = seg_mean(m, k.i, l0, l1); f[1] = seg_mean(m, k.i, r0, r1); return 2; }
    int n = block(m, k, f);
    if (k.type == 1) { if (ex->kstar) f[n++] = H(m, ex->kstar, k.i); f[n++] = H(m, 0, k.i); }
    return n;
}
static real seg_contrib(const lebre052 *m, lb_key k) {          /* _seg_contrib */
    int a = act_find(m, kin(k.i));
    for (int q = 0; q < m->act[a].nseg; q++) if (m->act[a].lo[q] == k.lo && m->act[a].hi[q] == k.hi)
        return m->act[a].w[q] * seg_mean(m, k.i, k.lo, k.hi);
    return 0;
}
static real a_of(const lebre052 *m, int i) {                     /* _a() */
    real c0 = m->a_c0[i] > (real)1e-6 ? m->a_c0[i] : (real)1e-6, a = m->a_c1[i] / c0;
    return a < (real)-0.999 ? (real)-0.999 : (a > (real)0.999 ? (real)0.999 : a);
}

/* split_keys() in the Python iteration order */
static int split_keys(const lebre052 *m, lb_key *out) {
    int n = 0;
    for (int a = 0; a < m->nact; a++) if (m->act[a].unit.type == 1)
        for (int q = 0; q < m->act[a].nseg; q++) if (m->act[a].hi[q] > m->act[a].lo[q]) {
            lb_key k = {3, m->act[a].unit.i, m->act[a].lo[q], m->act[a].hi[q]}; out[n++] = k;
        }
    return n;
}

/* ------------------------------------------------------------------ change engine (change_engine.py) */
static void hyp_init(lb_hyp *h, real eps, double alpha_level, int idx) {
    memset(h, 0, sizeof(*h)); h->used = 1; h->eps = eps; h->c = (real)1.0 + (eps > 0 ? eps : 0);
    h->log_thr = (real)log(1.0 / alpha_level); h->idx = idx;
    for (int k = 0; k < 8; k++) {                       /* mixture grid, fixed per hypothesis (same values as before) */
        real lam = (real)(0.9 * pow(2.0, -k)) / h->c, cl = h->c * lam;
        h->lam[k] = lam; h->psi[k] = (-RLOG((real)1 - cl) - cl) / (h->c * h->c);
    }
}
static void hyp_observe(lb_hyp *h, real d) {                    /* psiE1 observe */
    real gam = h->mean; if (gam > 0) gam = 0; if (gam < -h->c) gam = -h->c;
    h->S += d; h->V += (d - gam) * (d - gam); h->n++;
    h->mean += (d - h->mean) / (real)h->n;
}
static real hyp_log_e(const lb_hyp *h) {                        /* _log_mix */
    real a[8], mx = -INFINITY;
    for (int k = 0; k < 8; k++) { a[k] = h->lam[k] * h->S - h->psi[k] * h->V; if (a[k] > mx) mx = a[k]; }
    real s = 0; for (int k = 0; k < 8; k++) s += REXP(a[k] - mx);
    return mx + RLOG(s / (real)8);
}
static int hypothesis(lebre052 *m, int dir, lb_key key, real eps) {
    for (int j = 0; j < LB_HYPMAX; j++) if (m->hyp[j].used && m->hyp[j].dir == dir && keq(m->hyp[j].key, key)) return j;
    int P = 2 * (m->d + 1); m->n_hyp++;
    double g = m->n_hyp <= P ? 1.0 / (2 * P) : 0.5 * GAMMA_C / ((m->n_hyp - P) * pow(log((double)(m->n_hyp - P) + 1), 2));
    double al = ALPHA * g * (m->n_accepted + 1); if (al > 0.5) al = 0.5;
    for (int j = 0; j < LB_HYPMAX; j++) if (!m->hyp[j].used) { hyp_init(&m->hyp[j], eps, al, m->n_hyp); m->hyp[j].dir = dir; m->hyp[j].key = key; return j; }
    m->overflow |= 4; return 0;
}

/* ------------------------------------------------------------------ lifecycle */
static void open_ex(lebre052 *m, int kind, lb_key add, lb_key rem) {    /* _open */
    lb_ex *ex = &m->slot[m->nslot++]; memset(ex, 0, sizeof(*ex));
    ex->kind = kind; ex->add = add; ex->rem = rem; ex->t0 = m->t;
    int dir = kind == 2 ? 1 : 0; lb_key hk = kind == 2 ? rem : add;
    real eps = kind == 2 ? EPS_REM : EPS_ADD;
    ex->hyp = hypothesis(m, dir, hk, eps); ex->eps = m->hyp[ex->hyp].eps; m->k_started++;
    if (add.type) {
        real f[LB_NW + LB_SEGMAX]; lb_ex tmp = *ex; tmp.kstar = 0; ex->nw = cfeat(m, &tmp, f);
        for (int q = 0; q < ex->nw; q++) { ex->w[q] = 0; for (int z = 0; z < ex->nw; z++) ex->P[q][z] = q == z ? P0 : 0; }
        if (kind == 3) { int a = act_find(m, kin(add.i));
            for (int q = 0; q < m->act[a].nseg; q++) if (m->act[a].lo[q] == add.lo && m->act[a].hi[q] == add.hi) { ex->w[0] = ex->w[1] = m->act[a].w[q]; break; } }
        lt_set(m, m->lt_key, m->lt_t, &m->nlt, add, m->t);
    }
    if (rem.type) lt_set(m, m->lt_key, m->lt_t, &m->nlt, rem, m->t);
}

static void log_event(lebre052 *m, int kind, lb_key add, lb_key rem) {
    if (m->nev >= LB_EVMAX) { m->overflow |= 8; return; }
    m->ev_t[m->nev] = m->t; m->ev_kind[m->nev] = (signed char)kind; m->ev_add[m->nev] = add; m->ev_rem[m->nev] = rem; m->nev++;
}

static void accept(lebre052 *m, lb_ex *ex) {                     /* _accept */
    if (ex->kind == 3) {
        int a = act_find(m, kin(ex->add.i)); lb_act *A = &m->act[a];
        int j = 0; for (; j < A->nseg; j++) if (A->lo[j] == ex->add.lo && A->hi[j] == ex->add.hi) break;
        int l0, l1, r0, r1; halves(ex->add.lo, ex->add.hi, &l0, &l1, &r0, &r1);
        signed char lo[LB_SEGMAX + 1], hi[LB_SEGMAX + 1]; real w[LB_SEGMAX + 1]; int n = 0;
        for (int q = 0; q < A->nseg; q++) {
            if (q == j) { lo[n] = (signed char)l0; hi[n] = (signed char)l1; w[n++] = ex->w[0]; lo[n] = (signed char)r0; hi[n] = (signed char)r1; w[n++] = ex->w[1]; }
            else { lo[n] = A->lo[q]; hi[n] = A->hi[q]; w[n++] = A->w[q]; }
        }
        int nm = 0;                                              /* merge duplicate segments (first-occurrence order) */
        for (int q = 0; q < n; q++) {
            int f = -1; for (int z = 0; z < nm; z++) if (A->lo[z] == lo[q] && A->hi[z] == hi[q]) f = z;
            if (f >= 0) A->w[f] += w[q]; else { if (nm >= LB_SEGMAX) { m->overflow |= 16; break; } A->lo[nm] = lo[q]; A->hi[nm] = hi[q]; A->w[nm] = w[q]; nm++; }
        }
        A->nseg = A->nw = nm;
    } else {
        if (ex->rem.type) { int a = act_find(m, ex->rem);
            if (a >= 0) { for (int z = a; z < m->nact - 1; z++) m->act[z] = m->act[z + 1]; m->nact--; } }
        if (ex->add.type) {
            if (m->nact >= LB_ACTMAX) { m->overflow |= 32; }
            else {
                lb_act *A = &m->act[m->nact++]; memset(A, 0, sizeof(*A)); A->used = 1; A->unit = ex->add;
                if (ex->add.type == 1) {
                    for (int b = 0; b < LB_NB; b++) { A->lo[b] = (signed char)BLO[b]; A->hi[b] = (signed char)BHI[b]; }
                    A->nseg = LB_NB; if (ex->kstar) { A->lo[A->nseg] = A->hi[A->nseg] = (signed char)ex->kstar; A->nseg++; }
                    for (int q = 0; q < ex->nw - 1; q++) A->w[q] = ex->w[q];
                    A->nw = ex->nw - 1; m->base[1 + ex->add.i] += ex->w[ex->nw - 1];
                } else { A->nseg = 0; A->nw = LB_NP; A->w[0] = ex->w[0]; A->w[1] = ex->w[1]; }
            }
        }
    }
    m->n_accepted++; m->hyp[ex->hyp].used = 0;                  /* engine.consume */
    retrack(m);
    log_event(m, ex->kind, ex->add, ex->rem);
}

static real screen_stat(const lebre052 *m, lb_key k) {         /* screen_stat */
    real kk = SW / ((real)2 - SW);
    if (k.type == 3) {
        for (int j = 0; j < m->nsp; j++) if (keq(m->sp_key[j], k)) return m->sp[j][0] * m->sp[j][0] / (m->sp[j][1] * m->sp[j][2] + (real)1e-12) / kk;
        return 0;
    }
    real s = 0;
    if (k.type == 1) { for (int b = 0; b < LB_NB; b++) s += m->sc_xy[b][k.i] * m->sc_xy[b][k.i] / (m->sc_xx[b][k.i] * m->sc_yy[k.i] + (real)1e-12); }
    else { for (int p = 0; p < LB_NP; p++) s += m->sr_xy[p] * m->sr_xy[p] / (m->sr_xx[p] * m->sr_yy + (real)1e-12); }
    return s / kk;
}

static int busy_has(const lb_key *busy, int nb, lb_key u) { for (int j = 0; j < nb; j++) if (keq(busy[j], u)) return 1; return 0; }

static void fill(lebre052 *m) {                                 /* _fill */
    lb_key busy[8]; int nb = 0;
    for (int s = 0; s < m->nslot; s++) { if (m->slot[s].add.type) busy[nb++] = unit_of(m->slot[s].add); if (m->slot[s].rem.type) busy[nb++] = unit_of(m->slot[s].rem); }
    while (m->nslot < 2) {
        int due = -1;
        for (int a = 0; a < m->nact; a++) { lb_key u = m->act[a].unit;
            if (!busy_has(busy, nb, u) && m->t - lt_get(m->lr_key, m->lr_t, m->nlr, u) >= REMPER && m->t - lt_get(m->lt_key, m->lt_t, m->nlt, u) >= NMIN) { due = a; break; } }
        if (due >= 0) { lb_key u = m->act[due].unit; lt_set(m, m->lr_key, m->lr_t, &m->nlr, u, m->t); open_ex(m, 2, knone(), u); busy[nb++] = u; continue; }
        int warming = 0; for (int s = 0; s < m->nslot; s++) if (m->slot[s].add.type && m->slot[s].k <= WARM) warming = 1;
        if (warming) break;
        int have = 0; real best_r = 0; int best_t = 0; lb_key best_k = knone();
        /* pool of units, in self.units order: inputs 0..d-1 then the residual unit; max keeps the first maximum */
        lb_key cu = knone(); real cs = -INFINITY; int any = 0;
        for (int u = 0; u <= m->d; u++) { lb_key k = u < m->d ? kin(u) : kres();
            if (act_find(m, k) >= 0 || busy_has(busy, nb, k) || m->t - lt_get(m->lt_key, m->lt_t, m->nlt, k) < COOLDOWN) continue;
            real st = screen_stat(m, k); if (!any || st > cs) { cs = st; cu = k; any = 1; } }
        if (any && cs >= SQ) { have = 1; best_r = cs / SQ; best_t = 1; best_k = cu; }
        lb_key sk[LB_SPMAX]; int ns = split_keys(m, sk); lb_key cs2 = knone(); real ss = -INFINITY; int any2 = 0;
        for (int j = 0; j < ns; j++) { if (busy_has(busy, nb, unit_of(sk[j])) || m->t - lt_get(m->lt_key, m->lt_t, m->nlt, sk[j]) < COOLDOWN) continue;
            real st = screen_stat(m, sk[j]); if (!any2 || st > ss) { ss = st; cs2 = sk[j]; any2 = 1; } }
        if (any2 && ss >= SPQ) { real r = ss / SPQ; if (!have || r > best_r) { have = 1; best_r = r; best_t = 3; best_k = cs2; } }
        if (!have) break;
        if (best_t == 3) open_ex(m, 3, best_k, knone());
        else if (m->nact < MMAX) open_ex(m, 0, best_k, knone());
        else {
            int ai = -1; real bc = INFINITY;
            for (int a = 0; a < m->nact; a++) { if (busy_has(busy, nb, m->act[a].unit)) continue;
                real c = m->act[a].has_ce ? m->act[a].ce : INFINITY; if (ai < 0 || c < bc) { bc = c; ai = a; } }
            if (ai < 0) break;
            lb_key a = m->act[ai].unit; open_ex(m, 1, best_k, a); busy[nb++] = a;
        }
        busy[nb++] = unit_of(best_k);
    }
}

static void decide(lebre052 *m) {                               /* _decide + engine.review */
    lb_ex keep[2]; int nk = 0; int changed_any = 0; lb_key ch[8]; int nch = 0;
    lb_ex done[2]; int dec[2], nd = 0;
    for (int s = 0; s < m->nslot; s++) {
        lb_ex *ex = &m->slot[s]; lb_hyp *h = &m->hyp[ex->hyp]; real le = hyp_log_e(h);
        if (le >= h->log_thr) { done[nd] = *ex; dec[nd++] = 1; }
        else if (ex->n >= TMAX || (ex->n >= NMIN && ex->S <= 0)) { done[nd] = *ex; dec[nd++] = 0; }
        else keep[nk++] = *ex;
    }
    for (int s = 0; s < nk; s++) m->slot[s] = keep[s];
    m->nslot = nk;
    for (int j = 0; j < nd; j++) {
        if (dec[j]) { accept(m, &done[j]); changed_any = 1;
            if (done[j].add.type) ch[nch++] = unit_of(done[j].add);
            if (done[j].rem.type) ch[nch++] = unit_of(done[j].rem); }
    }
    if (changed_any) {
        int n = 0;
        for (int s = 0; s < m->nslot; s++) { lb_ex *ex = &m->slot[s]; int hit = 0;
            if (ex->add.type && busy_has(ch, nch, unit_of(ex->add))) hit = 1;
            if (ex->rem.type && busy_has(ch, nch, unit_of(ex->rem))) hit = 1;
            if (!hit) m->slot[n++] = *ex; }
        m->nslot = n;
        retrack(m);
        lb_key sk[LB_SPMAX]; int ns = split_keys(m, sk), n2 = 0;          /* keep split statistics of current split keys */
        for (int j = 0; j < m->nsp; j++) { if (busy_has(sk, ns, m->sp_key[j])) { m->sp_key[n2] = m->sp_key[j];
            m->sp[n2][0] = m->sp[j][0]; m->sp[n2][1] = m->sp[j][1]; m->sp[n2][2] = m->sp[j][2]; n2++; } }
        m->nsp = n2;
    }
    fill(m);
}

/* ------------------------------------------------------------------ peak statistic and screen */
static void peak_stats(lebre052 *m, lb_ex *ex, real rr) {     /* _peak_stats (peak_persist, peak_split) */
    lb_hyp *h = &m->hyp[ex->hyp]; int i = ex->add.i; real a = a_of(m, i);
    real pr = rr - a * ex->rprev; ex->rprev = rr;
    if (!ex->peak_init) { if (!h->has_peak) { for (int j = 0; j < LB_L; j++) { h->cxy[j] = 0; h->cxx[j] = (real)1e-9; } h->has_peak = 1; } ex->peak_init = 1; }
    for (int j = 0; j < LB_L; j++) if ((j + ex->k) % 2 == 0) {
        real u = H(m, j + 1, i) - a * H(m, j + 2, i); h->cxy[j] += pr * u; h->cxx[j] += u * u; }
    if (ex->k == PEAKU) {
        int kb = 0; real bv = -INFINITY;
        for (int j = 0; j < LB_L; j++) { real v = h->cxy[j] * h->cxy[j] / h->cxx[j]; if (v > bv) { bv = v; kb = j; } }
        int k = kb + 1;
        if (k > 1) {                                             /* insert the peak before the current-value term */
            int n = ex->nw; ex->kstar = k;
            ex->w[n] = ex->w[n - 1]; ex->w[n - 1] = 0;
            real Pn[LB_NW][LB_NW];
            for (int q = 0; q <= n; q++) for (int z = 0; z <= n; z++) {
                int oq = q < n - 1 ? q : (q == n - 1 ? -1 : n - 1), oz = z < n - 1 ? z : (z == n - 1 ? -1 : n - 1);
                Pn[q][z] = (oq < 0 || oz < 0) ? ((oq < 0 && oz < 0) ? P0 : 0) : ex->P[oq][oz]; }
            for (int q = 0; q <= n; q++) for (int z = 0; z <= n; z++) ex->P[q][z] = Pn[q][z];
            ex->nw = n + 1;
        }
    }
}

static void screen_spread(lebre052 *m, real res) {              /* _screen_spread */
    long t = m->t; real ra = (real)1e-3 * SE;
    for (int i = 0; i < m->d; i++) {
        if ((t + i) % SE) continue;
        real x = H(m, 0, i), x1 = H(m, 1, i);
        m->a_c0[i] += ra * (x * x - m->a_c0[i]); m->a_c1[i] += ra * (x * x1 - m->a_c1[i]);
        if (act_find(m, kin(i)) >= 0) continue;
        real a = a_of(m, i), pres = res - a * m->res_prev;
        for (int b = 0; b < LB_NB; b++) {
            real ub = (m->bs[b][i] - a * (m->bs[b][i] - H(m, BLO[b], i) + H(m, BHI[b] + 1, i))) / (real)(BHI[b] - BLO[b] + 1);
            m->sc_xy[b][i] += SW * (pres * ub - m->sc_xy[b][i]); m->sc_xx[b][i] += SW * (ub * ub - m->sc_xx[b][i]);
        }
        m->sc_yy[i] += SW * (pres * pres - m->sc_yy[i]);
    }
    if (t % SE == m->d % SE) {
        for (int p = 0; p < LB_NP; p++) { m->sr_xy[p] += SW * (res * m->r[p] - m->sr_xy[p]); m->sr_xx[p] += SW * (m->r[p] * m->r[p] - m->sr_xx[p]); }
        m->sr_yy += SW * (res * res - m->sr_yy);
    }
    if (t % SE == (m->d + 1) % SE) {
        real gw = (real)1e-3 * SE, xc[LB_DMAX];
        for (int i = 0; i < m->d; i++) { m->g_m[i] += gw * (H(m, 0, i) - m->g_m[i]); xc[i] = H(m, 0, i) - m->g_m[i]; }
        for (int i = 0; i < m->d; i++) for (int j = 0; j < m->d; j++) m->g_c[i][j] += gw * (xc[i] * xc[j] - m->g_c[i][j]);
    }
    lb_key sk[LB_SPMAX]; int ns = split_keys(m, sk);
    for (int j = 0; j < ns; j++) {
        if ((t + j) % SE) continue;
        int l0, l1, r0, r1; halves(sk[j].lo, sk[j].hi, &l0, &l1, &r0, &r1);
        real dv = seg_mean(m, sk[j].i, l0, l1) - seg_mean(m, sk[j].i, r0, r1);
        int f = -1; for (int z = 0; z < m->nsp; z++) if (keq(m->sp_key[z], sk[j])) f = z;
        if (f < 0) { if (m->nsp >= LB_SPMAX) { m->overflow |= 64; continue; } f = m->nsp++; m->sp_key[f] = sk[j]; m->sp[f][0] = 0; m->sp[f][1] = (real)1e-3; m->sp[f][2] = 1; }
        m->sp[f][0] += SW * (res * dv - m->sp[f][0]); m->sp[f][1] += SW * (dv * dv - m->sp[f][1]); m->sp[f][2] += SW * (res * res - m->sp[f][2]);
    }
}

/* ------------------------------------------------------------------ public */
void lebre052_init(lebre052 *m, int dx, int season, int season2) {
    memset(m, 0, sizeof(*m));
    m->dx = dx; m->d = dx + 1; m->yv = 1; m->quar_until = -1;
    for (int i = 0; i < m->d; i++) { m->a_c0[i] = 1; m->sc_yy[i] = 1; m->g_c[i][i] = 1; for (int b = 0; b < LB_NB; b++) m->sc_xx[b][i] = (real)1e-3; }
    for (int p = 0; p < LB_NP; p++) m->sr_xx[p] = (real)1e-3;
    m->sr_yy = 1; m->sig = 1; m->sigr = 1; m->wS = (real)0.5;
    mem_init(&m->M, season, season2);
}

real lebre052_step(lebre052 *m, const real *xin, real y, int y_ok, int quarantine) {
    real x[LB_DMAX];
    for (int i = 0; i < m->dx; i++) x[i] = xin[i];
    { real v = m->ylast; x[m->dx] = (v - m->ym) / RSQRT(m->yv + (real)1e-6);        /* own past, standardised causally */
      real dlt = v - m->ym; m->ym += (real)1e-4 * dlt;
      real yv = ((real)1 - (real)1e-4) * m->yv + (real)1e-4 * (v - m->ym) * dlt; m->yv = yv > (real)1e-4 ? yv : (real)1e-4; }
    int out = 0;
    for (int i = 0; i < m->d; i++) { if (isnan(x[i])) x[i] = 0; if (RFABS(x[i]) > CLIPX) out = 1; }
    if (out) m->quar_until = m->t + LB_L;
    for (int i = 0; i < m->d; i++) x[i] = x[i] > CLIPX ? CLIPX : (x[i] < -CLIPX ? -CLIPX : x[i]);
    /* _shift */
    m->hpos = (m->hpos + 1) % (LB_L + 2); for (int i = 0; i < m->d; i++) m->hbuf[m->hpos][i] = x[i];
    for (int b = 0; b < LB_NB; b++) for (int i = 0; i < m->d; i++) m->bs[b][i] += H(m, BLO[b], i) - H(m, BHI[b] + 1, i);
    for (int j = 0; j < m->ntrk; j++) m->trk_sum[j] += H(m, m->trk_lo[j], m->trk_i[j]) - H(m, m->trk_hi[j] + 1, m->trk_i[j]);
    real mm = mem_predict(&m->M);
    /* _struct_pred */
    real xb[LB_DMAX + 1]; xb[0] = 1; for (int i = 0; i < m->d; i++) xb[1 + i] = x[i];
    real s = 0; for (int i = 0; i <= m->d; i++) s += m->base[i] * xb[i];
    real blk[LB_ACTMAX][LB_SEGMAX]; int nbk[LB_ACTMAX];
    for (int a = 0; a < m->nact; a++) { nbk[a] = block(m, m->act[a].unit, blk[a]); real du = 0; for (int q = 0; q < nbk[a]; q++) du += m->act[a].w[q] * blk[a][q]; s += du; }
    real f = mm + m->wS * (s - mm);
    if (m->env_n >= 50) {
        real w_ = OMARGIN * (m->env_hi - m->env_lo), fc;
        if (isfinite(f)) { fc = f < m->env_lo - w_ ? m->env_lo - w_ : f; fc = fc > m->env_hi + w_ ? m->env_hi + w_ : fc; } else fc = m->last_obs;
        m->n_clipped += fc != f; f = fc;
    }
    real ref = s, outs[2], back[2];
    for (int k = 0; k < m->nslot; k++) {
        lb_ex *ex = &m->slot[k]; real fx[LB_NW]; int n;
        if (ex->kind == 3) { real c = seg_contrib(m, ex->add); n = cfeat(m, ex, fx); real a = 0; for (int q = 0; q < n; q++) a += ex->w[q] * fx[q];
            outs[k] = ref - c + a; back[k] = c; continue; }
        real a = 0, r = 0;
        if (ex->add.type) { n = cfeat(m, ex, fx); for (int q = 0; q < n; q++) a += ex->w[q] * fx[q]; }
        if (ex->rem.type) { int ai = act_find(m, ex->rem); real b[LB_SEGMAX]; int nbq = block(m, ex->rem, b); for (int q = 0; q < nbq; q++) r += m->act[ai].w[q] * b[q]; }
        outs[k] = ref + a - r; back[k] = r;
    }
    int mem_learn = y_ok && !quarantine, learn = mem_learn && !(m->t <= m->quar_until);
    real u_ = 0;
    if (y_ok) {
        real e = y - f, er = y - ref;
        if (!m->e2r_ok) { m->e2r = er * er; m->e2r_ok = 1; } else m->e2r += ((real)1 - LAM) * (er * er - m->e2r);
        if (!m->ysm_ok) { m->y_sm = y; m->n_y = 0; m->ysm_ok = 1; }
        m->n_y++; real ry = (real)1 / (real)m->n_y; if (ry < (real)1e-4) ry = (real)1e-4;
        real dy = y - m->y_sm; m->y_sm += ry * dy; m->y_sv += ry * (dy * (y - m->y_sm) - m->y_sv);
        real floor_ = m->t >= 200 ? FLOORF * RSQRT(m->y_sv > 0 ? m->y_sv : 0) : 0;
        real B = CLIPK * (m->sigr > floor_ ? m->sigr : floor_), B2 = B * B;
        real lf = er * er / B2; if (lf > 1) lf = 1;
        real res = y - s;
        if (learn) {
            for (int k = 0; k < m->nslot; k++) {
                lb_ex *ex = &m->slot[k]; ex->k++;
                if (ex->k > WARM || !ex->add.type) {
                    real lg = (y - outs[k]) * (y - outs[k]) / B2; if (lg > 1) lg = 1;
                    real dd = lf - lg - ex->eps; hyp_observe(&m->hyp[ex->hyp], dd); ex->S += dd; ex->n++;
                }
                if (ex->add.type) {
                    real rr = res + back[k];
                    if (ex->add.type == 1 && ex->k <= PEAKU) peak_stats(m, ex, rr);
                    real fx[LB_NW], Pf[LB_NW], kg[LB_NW]; int n = cfeat(m, ex, fx);
                    real den = 1, pred = 0;
                    for (int q = 0; q < n; q++) { Pf[q] = 0; for (int z = 0; z < n; z++) Pf[q] += ex->P[q][z] * fx[z]; den += fx[q] * Pf[q]; pred += ex->w[q] * fx[q]; }
                    for (int q = 0; q < n; q++) kg[q] = Pf[q] / den;
                    real err = rr - pred;
                    for (int q = 0; q < n; q++) ex->w[q] += kg[q] * err;
                    for (int q = 0; q < n; q++) for (int z = 0; z < n; z++) ex->P[q][z] -= kg[q] * Pf[z];
                }
            }
            /* live NLMS on base + active blocks */
            real den = 0; for (int i = 0; i <= m->d; i++) den += xb[i] * xb[i];
            for (int a = 0; a < m->nact; a++) for (int q = 0; q < nbk[a]; q++) den += blk[a][q] * blk[a][q];
            den += (real)1e-6;
            real g_ = MU * res / den;
            for (int i = 0; i <= m->d; i++) m->base[i] += g_ * xb[i];
            for (int a = 0; a < m->nact; a++) { real c = 0;
                for (int q = 0; q < nbk[a]; q++) { m->act[a].w[q] += g_ * blk[a][q]; c += m->act[a].w[q] * blk[a][q]; }
                c = RFABS(c); if (!m->act[a].has_ce) { m->act[a].ce = c; m->act[a].has_ce = 1; } else m->act[a].ce += (real)0.01 * (c - m->act[a].ce); }
            screen_spread(m, res);
            m->res_prev = res;
            if (!m->res2_ok) { m->res2 = res * res; m->res2_ok = 1; } else m->res2 += ((real)1 - LAM) * (res * res - m->res2);
        }
        real es = y - s, em = y - mm;
        m->D = LAM * m->D + (es * es - em * em) / (m->sig * m->sig + (real)1e-12);
        if (m->t % EVERY == 0) { real z = ETA * m->D; m->wS = z < 700 ? (real)1 / ((real)1 + REXP(z)) : 0; }
        if (!m->e2_ok) { m->e2 = e * e; m->e2_ok = 1; } else m->e2 += ((real)1 - LAM) * (e * e - m->e2);
        if (!m->qhat_ok) { m->qhat = (real)1.645 * RSQRT(m->e2); m->qhat_ok = 1; }
        int miss = RFABS(e) > m->qhat; m->hits_obs++; m->hits_ok += !miss;
        m->qacc += (real)miss - ACOV;
        if (m->t % EVERY == 0) {
            m->sig = RSQRT(m->e2 > RTINY ? m->e2 : RTINY); m->sigr = RSQRT(m->e2r > RTINY ? m->e2r : RTINY);
            real q = m->qhat + GAMQ * m->sig * m->qacc; m->qhat = q > 0 ? q : 0; m->qacc = 0;
        }
        u_ = e / m->sig;
    }
    if (!y_ok && m->lastobs_ok) mem_update(&m->M, m->last_obs, 1, mm, 0);   /* gap_hold */
    else mem_update(&m->M, y, y_ok, mm, mem_learn);
    if (y_ok) {
        m->last_obs = y; m->lastobs_ok = 1;
        if (!m->env_ok) { m->env_hi = m->env_lo = m->env_m = y; m->env_ok = 1; }
        m->env_n++; real r_ = (real)1 / (real)m->env_n; if (r_ < ORHO) r_ = ORHO;
        m->env_m += r_ * (y - m->env_m);
        real hi = m->env_hi - ORHO * (m->env_hi - m->env_m), lo = m->env_lo - ORHO * (m->env_lo - m->env_m);
        m->env_hi = y > hi ? y : hi; m->env_lo = y < lo ? y : lo;
        m->ylast = y;
    }
    for (int p = 0; p < LB_NP; p++) m->r[p] = POLE[p] * m->r[p] + ((real)1 - POLE[p]) * u_;
    if (m->t % DECIDE == 0 && m->t > 0) decide(m);
    m->t++;
    return f;
}
