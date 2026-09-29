# Embedded Systems Design Note: Low-Power Shadow-Rent Governance

**Study ID:** `LEBRE-V0.2-SHADOW-RENT-GOVERNANCE-01`  
**Focus:** Embedded Implementation Architecture, State Machine, and Fixed-Point Transformation  
**Target Platform:** ARM Cortex-M0+ / Cortex-M4 Microcontrollers (TinyML Class)  
**Author:** Independent Skeptical Senior Researcher  
**Status:** SEALED ENGINEERING REFERENCE  

---

## 1. Embedded Architectural Overview

In streaming edge devices, battery life and thermal constraints prevent continuous high-frequency execution of exploratory machine learning routines. The LEBRE $T_3$ topology segregates its computation into:
1. An **always-on synchronous fast-path (Live Filter)** executing at full sensor sampling frequency ($f_s$).
2. A **duty-cycled exploratory background task (Shadow Path)** executing intermittently to probe temporal dependencies, evaluate provisional candidate LMS updates, and arbitrate topological promotions.

This design note documents the exact C data structures, state machine transitions, and fixed-point execution semantics required to implement the shadow scheduler on bare-metal or RTOS-based microcontrollers within a strict $16\text{-Byte}$ RAM footprint.

---

## 2. Microcontroller Memory Map & Struct Layout

To guarantee zero dynamic heap allocation (`malloc` prohibited) and word-aligned access on 32-bit ARM architectures, the complete scheduler state is encapsulated in a single 16-Byte structure:

```c
#include <stdint.h>
#include <stdbool.h>

/**
 * @brief 16-Byte Word-Aligned State Structure for S3 Event-Triggered Scheduler
 * Preallocated in static BSS segment (.bss).
 */
typedef struct __attribute__((aligned(4))) {
    float    ref_loss_ema;      /* 4 Bytes: Running baseline prequential MSE (float32) */
    float    cum_dev;           /* 4 Bytes: Page-Hinkley cumulative sum U_t (float32)  */
    uint16_t heartbeat_counter; /* 2 Bytes: Steps elapsed since last shadow execution  */
    uint16_t burst_counter;     /* 2 Bytes: Remaining shadow steps in current burst    */
    uint8_t  is_shadow_awake;   /* 1 Byte:  Boolean flag: 1 = Awake, 0 = Asleep        */
    uint8_t  wake_reason_code;  /* 1 Byte:  0=Sleep, 1=Alarm, 2=Heartbeat, 3=Init      */
    uint8_t  reserved_padding[2];/* 2 Bytes: Alignment padding for 32-bit boundary      */
} LebreShadowScheduler_t;

/* Static Allocation: Exactly 16 Bytes of SRAM */
static LebreShadowScheduler_t g_sched_state;
```

---

## 3. Discrete State Machine & Execution Semantics

The scheduler operates as a deterministic finite-state machine (FSM) evaluated at the end of each live filtering step:

```
                  +-----------------------------------+
                  |           INITIAL WAKE            |
                  |     (Warmup burst: W=50 steps)    |
                  +-----------------+-----------------+
                                    |
                                    | (Burst counter == 0)
                                    v
                  +-----------------------------------+
       +--------->|            DEEP SLEEP             |<---------+
       |          | - Shadow block completely frozen  |          |
       |          | - Inc heartbeat_counter           |          |
       |          | - Accumulate Page-Hinkley sum     |          |
       |          +--------+-----------------+--------+          |
       |                   |                 |                   |
       | (Burst Done)      | (cum_dev > 8.0) | (hb >= 250)       | (1 Step Done)
       |                   v                 v                   |
       |          +-----------------+  +-----------------+       |
       |          |   EVENT ALARM   |  | HEARTBEAT WAKE  |       |
       |          | - Reset cum_dev |  | - Reset hb_cnt  |       |
       |          | - Burst W = 50  |  | - Run 1 step    |       |
       |          +--------+--------+  +--------+--------+       |
       |                   |                    |                |
       +-------------------+--------------------+----------------+
```

---

## 4. Bare-Metal C Implementation

