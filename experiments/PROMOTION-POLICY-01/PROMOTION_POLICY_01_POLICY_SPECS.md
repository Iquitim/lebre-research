# PROMOTION-POLICY-01: Formal Policy Pseudocode Specifications

**Stage:** PROMOTION-POLICY-01 — Sequential Structural Evidence & False-Promotion Control  
**Architecture:** LEBRE v0.1 (`FROZEN_WITH_SCOPE_LIMITS`)  
**Status:** Preregistered Policy Implementation Reference

---

## 1. Common Architectural Interface

All promotion policy variants implement the `IPromotionPolicy` interface. For each time step $t$, after calculating the live baseline prediction $\hat{y}_{\text{base}, t}$ and candidate shadow prediction $\hat{y}_{\text{cand}, t}$, and after the true target $y_t$ is revealed, the prequential loss difference is computed:
$$e_{\text{base}, t} = y_t - \hat{y}_{\text{base}, t}, \quad e_{\text{cand}, t} = y_t - \hat{y}_{\text{cand}, t}$$
$$D_t = e_{\text{base}, t}^2 - e_{\text{cand}, t}^2$$

The policy receives $D_t, e_{\text{base}, t}^2, e_{\text{cand}, t}^2$ and returns one of:
- `DECISION_CONTINUE`: Keep candidate in shadow probation.
- `DECISION_PROMOTE`: Promote candidate to active live state.
- `DECISION_DISCARD`: Terminate probation, discard candidate, and return to dormant or trigger alternate candidate.

---

## 2. Policy Pseudocode Definitions

### P0: `LEBRE_v0.1_FIXED` (Frozen Reference Baseline)
```python
class Policy_P0_Fixed:
    def __init__(self, T_prob=50, theta_promote=0.05):
        self.T_prob = T_prob
        self.theta_promote = theta_promote
        self.age = 0
        self.sum_base_sq = 0.0
        self.sum_cand_sq = 0.0

    def step(self, e_base_sq, e_cand_sq, D_t, w_prov):
        self.age += 1
        self.sum_base_sq += e_base_sq
        self.sum_cand_sq += e_cand_sq
        
        if self.age >= self.T_prob:
            G_prob = 1.0 - (self.sum_cand_sq / (self.sum_base_sq + 1e-8))
            if G_prob > self.theta_promote or abs(w_prov) > 0.30:
                return "DECISION_PROMOTE"
            else:
                return "DECISION_DISCARD"
        return "DECISION_CONTINUE"
```

---

### P1: `FIXED_LONG` (Extended Horizon Control)
```python
class Policy_P1_FixedLong:
    def __init__(self, T_prob=150, theta_promote=0.05):
        self.T_prob = T_prob
        self.theta_promote = theta_promote
        self.age = 0
        self.sum_base_sq = 0.0
        self.sum_cand_sq = 0.0

    def step(self, e_base_sq, e_cand_sq, D_t, w_prov):
        self.age += 1
        self.sum_base_sq += e_base_sq
        self.sum_cand_sq += e_cand_sq
        
        if self.age >= self.T_prob:
            G_prob = 1.0 - (self.sum_cand_sq / (self.sum_base_sq + 1e-8))
            if G_prob > self.theta_promote:
                return "DECISION_PROMOTE"
            else:
                return "DECISION_DISCARD"
        return "DECISION_CONTINUE"
```

---

### P2: `FIXED_STRICT` (Conservative Threshold Control)
```python
class Policy_P2_FixedStrict:
    def __init__(self, T_prob=50, theta_promote=0.15):
        self.T_prob = T_prob
        self.theta_promote = theta_promote
        self.age = 0
        self.sum_base_sq = 0.0
        self.sum_cand_sq = 0.0

    def step(self, e_base_sq, e_cand_sq, D_t, w_prov):
        self.age += 1
        self.sum_base_sq += e_base_sq
        self.sum_cand_sq += e_cand_sq
        
        if self.age >= self.T_prob:
            G_prob = 1.0 - (self.sum_cand_sq / (self.sum_base_sq + 1e-8))
            if G_prob > self.theta_promote:
                return "DECISION_PROMOTE"
            else:
                return "DECISION_DISCARD"
        return "DECISION_CONTINUE"
```

---

