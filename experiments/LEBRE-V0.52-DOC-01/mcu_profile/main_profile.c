/* main_profile.c — DOCUMENTATION PROFILE (same model code, same measurement as EXT-01 main.c) that additionally reports
 * per-block (64 steps) mean/max instruction counts, a coarse histogram and the steps above 20k instructions. Based on main.c, which runs the float32 LEBRE v0.52 port over one embedded development series and reports, per step, the counts of
 * the DWT cycle counter (Renode: CYCCNT follows virtual time; with PerformanceInMips = DWT frequency it counts executed
 * instructions) for (a) the causal input scaler and (b) the model step; plus the test-region NMSE and structural events. */
#include <stdint.h>
#include <math.h>
#include "../../LEBRE-V0.52-EXT-01/lebre_c/lebre052.h"
#include "../../LEBRE-V0.52-EXT-01/mcu/series_data.h"                  /* SER_T, SER_DX, SER_SEASON, SER_SEASON2, ser_x[], ser_y[], ser_q[] */

#define DEMCR (*(volatile uint32_t *)0xE000EDFC)
#define DWT_CTRL (*(volatile uint32_t *)0xE0001000)
#define DWT_CYC (*(volatile uint32_t *)0xE0001004)
#define U2_SR (*(volatile uint32_t *)0x40004400)
#define U2_DR (*(volatile uint32_t *)0x40004404)
#define U2_CR1 (*(volatile uint32_t *)0x4000440C)
#define NBIN 8192                           /* histogram of step counts, 4 per bin, up to 32768 */

static lebre052 M;
static uint16_t hist[NBIN];
#define BLK 64
static uint32_t bsum[SER_T / BLK + 1], bmax[SER_T / BLK + 1];
static long big_t[64]; static uint32_t big_v[64]; static int nbig;

static void putc_(char c) { while (!(U2_SR & 0x80)) {} U2_DR = (uint32_t)c; }
static void puts_(const char *s) { while (*s) putc_(*s++); }
static void putu(uint64_t v) { char b[24]; int n = 0; do { b[n++] = (char)('0' + v % 10); v /= 10; } while (v); while (n) putc_(b[--n]); }
static void putf(float v) { if (v < 0) { putc_('-'); v = -v; } uint64_t ip = (uint64_t)v; putu(ip); putc_('.');
    float fr = v - (float)ip; for (int k = 0; k < 6; k++) { fr *= 10; int dg = (int)fr; putc_((char)('0' + dg)); fr -= (float)dg; } }
static void kv(const char *k, uint64_t v) { puts_(k); putc_('='); putu(v); putc_('\n'); }

int main(void) {
    U2_CR1 = (1u << 13) | (1u << 3);
    DEMCR |= (1u << 24); DWT_CYC = 0; DWT_CTRL |= 1u;
    lebre052_init(&M, SER_DX, SER_SEASON, SER_SEASON2);
    float mean[8] = {0}, var[8] = {1, 1, 1, 1, 1, 1, 1, 1}, xs[8];
    uint64_t sum_step = 0, sum_sc = 0; uint32_t max_step = 0, max_sc = 0; long t_max = -1, n_big = 0, n_big_dec = 0;
    long ts = (long)(0.3 * SER_T); double sy = 0, syy = 0, see = 0; long nobs = 0;
    for (long t = 0; t < SER_T; t++) {
        const float *x = &ser_x[t * SER_DX];
        uint32_t c0 = DWT_CYC;
        for (int i = 0; i < SER_DX; i++) xs[i] = (x[i] - mean[i]) / sqrtf(var[i] + 1e-6f);     /* CausalStandardScaler */
        uint32_t c1 = DWT_CYC;
        int ok = !isnan(ser_y[t]);
        float f = lebre052_step(&M, xs, ok ? ser_y[t] : 0.0f, ok, ser_q[t]);
        uint32_t c2 = DWT_CYC;
        for (int i = 0; i < SER_DX; i++) { float dl = x[i] - mean[i]; mean[i] += 1e-4f * dl;
            float v = (1.0f - 1e-4f) * var[i] + 1e-4f * (x[i] - mean[i]) * dl; var[i] = v > 1e-4f ? v : 1e-4f; }
        uint32_t c3 = DWT_CYC;
        uint32_t st = c2 - c1, sc = (c1 - c0) + (c3 - c2);
        sum_step += st; sum_sc += sc; if (st > max_step) { max_step = st; t_max = t; } if (sc > max_sc) max_sc = sc;
        bsum[t / BLK] += st; if (st > bmax[t / BLK]) bmax[t / BLK] = st;
        if (st > 20000 && nbig < 64) { big_t[nbig] = t; big_v[nbig++] = st; }
        if (st > 20000) { n_big++; if (t % 10 == 0) n_big_dec++; }
        uint32_t b = st / 4; if (b >= NBIN) b = NBIN - 1; if (hist[b] < 65535) hist[b]++;
        if (ok && t >= ts) { double yy = ser_y[t]; sy += yy; syy += yy * yy; see += ((double)yy - f) * ((double)yy - f); nobs++; }
    }
    puts_("BEGIN\n");
    kv("T", SER_T); kv("DX", SER_DX); kv("STRUCT_BYTES", sizeof(lebre052));
    kv("STEP_SUM", sum_step); kv("STEP_MAX", max_step); kv("SCALER_SUM", sum_sc); kv("SCALER_MAX", max_sc);
    uint64_t acc = 0, tgt999 = (uint64_t)(0.999 * SER_T), tgt99 = (uint64_t)(0.99 * SER_T), tgt50 = SER_T / 2; int got999 = 0, got99 = 0, got50 = 0;
    for (int b = 0; b < NBIN; b++) { acc += hist[b];
        if (!got50 && acc >= tgt50) { kv("STEP_P50", (uint64_t)b * 4 + 3); got50 = 1; }
        if (!got99 && acc >= tgt99) { kv("STEP_P99", (uint64_t)b * 4 + 3); got99 = 1; }
        if (!got999 && acc >= tgt999) { kv("STEP_P999", (uint64_t)b * 4 + 3); got999 = 1; } }
    double var_y = syy / nobs - (sy / nobs) * (sy / nobs);
    puts_("NMSE="); putf((float)(see / nobs / var_y)); putc_('\n');
    kv("T_MAX", (uint64_t)t_max); kv("N_OVER_20K", (uint64_t)n_big); kv("N_OVER_20K_DECIDE", (uint64_t)n_big_dec);
    kv("EVENTS", (uint64_t)M.nev); kv("CLIPPED", (uint64_t)M.n_clipped); kv("OVERFLOW", (uint64_t)M.overflow);
    for (long b = 0; b <= (SER_T - 1) / BLK; b++) { puts_("BLK="); putu((uint64_t)b); putc_(','); putu(bsum[b]); putc_(','); putu(bmax[b]); putc_('\n'); }
    for (int b = 0; b < NBIN; b += 16) { uint32_t s = 0; for (int q = 0; q < 16; q++) s += hist[b + q];
        if (s) { puts_("HIST="); putu((uint64_t)b * 4); putc_(','); putu(s); putc_('\n'); } }
    for (int k = 0; k < nbig; k++) { puts_("BIG="); putu((uint64_t)big_t[k]); putc_(','); putu(big_v[k]); putc_('\n'); }
    puts_("END\n");
    for (;;) {}
}
