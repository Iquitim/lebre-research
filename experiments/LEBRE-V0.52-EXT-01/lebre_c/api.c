/* api.c — host shared-library wrapper for the equivalence test (runs a whole series in one call). */
#include "lebre052.h"
#include <stdlib.h>
#ifdef _WIN32
#define EXPORT __declspec(dllexport)
#else
#define EXPORT
#endif
EXPORT int lebre052_sizeof(void) { return (int)sizeof(lebre052); }
/* X: T x dx (row-major, double), y: T (NaN = missing), q: T quarantine flags; out: forecasts; ev: up to evmax events
   (t, kind, add.type, add.i, add.lo, add.hi, rem.type, rem.i) ; returns number of events, or -overflow_flags */
EXPORT int lebre052_run(int T, int dx, int season, int season2, const double *X, const double *y, const int *q,
                        double *out, long *ev, int evmax, long *clipped) {
    lebre052 *m = (lebre052 *)calloc(1, sizeof(lebre052)); if (!m) return -1000;
    lebre052_init(m, dx, season, season2);
    real xr[LB_DMAX];
    for (int t = 0; t < T; t++) {
        for (int i = 0; i < dx; i++) xr[i] = (real)X[(long)t * dx + i];
        int ok = y[t] == y[t];
        out[t] = (double)lebre052_step(m, xr, ok ? (real)y[t] : (real)0, ok, q[t]);
    }
    int n = m->nev < evmax ? m->nev : evmax;
    for (int j = 0; j < n; j++) { long *e = ev + 8L * j; e[0] = m->ev_t[j]; e[1] = m->ev_kind[j]; e[2] = m->ev_add[j].type; e[3] = m->ev_add[j].i;
        e[4] = m->ev_add[j].lo; e[5] = m->ev_add[j].hi; e[6] = m->ev_rem[j].type; e[7] = m->ev_rem[j].i; }
    *clipped = m->n_clipped;
    int ov = m->overflow; free(m);
    return ov ? -ov : n;
}