### P3: `TWO_WINDOW_CONFIRM` (Temporal Replication Policy)
```python
class Policy_P3_TwoWindowConfirm:
    def __init__(self, T_A=50, T_B=50, theta_A=0.05, theta_B=0.02):
        self.T_A = T_A
        self.T_B = T_B
        self.theta_A = theta_A
        self.theta_B = theta_B
        self.age = 0
        
        # Window A accumulators
        self.sum_base_A = 0.0
        self.sum_cand_A = 0.0
        # Window B accumulators
        self.sum_base_B = 0.0
        self.sum_cand_B = 0.0

    def step(self, e_base_sq, e_cand_sq, D_t, w_prov):
        self.age += 1
        
        if self.age <= self.T_A:
            self.sum_base_A += e_base_sq
            self.sum_cand_A += e_cand_sq
            if self.age == self.T_A:
                G_A = 1.0 - (self.sum_cand_A / (self.sum_base_A + 1e-8))
                if G_A <= self.theta_A:
                    return "DECISION_DISCARD" # Failed initial probation
            return "DECISION_CONTINUE"
            
        elif self.age <= self.T_A + self.T_B:
            self.sum_base_B += e_base_sq
            self.sum_cand_B += e_cand_sq
            if self.age == self.T_A + self.T_B:
                G_B = 1.0 - (self.sum_cand_B / (self.sum_base_B + 1e-8))
                if G_B > self.theta_B:
                    return "DECISION_PROMOTE" # Confirmed out-of-sample!
                else:
                    return "DECISION_DISCARD" # Failed confirmation
            return "DECISION_CONTINUE"
            
        return "DECISION_DISCARD"
```

---

### P4: `CS_PROMOTION` (Empirical Confidence Sequence Policy)
```python
class Policy_P4_ConfidenceSequence:
    def __init__(self, min_obs=30, futility_obs=60, max_obs=150, delta_min=0.02, z_crit=1.96):
        self.min_obs = min_obs
        self.futility_obs = futility_obs
        self.max_obs = max_obs
        self.delta_min = delta_min
        self.z_crit = z_crit
        
        self.t = 0
        self.mean_D = 0.0
        self.M2_D = 0.0 # Welford running variance accumulator

    def step(self, e_base_sq, e_cand_sq, D_t, w_prov):
        self.t += 1
        # Online Welford update for mean and variance of D_t
        delta = D_t - self.mean_D
        self.mean_D += delta / self.t
        delta2 = D_t - self.mean_D
        self.M2_D += delta * delta2
        
        var_D = (self.M2_D / (self.t - 1)) if self.t > 1 else 1.0
        std_D = max(1e-4, var_D ** 0.5)
        
        # Stitching confidence sequence radius
        radius = self.z_crit * (std_D / (self.t ** 0.5)) * ((1.0 + (np.log(self.t + 1.0) / self.t)) ** 0.5)
        lcb = self.mean_D - radius
        ucb = self.mean_D + radius
        
        # 1. Early Promotion
        if self.t >= self.min_obs and lcb > self.delta_min:
            return "DECISION_PROMOTE"
            
        # 2. Early Futility Discard
        if self.t >= self.futility_obs and ucb < 0.0:
            return "DECISION_DISCARD"
            
        # 3. Maximum Horizon
        if self.t >= self.max_obs:
            if self.mean_D > self.delta_min:
                return "DECISION_PROMOTE"
            else:
                return "DECISION_DISCARD"
                
        return "DECISION_CONTINUE"
```

---

### P5: `GLOBAL_ERROR_BUDGET` (Across-Candidate Wealth Budgeting)
```python
class Policy_P5_GlobalErrorBudget:
    def __init__(self, initial_wealth=1.0, birth_cost=0.10, success_reward=0.25, base_policy_cls=Policy_P0_Fixed):
        self.wealth = initial_wealth
        self.birth_cost = birth_cost
        self.success_reward = success_reward
        self.base_policy_cls = base_policy_cls
        self.current_candidate_policy = None

    def can_birth(self) -> bool:
        return self.wealth >= self.birth_cost

    def on_birth(self):
        self.wealth -= self.birth_cost
        self.current_candidate_policy = self.base_policy_cls()

    def step(self, e_base_sq, e_cand_sq, D_t, w_prov):
        decision = self.current_candidate_policy.step(e_base_sq, e_cand_sq, D_t, w_prov)
        return decision

    def on_post_evaluation(self, post_gain_positive: bool):
        if post_gain_positive:
            self.wealth = min(2.0, self.wealth + self.success_reward)
```

---

### P6: `CS_PLUS_BUDGET` (Sequential CS + Opportunity Budget)
```python
class Policy_P6_CSPlusBudget(Policy_P5_GlobalErrorBudget):
    def __init__(self):
        super().__init__(
            initial_wealth=1.0,
            birth_cost=0.10,
            success_reward=0.25,
            base_policy_cls=Policy_P4_ConfidenceSequence
        )
```