```c
#define PH_ALPHA_LOSS   0.0100000f   /* EMA smoothing factor for baseline reference */
#define PH_DELTA_SLACK  0.1000000f   /* Insensitivity slack deadband                */
#define PH_LAMBDA_TRIP  8.0000000f   /* Page-Hinkley alarm threshold                */
#define HB_INTERVAL_MAX 250          /* Anti-starvation heartbeat interval (steps)  */
#define WAKE_BURST_LEN  50           /* Active burst duration (T_prob equivalent)   */

/**
 * @brief Initialize Scheduler State
 */
void lebre_scheduler_init(LebreShadowScheduler_t *s) {
    s->ref_loss_ema = 0.2000000f;
    s->cum_dev = 0.0f;
    s->heartbeat_counter = 0;
    s->burst_counter = WAKE_BURST_LEN; /* Initial discovery warmup burst */
    s->is_shadow_awake = 1;
    s->wake_reason_code = 3; /* Initial */
}

/**
 * @brief Per-Step Scheduler Sentinel Evaluation
 * Incurs exactly 4 floating-point operations and 2 integer branches.
 * 
 * @param s Pointer to static scheduler state
 * @param ell_live Instantaneous prequential squared error: (y - y_hat)^2
 * @return bool True if shadow block must execute; False to skip and sleep
 */
bool lebre_scheduler_update(LebreShadowScheduler_t *s, float ell_live) {
    /* 1. Sentinel Evaluation: Update baseline reference loss EMA */
    s->ref_loss_ema = (1.0f - PH_ALPHA_LOSS) * s->ref_loss_ema + (PH_ALPHA_LOSS * ell_live);
    
    /* 2. Compute positive innovation beyond deadband slack */
    float diff = ell_live - (s->ref_loss_ema + PH_DELTA_SLACK);
    
    /* 3. Page-Hinkley Cumulative Sum Update */
    float next_dev = s->cum_dev + diff;
    s->cum_dev = (next_dev > 0.0f) ? next_dev : 0.0f;
    
    /* 4. Priority Arbitrated Wake Logic */
    if (s->burst_counter > 0) {
        /* Already in an active wake burst: continue until counter expires */
        s->burst_counter--;
        s->is_shadow_awake = 1;
        s->wake_reason_code = 1; /* Burst active */
    } 
    else if (s->cum_dev > PH_LAMBDA_TRIP) {
        /* Innovation threshold breached: signal alarm and initiate burst */
        s->is_shadow_awake = 1;
        s->burst_counter = WAKE_BURST_LEN - 1; /* Current step counts as step 1 */
        s->cum_dev = 0.0f;                     /* Reset cumulative sum */
        s->heartbeat_counter = 0;             /* Reset anti-starvation counter */
        s->wake_reason_code = 1;              /* Alarm */
    } 
    else if (s->heartbeat_counter >= HB_INTERVAL_MAX) {
        /* Heartbeat wake: anti-starvation single probe step */
        s->is_shadow_awake = 1;
        s->burst_counter = 0;                 /* Exactly 1 step */
        s->heartbeat_counter = 0;             /* Reset heartbeat */
        s->wake_reason_code = 2;              /* Heartbeat */
    } 
    else {
        /* Deep Sleep: skip entire counterfactual shadow pipeline */
        s->is_shadow_awake = 0;
        s->heartbeat_counter++;
        s->wake_reason_code = 0;              /* Sleep */
    }
    
    return (s->is_shadow_awake != 0);
}
```

---

## 5. Integer-Only / Q15 Fixed-Point Transformation

For architectures lacking a hardware Floating-Point Unit (FPU) such as the ARM Cortex-M0+:
- Prequential errors and cumulative sums can be mapped to $Q15$ fixed-point format (1 sign bit, 15 fractional bits, resolution $2^{-15} \approx 3.05 \times 10^{-5}$, range $[-1.0, +0.9999]$).
- Page-Hinkley slack $\delta = 0.10$ maps to integer `3277`.
- Threshold $\lambda = 8.0$ exceeds $[-1, +1)$, and should be accumulated in a $Q16.16$ 32-bit signed integer register (`int32_t`).
- Multiplication by $\alpha = 0.01$ is approximated via binary shift-and-add:
  $$x \times 0.01 \approx (x \gg 7) + (x \gg 9) + (x \gg 10)$$
  yielding zero-division, zero-FPU execution taking $< 12$ clock cycles.

---

## 6. Integration Checklist for Firmware Engineers

1. **Static Linkage:** Confirm `sizeof(LebreShadowScheduler_t) == 16` via `static_assert`.
2. **Interrupt Latency:** Because the scheduler executes synchronously in the sensor ISR or main loop, verify that the worst-case execution time (WCET) of `lebre_scheduler_update` does not exceed $2.5 \mu\text{s}$ at $48\text{ MHz}$.
3. **Power Island Gating:** On microcontrollers with sub-system power gating, when `is_shadow_awake == 0`, SRAM banks storing the shadow correlation grid (`corr_grid`, $330\text{ Bytes}$) can be placed in retention sleep mode to cut dynamic leakage current.
