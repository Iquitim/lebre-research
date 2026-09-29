"""
Generates the canonical SVG diagrams for the LEBRE architecture v0.1.
Publication-grade vector graphics with clean typography, responsive viewboxes,
reconciled normative constants, and no vertical/rotated text over lines.
"""

from pathlib import Path

OUT_DIR = Path("docs/architecture/assets/diagrams")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# -------------------------------------------------------------
# D1: High-Level Architecture
# -------------------------------------------------------------
d1_svg = """<svg width="800" height="480" viewBox="0 0 800 480" xmlns="http://www.w3.org/2000/svg" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif">
  <defs>
    <marker id="arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#334155" />
    </marker>
    <marker id="arr-blue" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#0284C7" />
    </marker>
    <marker id="arr-red" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#DC2626" />
    </marker>
    <filter id="shadow" x="-3%" y="-4%" width="106%" height="110%" filterUnits="userSpaceOnUse">
      <feDropShadow dx="1" dy="2" stdDeviation="2" flood-opacity="0.08" />
    </filter>
  </defs>

  <!-- Canvas Background -->
  <rect width="800" height="480" fill="#FFFFFF" rx="8" />

  <!-- Diagram Title -->
  <text x="30" y="32" font-size="16" font-weight="700" fill="#0F172A">D1: LEBRE High-Level System Architecture &amp; Execution Flow</text>
  <text x="30" y="50" font-size="12" fill="#64748B">Causal Inference Pipeline vs. Post-Target Evidence &amp; Lifecycle Controller</text>

  <!-- Section 1: Observation Layer -->
  <g transform="translate(30, 70)" filter="url(#shadow)">
    <rect width="160" height="150" fill="#F8FAFC" stroke="#CBD5E1" stroke-width="1.5" rx="6" />
    <text x="15" y="24" font-size="12" font-weight="700" fill="#1E293B">1. OBSERVATION</text>
    <rect x="15" y="40" width="130" height="35" fill="#FFFFFF" stroke="#94A3B8" rx="4" />
    <text x="80" y="62" font-size="11" text-anchor="middle" fill="#0F172A">Input Stream x_t</text>
    <rect x="15" y="90" width="130" height="45" fill="#FFFFFF" stroke="#94A3B8" rx="4" />
    <text x="80" y="108" font-size="10" text-anchor="middle" fill="#0F172A">Causal Preprocessing</text>
    <text x="80" y="122" font-size="9" text-anchor="middle" fill="#64748B">&amp; Normalization</text>
  </g>

  <!-- Connector to Inference -->
  <line x1="190" y1="145" x2="230" y2="145" stroke="#334155" stroke-width="1.5" marker-end="url(#arr)" />

  <!-- Section 2: Dual Inference Predictor -->
  <g transform="translate(235, 70)" filter="url(#shadow)">
    <rect width="260" height="150" fill="#F0F9FF" stroke="#BAE6FD" stroke-width="1.5" rx="6" />
    <text x="15" y="24" font-size="12" font-weight="700" fill="#0369A1">2. ACTIVE CAUSAL PREDICTOR</text>
    
    <!-- Base Model -->
    <rect x="15" y="38" width="230" height="44" fill="#FFFFFF" stroke="#38BDF8" rx="4" />
    <text x="25" y="56" font-size="11" font-weight="600" fill="#0F172A">Sparse Linear Base Model</text>
    <text x="25" y="72" font-size="10" fill="#64748B">y_base,t = w_base^T x_t (K &lt;= 10)</text>

    <!-- Recurrent Model -->
    <rect x="15" y="92" width="230" height="44" fill="#FFFFFF" stroke="#38BDF8" rx="4" />
    <text x="25" y="110" font-size="11" font-weight="600" fill="#0F172A">Active Recurrent State (N &lt;= 1)</text>
    <text x="25" y="126" font-size="10" fill="#64748B">y_rec,t = w_s * s_t (Linear or Gated)</text>
  </g>

  <!-- Adder & Output -->
  <line x1="495" y1="145" x2="535" y2="145" stroke="#334155" stroke-width="1.5" marker-end="url(#arr)" />

  <g transform="translate(540, 115)" filter="url(#shadow)">
    <rect width="100" height="60" fill="#ECFDF5" stroke="#A7F3D0" stroke-width="1.5" rx="6" />
    <text x="50" y="26" font-size="11" font-weight="700" text-anchor="middle" fill="#065F46">PREDICTION</text>
    <text x="50" y="46" font-size="12" font-weight="700" text-anchor="middle" fill="#047857">y_hat,t</text>
  </g>

  <!-- Output Emission & Target Reveal -->
  <line x1="640" y1="145" x2="685" y2="145" stroke="#059669" stroke-width="1.5" marker-end="url(#arr)" />
  
  <g transform="translate(685, 115)">
    <rect width="85" height="60" fill="#FEF3C7" stroke="#FDE68A" stroke-width="1.5" rx="6" />
    <text x="42" y="26" font-size="10" font-weight="700" text-anchor="middle" fill="#92400E">TARGET</text>
    <text x="42" y="46" font-size="12" font-weight="700" text-anchor="middle" fill="#B45309">y_t</text>
  </g>

  <!-- Downward Line: Target reveals Error -->
  <path d="M 727 175 L 727 250 L 675 250" stroke="#DC2626" stroke-width="1.5" fill="none" marker-end="url(#arr-red)" />

  <!-- Section 3: Error & Prequential Scoring -->
  <g transform="translate(480, 230)" filter="url(#shadow)">
    <rect width="190" height="75" fill="#FEF2F2" stroke="#FECACA" stroke-width="1.5" rx="6" />
    <text x="15" y="22" font-size="11" font-weight="700" fill="#991B1B">3. ERROR SCORING</text>
    <text x="15" y="42" font-size="11" fill="#0F172A">e_t = y_t - y_hat,t</text>
    <text x="15" y="60" font-size="11" fill="#64748B">e_base,t = y_t - y_base,t</text>
  </g>

  <!-- Section 4: Shadow Probation Explorer -->
  <g transform="translate(30, 250)" filter="url(#shadow)">
    <rect width="180" height="90" fill="#FDF4FF" stroke="#F5D0FE" stroke-width="1.5" rx="6" />
    <text x="12" y="22" font-size="11" font-weight="700" fill="#86198F">4. SHADOW PROBATION</text>
    <text x="12" y="42" font-size="10" fill="#0F172A">Candidate s_p,t (Isolated)</text>
    <text x="12" y="58" font-size="9" fill="#701A75">Adapts w_prov in parallel</text>
    <text x="12" y="74" font-size="9" fill="#701A75">Zero impact on live y_hat,t</text>
  </g>

  <!-- Section 5: Evidence & Utility Layer -->
  <g transform="translate(235, 250)" filter="url(#shadow)">
    <rect width="220" height="90" fill="#F8FAFC" stroke="#CBD5E1" stroke-width="1.5" rx="6" />
    <text x="12" y="22" font-size="11" font-weight="700" fill="#1E293B">5. EVIDENCE &amp; UTILITY</text>
    <text x="12" y="40" font-size="10" fill="#0F172A">Delta Loss = e_base^2 - e_t^2</text>
    <text x="12" y="56" font-size="10" fill="#0F172A">Slow Relevance: U_ret (tau~140)</text>
    <text x="12" y="74" font-size="10" fill="#0F172A">Obsolescence: O_obs accumulator</text>
  </g>

  <!-- Connecting Error to Utility -->
  <line x1="480" y1="270" x2="460" y2="270" stroke="#334155" stroke-width="1.5" marker-end="url(#arr)" />

  <!-- Section 6: Lifecycle & Resource Controller -->
  <g transform="translate(100, 375)" filter="url(#shadow)">
    <rect width="600" height="85" fill="#F1F5F9" stroke="#94A3B8" stroke-width="1.5" rx="6" />
    <text x="20" y="24" font-size="12" font-weight="700" fill="#0F172A">6. RESOURCE-GOVERNED LIFECYCLE CONTROLLER</text>
    <text x="20" y="46" font-size="11" fill="#334155">Governs transitions across unified states: DORMANT -&gt; PROVISIONAL -&gt; ACTIVE -&gt; MATURE -&gt; EVICTED</text>
    <text x="20" y="66" font-size="10" fill="#475569">Actions: Prov. Birth (Error Trigger) | Promotion (Probation Gain) | Retain (Quiescent U_ret) | Evict &amp; Reclaim RAM/FLOPs</text>
  </g>

  <!-- Upward control lines -->
  <path d="M 230 375 L 230 345" stroke="#0284C7" stroke-width="1.5" marker-end="url(#arr-blue)" />
  <path d="M 120 375 L 120 345" stroke="#0284C7" stroke-width="1.5" marker-end="url(#arr-blue)" />
  <path d="M 400 375 L 400 225" stroke="#0284C7" stroke-width="1.5" marker-end="url(#arr-blue)" />
</svg>
"""

# -------------------------------------------------------------
# D2: Five-State Structural Lifecycle State Machine (English)
# -------------------------------------------------------------
d2_svg = """<svg width="800" height="380" viewBox="0 0 800 380" xmlns="http://www.w3.org/2000/svg" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif">
  <defs>
    <marker id="arr2" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#475569" />
    </marker>
    <filter id="sh2" x="-4%" y="-5%" width="108%" height="112%" filterUnits="userSpaceOnUse">
      <feDropShadow dx="1" dy="2" stdDeviation="2" flood-opacity="0.08" />
    </filter>
  </defs>

  <rect width="800" height="380" fill="#FFFFFF" rx="8" />
  <text x="30" y="32" font-size="16" font-weight="700" fill="#0F172A">D2: Five-State Structural Lifecycle State Machine</text>
  <text x="30" y="50" font-size="12" fill="#64748B">Five discrete lifecycle states governing all cost-bearing structural objects</text>

  <!-- State 1: DORMANT -->
  <g transform="translate(30, 90)" filter="url(#sh2)">
    <rect width="125" height="110" fill="#F8FAFC" stroke="#94A3B8" stroke-width="1.5" rx="6" />
    <rect x="0" y="0" width="125" height="28" fill="#E2E8F0" rx="6" />
    <text x="62" y="19" font-size="11" font-weight="700" text-anchor="middle" fill="#334155">1. DORMANT</text>
    <text x="12" y="48" font-size="10" fill="#475569">Memory: 0 Bytes</text>
    <text x="12" y="66" font-size="10" fill="#475569">Compute: 0 FLOPs</text>
    <text x="12" y="84" font-size="9" fill="#64748B">Object latent</text>
    <text x="12" y="98" font-size="9" fill="#64748B">No prediction impact</text>
  </g>

  <!-- Arrow 1 -> 2: Birth -->
  <line x1="155" y1="145" x2="190" y2="145" stroke="#475569" stroke-width="1.5" marker-end="url(#arr2)" />
  <text x="172" y="135" font-size="9" font-weight="600" text-anchor="middle" fill="#0284C7">Birth</text>

  <!-- State 2: PROVISIONAL -->
  <g transform="translate(195, 90)" filter="url(#sh2)">
    <rect width="135" height="110" fill="#FDF4FF" stroke="#D8B4FE" stroke-width="1.5" rx="6" />
    <rect x="0" y="0" width="135" height="28" fill="#F3E8FF" rx="6" />
    <text x="67" y="19" font-size="11" font-weight="700" text-anchor="middle" fill="#7E22CE">2. PROVISIONAL</text>
    <text x="10" y="48" font-size="10" fill="#475569">Shadow Probation</text>
    <text x="10" y="66" font-size="10" font-weight="600" fill="#7E22CE">T_prob = 50 steps</text>
    <text x="10" y="84" font-size="9" fill="#7E22CE">Isolated from y_hat</text>
    <text x="10" y="98" font-size="9" fill="#64748B">Parallel RTRL update</text>
  </g>

  <!-- Arrow 2 -> 3: Promotion -->
  <line x1="330" y1="145" x2="365" y2="145" stroke="#475569" stroke-width="1.5" marker-end="url(#arr2)" />
  <text x="348" y="135" font-size="9" font-weight="600" text-anchor="middle" fill="#059669">Promote</text>

  <!-- Discard from Provisional back to Dormant -->
  <path d="M 262 200 L 262 230 L 92 230 L 92 205" stroke="#94A3B8" stroke-dasharray="3,3" stroke-width="1.2" fill="none" marker-end="url(#arr2)" />
  <text x="177" y="244" font-size="9" text-anchor="middle" fill="#94A3B8">Probation Failed (Discard / Revert)</text>

  <!-- State 3: ACTIVE -->
  <g transform="translate(370, 90)" filter="url(#sh2)">
    <rect width="130" height="110" fill="#F0FDF4" stroke="#86EFAC" stroke-width="1.5" rx="6" />
    <rect x="0" y="0" width="130" height="28" fill="#DCFCE7" rx="6" />
    <text x="65" y="19" font-size="11" font-weight="700" text-anchor="middle" fill="#15803D">3. ACTIVE</text>
    <text x="10" y="48" font-size="10" fill="#475569">Coupled to y_hat</text>
    <text x="10" y="66" font-size="10" fill="#475569">Full inference cost</text>
    <text x="10" y="84" font-size="9" fill="#15803D">Maturation Grace</text>
    <text x="10" y="98" font-size="9" fill="#64748B">tau_mature = 100 steps</text>
  </g>

  <!-- Arrow 3 -> 4: Maturation -->
  <line x1="500" y1="145" x2="535" y2="145" stroke="#475569" stroke-width="1.5" marker-end="url(#arr2)" />
  <text x="518" y="135" font-size="9" font-weight="600" text-anchor="middle" fill="#15803D">Mature</text>

  <!-- State 4: MATURE -->
  <g transform="translate(540, 90)" filter="url(#sh2)">
    <rect width="135" height="110" fill="#EFF6FF" stroke="#93C5FD" stroke-width="1.5" rx="6" />
    <rect x="0" y="0" width="135" height="28" fill="#DBEAFE" rx="6" />
    <text x="67" y="19" font-size="11" font-weight="700" text-anchor="middle" fill="#1D4ED8">4. MATURE</text>
    <text x="10" y="48" font-size="10" fill="#475569">Full Rent Required</text>
    <text x="10" y="66" font-size="10" fill="#475569">Two-Timescale U_ret</text>
    <text x="10" y="84" font-size="9" fill="#1D4ED8">Quiescent Retention</text>
    <text x="10" y="98" font-size="9" fill="#64748B">Bridges silent gaps</text>
  </g>

  <!-- Arrow 4 -> 5: Eviction -->
  <path d="M 607 200 L 607 280 L 505 280" stroke="#DC2626" stroke-width="1.5" fill="none" marker-end="url(#arr2)" />
  <text x="612" y="245" font-size="9" font-weight="600" fill="#DC2626">Eviction Gate</text>
  <text x="612" y="258" font-size="8" fill="#64748B">(U_ret low &amp; O_obs high)</text>

  <!-- State 5: EVICTED / RECLAIMED -->
  <g transform="translate(345, 245)" filter="url(#sh2)">
    <rect width="155" height="90" fill="#FEF2F2" stroke="#FCA5A5" stroke-width="1.5" rx="6" />
    <rect x="0" y="0" width="155" height="28" fill="#FEE2E2" rx="6" />
    <text x="77" y="19" font-size="11" font-weight="700" text-anchor="middle" fill="#B91C1C">5. EVICTED</text>
    <text x="10" y="46" font-size="10" fill="#475569">Physical Deallocation</text>
    <text x="10" y="62" font-size="9" fill="#B91C1C">Arrays freed (None)</text>
    <text x="10" y="76" font-size="9" fill="#475569">Compute excised from loop</text>
  </g>

  <!-- Arrow 5 -> 1: Return to Dormant -->
  <path d="M 345 290 L 92 290 L 92 205" stroke="#475569" stroke-width="1.5" fill="none" marker-end="url(#arr2)" />
  <text x="210" y="306" font-size="9" font-weight="600" text-anchor="middle" fill="#475569">Slot returned to Dormant (Budget Reclaimed)</text>
</svg>
"""

# -------------------------------------------------------------
# D3: Data Flow vs Control Flow
# -------------------------------------------------------------
d3_svg = """<svg width="800" height="360" viewBox="0 0 800 360" xmlns="http://www.w3.org/2000/svg" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif">
  <defs>
    <marker id="arr3" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#334155" />
    </marker>
    <marker id="arr-c" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#7C3AED" />
    </marker>
  </defs>

  <rect width="800" height="360" fill="#FFFFFF" rx="8" />
  <text x="30" y="32" font-size="16" font-weight="700" fill="#0F172A">D3: Data Flow vs. Control Flow Decoupling</text>
  <text x="30" y="50" font-size="12" fill="#64748B">Rigorous temporal and functional separation between inference and governance</text>

  <!-- Top Block: DATA FLOW (Inference Pipeline) -->
  <g transform="translate(30, 75)">
    <rect width="740" height="115" fill="#F0FDF4" stroke="#86EFAC" stroke-width="1.5" rx="6" />
    <text x="20" y="24" font-size="12" font-weight="700" fill="#166534">DATA FLOW (Strictly Causal Inference before target y_t is revealed)</text>
    
    <!-- Steps in Data Flow -->
    <rect x="20" y="40" width="130" height="50" fill="#FFFFFF" stroke="#86EFAC" rx="4" />
    <text x="85" y="60" font-size="11" font-weight="600" text-anchor="middle" fill="#0F172A">Observe x_t</text>
    <text x="85" y="76" font-size="9" text-anchor="middle" fill="#64748B">R^D Ambient</text>

    <line x1="150" y1="65" x2="190" y2="65" stroke="#166534" stroke-width="1.5" marker-end="url(#arr3)" />

    <rect x="195" y="40" width="180" height="50" fill="#FFFFFF" stroke="#86EFAC" rx="4" />
    <text x="285" y="60" font-size="11" font-weight="600" text-anchor="middle" fill="#0F172A">Linear &amp; State Forward</text>
    <text x="285" y="76" font-size="9" text-anchor="middle" fill="#64748B">w_base^T x_t + w_s * s_t</text>

    <line x1="375" y1="65" x2="415" y2="65" stroke="#166534" stroke-width="1.5" marker-end="url(#arr3)" />

    <rect x="420" y="40" width="140" height="50" fill="#FFFFFF" stroke="#86EFAC" rx="4" />
    <text x="490" y="60" font-size="11" font-weight="600" text-anchor="middle" fill="#0F172A">Emit y_hat,t</text>
    <text x="490" y="76" font-size="9" text-anchor="middle" fill="#64748B">Prequential Prediction</text>

    <line x1="560" y1="65" x2="600" y2="65" stroke="#166534" stroke-width="1.5" marker-end="url(#arr3)" />

    <rect x="605" y="40" width="115" height="50" fill="#DCFCE7" stroke="#166534" rx="4" />
    <text x="662" y="60" font-size="11" font-weight="700" text-anchor="middle" fill="#166534">Environment</text>
    <text x="662" y="76" font-size="9" text-anchor="middle" fill="#166534">Action / Output</text>
  </g>

  <!-- Divider indicating Target Reveal -->
  <line x1="40" y1="210" x2="760" y2="210" stroke="#CBD5E1" stroke-dasharray="4,4" stroke-width="1.5" />
  <text x="400" y="214" font-size="10" font-weight="600" text-anchor="middle" fill="#94A3B8">TARGET REVEAL (y_t is received; Inference ends, Governance begins)</text>

  <!-- Bottom Block: CONTROL FLOW (Governance Pipeline) -->
  <g transform="translate(30, 225)">
    <rect width="740" height="115" fill="#FAF5FF" stroke="#D8B4FE" stroke-width="1.5" rx="6" />
    <text x="20" y="24" font-size="12" font-weight="700" fill="#6B21A8">CONTROL FLOW (Post-Target Evidence, Parameter &amp; Structural Adaptation)</text>
    
    <rect x="20" y="40" width="140" height="50" fill="#FFFFFF" stroke="#D8B4FE" rx="4" />
    <text x="90" y="60" font-size="11" font-weight="600" text-anchor="middle" fill="#0F172A">Error Evaluation</text>
    <text x="90" y="76" font-size="9" text-anchor="middle" fill="#64748B">e_t &amp; e_base,t</text>

    <line x1="160" y1="65" x2="195" y2="65" stroke="#7C3AED" stroke-width="1.5" marker-end="url(#arr-c)" />

    <rect x="200" y="40" width="160" height="50" fill="#FFFFFF" stroke="#D8B4FE" rx="4" />
    <text x="280" y="60" font-size="11" font-weight="600" text-anchor="middle" fill="#0F172A">Sensitivity &amp; Utility</text>
    <text x="280" y="76" font-size="9" text-anchor="middle" fill="#64748B">RTRL S_t, U_ret, O_obs</text>

    <line x1="360" y1="65" x2="395" y2="65" stroke="#7C3AED" stroke-width="1.5" marker-end="url(#arr-c)" />

    <rect x="400" y="40" width="170" height="50" fill="#FFFFFF" stroke="#D8B4FE" rx="4" />
    <text x="485" y="60" font-size="11" font-weight="600" text-anchor="middle" fill="#0F172A">Lifecycle Decisions</text>
    <text x="485" y="76" font-size="9" text-anchor="middle" fill="#64748B">Birth / Promote / Evict</text>

    <line x1="570" y1="65" x2="605" y2="65" stroke="#7C3AED" stroke-width="1.5" marker-end="url(#arr-c)" />

    <rect x="610" y="40" width="115" height="50" fill="#F3E8FF" stroke="#7C3AED" rx="4" />
    <text x="667" y="60" font-size="11" font-weight="700" text-anchor="middle" fill="#6B21A8">Reallocate</text>
    <text x="667" y="76" font-size="9" text-anchor="middle" fill="#6B21A8">Topology Updated</text>
  </g>
</svg>
"""

# -------------------------------------------------------------
# D4: Non-Interfering Shadow Probation (REDESIGNED — Publication Quality)
# -------------------------------------------------------------
d4_svg = """<svg width="800" height="390" viewBox="0 0 800 390" xmlns="http://www.w3.org/2000/svg" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif">
  <defs>
    <marker id="arr4" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#334155" />
    </marker>
    <filter id="card-shadow" x="-3%" y="-4%" width="106%" height="110%" filterUnits="userSpaceOnUse">
      <feDropShadow dx="1" dy="2" stdDeviation="2" flood-opacity="0.06" />
    </filter>
  </defs>

  <rect width="800" height="390" fill="#FFFFFF" rx="8" />
  
  <!-- Title & Subtitle -->
  <text x="30" y="30" font-size="15" font-weight="700" fill="#0F172A">D4: Non-Interfering Shadow Mode Probation &amp; Promotion Protocol</text>
  <text x="30" y="48" font-size="11" fill="#64748B">Provisional candidate learns counterfactually in isolation without injecting transient disruption into live inference</text>

  <!-- Left Card: Live Active Predictor -->
  <g transform="translate(30, 68)" filter="url(#card-shadow)">
    <rect width="325" height="180" fill="#F0FDF4" stroke="#86EFAC" stroke-width="1.5" rx="6" />
    <rect x="0" y="0" width="325" height="32" fill="#DCFCE7" rx="6" />
    <text x="15" y="21" font-size="12" font-weight="700" fill="#166534">LIVE PREDICTOR</text>
    <text x="130" y="21" font-size="10" font-weight="500" fill="#15803D">(Active Causal Model)</text>
    
    <text x="15" y="56" font-size="10.5" font-weight="600" fill="#0F172A">Sparse Base Model:</text>
    <text x="145" y="56" font-size="10.5" fill="#334155"><tspan font-style="italic">w</tspan><tspan font-size="8" dy="3">base</tspan><tspan dy="-3"> &#x2208; &#x211D;</tspan><tspan font-size="8" dy="-4">D</tspan></text>
    
    <text x="15" y="78" font-size="10.5" font-weight="600" fill="#0F172A">Causal Output:</text>
    <text x="145" y="78" font-size="10.5" font-weight="700" fill="#15803D">&#375;<tspan font-size="8" dy="3">t</tspan><tspan dy="-3"> = </tspan><tspan font-style="italic">w</tspan><tspan font-size="8" dy="3">base</tspan><tspan font-size="7.5" dy="-5">T</tspan><tspan dy="2" font-style="italic"> x</tspan><tspan font-size="8" dy="3">t</tspan><tspan dy="-3"> + </tspan><tspan font-style="italic">w</tspan><tspan font-size="8" dy="3">s</tspan><tspan dy="-3"> </tspan><tspan font-style="italic">s</tspan><tspan font-size="8" dy="3">t</tspan></text>

    <text x="15" y="100" font-size="10.5" font-weight="600" fill="#0F172A">Operational Role:</text>
    <text x="145" y="100" font-size="10" fill="#334155">Drives immediate system actions</text>

    <rect x="15" y="120" width="295" height="46" fill="#FFFFFF" stroke="#86EFAC" rx="4" />
    <text x="162" y="139" font-size="10" font-weight="700" text-anchor="middle" fill="#166534">Protected Inference Path</text>
    <text x="162" y="153" font-size="9" text-anchor="middle" fill="#64748B">Zero coupling to unvalidated shadow parameters</text>
  </g>

  <!-- Center: Non-Interference Barrier Column -->
  <g transform="translate(365, 68)">
    <rect width="70" height="180" fill="#F8FAFC" stroke="#CBD5E1" stroke-width="1.2" rx="6" />
    
    <!-- Top Horizontal Header Pill -->
    <rect x="-10" y="-8" width="90" height="24" fill="#1E293B" rx="12" />
    <text x="35" y="8" font-size="8" font-weight="700" text-anchor="middle" fill="#FFFFFF" letter-spacing="0.04em">BARRIER</text>
    
    <!-- Upper Vertical Dashed Line Segment -->
    <line x1="35" y1="22" x2="35" y2="68" stroke="#64748B" stroke-dasharray="4,3" stroke-width="2" />
    
    <!-- Middle Gate Badge Card -->
    <rect x="4" y="70" width="62" height="42" fill="#FFFFFF" stroke="#0284C7" stroke-width="1.5" rx="4" />
    <text x="35" y="87" font-size="11" font-weight="800" text-anchor="middle" fill="#0F172A"><tspan font-style="italic">g</tspan><tspan font-size="8" dy="2">p</tspan><tspan dy="-2"> = 0.0</tspan></text>
    <text x="35" y="102" font-size="7.5" font-weight="700" text-anchor="middle" fill="#0284C7">HARD GATE</text>

    <!-- Lower Vertical Dashed Line Segment -->
    <line x1="35" y1="114" x2="35" y2="128" stroke="#64748B" stroke-dasharray="4,3" stroke-width="2" />

    <!-- Bottom Isolation Pill Card -->
    <rect x="3" y="130" width="64" height="42" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="1.2" rx="4" />
    <text x="35" y="145" font-size="8" font-weight="700" text-anchor="middle" fill="#334155">Strict</text>
    <text x="35" y="156" font-size="8" font-weight="700" text-anchor="middle" fill="#334155">Isolation</text>
    <text x="35" y="167" font-size="7" font-weight="600" text-anchor="middle" fill="#64748B"><tspan font-style="italic">g</tspan><tspan font-size="6" dy="2">p</tspan><tspan dy="-2">&#183;</tspan><tspan font-style="italic">s</tspan><tspan font-size="6" dy="2">p</tspan><tspan dy="-2"> = 0</tspan></text>
  </g>

  <!-- Right Card: Shadow Provisional Candidate -->
  <g transform="translate(445, 68)" filter="url(#card-shadow)">
    <rect width="325" height="180" fill="#FAF5FF" stroke="#D8B4FE" stroke-width="1.5" rx="6" />
    <rect x="0" y="0" width="325" height="32" fill="#F3E8FF" rx="6" />
    <text x="15" y="21" font-size="12" font-weight="700" fill="#7E22CE">SHADOW CANDIDATE</text>
    <text x="165" y="21" font-size="10" font-weight="500" fill="#6B21A8">(Provisional State <tspan font-style="italic">s</tspan><tspan font-size="8" dy="2">p,t</tspan>)</text>
    
    <text x="15" y="56" font-size="10.5" font-weight="600" fill="#0F172A">Candidate State:</text>
    <text x="145" y="56" font-size="10.5" fill="#334155"><tspan font-style="italic">s</tspan><tspan font-size="8" dy="2">p,t</tspan><tspan dy="-2"> (Scalar Recurrent)</tspan></text>
    
    <text x="15" y="78" font-size="10.5" font-weight="600" fill="#0F172A">Shadow Output:</text>
    <text x="145" y="78" font-size="10.5" font-weight="700" fill="#7E22CE"><tspan font-style="italic">y</tspan><tspan font-size="8" dy="2">prov,t</tspan><tspan dy="-2"> = </tspan><tspan font-style="italic">y</tspan><tspan font-size="8" dy="2">base,t</tspan><tspan dy="-2"> + </tspan><tspan font-style="italic">w</tspan><tspan font-size="8" dy="2">p</tspan><tspan dy="-2"> </tspan><tspan font-style="italic">s</tspan><tspan font-size="8" dy="2">p,t</tspan></text>

    <text x="15" y="100" font-size="10.5" font-weight="600" fill="#0F172A">Parallel Learning:</text>
    <text x="145" y="100" font-size="10" fill="#334155">Local RTRL on candidate weights</text>

    <rect x="15" y="120" width="295" height="46" fill="#FFFFFF" stroke="#D8B4FE" rx="4" />
    <text x="162" y="138" font-size="10" font-weight="700" text-anchor="middle" fill="#7E22CE">Counterfactual Evidence Tracking</text>
    <text x="162" y="153" font-size="9" text-anchor="middle" fill="#64748B">&#916;&#8466;<tspan font-size="7" dy="2">t</tspan><tspan dy="-2"> = </tspan><tspan font-style="italic">e</tspan><tspan font-size="7" dy="2">base,t</tspan><tspan font-size="7" dy="-4">2</tspan><tspan dy="2"> &#x2212; (</tspan><tspan font-style="italic">y</tspan><tspan font-size="7" dy="2">t</tspan><tspan dy="-2"> &#x2212; </tspan><tspan font-style="italic">y</tspan><tspan font-size="7" dy="2">prov,t</tspan><tspan dy="-2">)</tspan><tspan font-size="7" dy="-4">2</tspan></text>
  </g>

  <!-- Bottom: Probation Decision Gate -->
  <g transform="translate(30, 262)" filter="url(#card-shadow)">
    <rect width="740" height="112" fill="#F8FAFC" stroke="#CBD5E1" stroke-width="1.5" rx="6" />
    
    <!-- Gate Header -->
    <text x="20" y="24" font-size="12" font-weight="700" fill="#0F172A">PROBATION DECISION GATE</text>
    <rect x="220" y="10" width="230" height="20" fill="#E0F2FE" rx="10" />
    <text x="335" y="24" font-size="9" font-weight="600" text-anchor="middle" fill="#0369A1">Evaluated at Horizon <tspan font-style="italic">T</tspan><tspan font-size="7.5" dy="2">prob</tspan><tspan dy="-2"> = 50 steps</tspan></text>
    
    <!-- Promotion Branch (Left) -->
    <g transform="translate(20, 36)">
      <rect width="340" height="64" fill="#F0FDF4" stroke="#86EFAC" stroke-width="1.2" rx="4" />
      <text x="12" y="20" font-size="10.5" font-weight="700" fill="#15803D">PROMOTE (Candidate Validated)</text>
      <text x="12" y="38" font-size="9.5" fill="#166534">Condition: Relative MSE Gain &gt; <tspan font-style="italic">&#952;</tspan><tspan font-size="7.5" dy="2">promote</tspan><tspan dy="-2"> (0.05 / &gt;5%)</tspan></text>
      <text x="12" y="53" font-size="9" fill="#475569">Action: <tspan font-style="italic">g</tspan><tspan font-size="7" dy="2">p</tspan><tspan dy="-2"> &#x2192; 1.0 (Coupled to live output), enters ACTIVE state</tspan></text>
    </g>

    <!-- Discard Branch (Right) -->
    <g transform="translate(380, 36)">
      <rect width="340" height="64" fill="#FEF2F2" stroke="#FECACA" stroke-width="1.2" rx="4" />
      <text x="12" y="20" font-size="10.5" font-weight="700" fill="#B91C1C">DISCARD (Candidate Insufficient)</text>
      <text x="12" y="38" font-size="9.5" fill="#991B1B">Condition: Relative MSE Gain &#x2264; <tspan font-style="italic">&#952;</tspan><tspan font-size="7.5" dy="2">promote</tspan><tspan dy="-2"> (&#x2264; 5%)</tspan></text>
      <text x="12" y="53" font-size="9" fill="#475569">Action: Candidate buffers excised, slot returns to DORMANT</text>
    </g>
  </g>
</svg>"""

# -------------------------------------------------------------
# D4: Non-Interfering Shadow Probation (PT-BR Version)
# -------------------------------------------------------------
d4_ptbr_svg = """<svg width="800" height="390" viewBox="0 0 800 390" xmlns="http://www.w3.org/2000/svg" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif">
  <defs>
    <marker id="arr4-pt" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#334155" />
    </marker>
    <filter id="card-shadow-pt" x="-3%" y="-4%" width="106%" height="110%" filterUnits="userSpaceOnUse">
      <feDropShadow dx="1" dy="2" stdDeviation="2" flood-opacity="0.06" />
    </filter>
  </defs>

  <rect width="800" height="390" fill="#FFFFFF" rx="8" />
  
  <!-- Title & Subtitle -->
  <text x="30" y="30" font-size="15" font-weight="700" fill="#0F172A">D4: Estágio Probatório em Sombra Não Interferente</text>
  <text x="30" y="48" font-size="11" fill="#64748B">Candidato provisório aprende contrafactualmente em isolamento sem injetar choque na inferência ativa</text>

  <!-- Left Card: Live Active Predictor -->
  <g transform="translate(30, 68)" filter="url(#card-shadow-pt)">
    <rect width="325" height="180" fill="#F0FDF4" stroke="#86EFAC" stroke-width="1.5" rx="6" />
    <rect x="0" y="0" width="325" height="32" fill="#DCFCE7" rx="6" />
    <text x="15" y="21" font-size="12" font-weight="700" fill="#166534">PREDITOR ATIVO</text>
    <text x="135" y="21" font-size="10" font-weight="500" fill="#15803D">(Modelo Causal em Produção)</text>
    
    <text x="15" y="56" font-size="10.5" font-weight="600" fill="#0F172A">Modelo Linear Base:</text>
    <text x="150" y="56" font-size="10.5" fill="#334155"><tspan font-style="italic">w</tspan><tspan font-size="8" dy="3">base</tspan><tspan dy="-3"> &#x2208; &#x211D;</tspan><tspan font-size="8" dy="-4">D</tspan></text>
    
    <text x="15" y="78" font-size="10.5" font-weight="600" fill="#0F172A">Saída Causal:</text>
    <text x="150" y="78" font-size="10.5" font-weight="700" fill="#15803D">&#375;<tspan font-size="8" dy="3">t</tspan><tspan dy="-3"> = </tspan><tspan font-style="italic">w</tspan><tspan font-size="8" dy="3">base</tspan><tspan font-size="7.5" dy="-5">T</tspan><tspan dy="2" font-style="italic"> x</tspan><tspan font-size="8" dy="3">t</tspan><tspan dy="-3"> + </tspan><tspan font-style="italic">w</tspan><tspan font-size="8" dy="3">s</tspan><tspan dy="-3"> </tspan><tspan font-style="italic">s</tspan><tspan font-size="8" dy="3">t</tspan></text>

    <text x="15" y="100" font-size="10.5" font-weight="600" fill="#0F172A">Papel Operacional:</text>
    <text x="150" y="100" font-size="10" fill="#334155">Conduz ações imediatas no fluxo</text>

    <rect x="15" y="120" width="295" height="46" fill="#FFFFFF" stroke="#86EFAC" rx="4" />
    <text x="162" y="139" font-size="10" font-weight="700" text-anchor="middle" fill="#166534">Caminho de Inferência Protegido</text>
    <text x="162" y="153" font-size="9" text-anchor="middle" fill="#64748B">Acoplamento nulo a parâmetros em teste</text>
  </g>

  <!-- Center: Non-Interference Barrier Column -->
  <g transform="translate(365, 68)">
    <rect width="70" height="180" fill="#F8FAFC" stroke="#CBD5E1" stroke-width="1.2" rx="6" />
    
    <!-- Top Horizontal Header Pill -->
    <rect x="-10" y="-8" width="90" height="24" fill="#1E293B" rx="12" />
    <text x="35" y="8" font-size="8" font-weight="700" text-anchor="middle" fill="#FFFFFF" letter-spacing="0.04em">BARREIRA</text>
    
    <!-- Upper Vertical Dashed Line Segment -->
    <line x1="35" y1="22" x2="35" y2="68" stroke="#64748B" stroke-dasharray="4,3" stroke-width="2" />
    
    <!-- Middle Gate Badge Card -->
    <rect x="4" y="70" width="62" height="42" fill="#FFFFFF" stroke="#0284C7" stroke-width="1.5" rx="4" />
    <text x="35" y="87" font-size="11" font-weight="800" text-anchor="middle" fill="#0F172A"><tspan font-style="italic">g</tspan><tspan font-size="8" dy="2">p</tspan><tspan dy="-2"> = 0,0</tspan></text>
    <text x="35" y="102" font-size="7.5" font-weight="700" text-anchor="middle" fill="#0284C7">PORTÃO</text>

    <!-- Lower Vertical Dashed Line Segment -->
    <line x1="35" y1="114" x2="35" y2="128" stroke="#64748B" stroke-dasharray="4,3" stroke-width="2" />

    <!-- Bottom Isolation Pill Card -->
    <rect x="3" y="130" width="64" height="42" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="1.2" rx="4" />
    <text x="35" y="145" font-size="8" font-weight="700" text-anchor="middle" fill="#334155">Isolamento</text>
    <text x="35" y="156" font-size="8" font-weight="700" text-anchor="middle" fill="#334155">Estrito</text>
    <text x="35" y="167" font-size="7" font-weight="600" text-anchor="middle" fill="#64748B"><tspan font-style="italic">g</tspan><tspan font-size="6" dy="2">p</tspan><tspan dy="-2">&#183;</tspan><tspan font-style="italic">s</tspan><tspan font-size="6" dy="2">p</tspan><tspan dy="-2"> = 0</tspan></text>
  </g>

  <!-- Right Card: Shadow Provisional Candidate -->
  <g transform="translate(445, 68)" filter="url(#card-shadow-pt)">
    <rect width="325" height="180" fill="#FAF5FF" stroke="#D8B4FE" stroke-width="1.5" rx="6" />
    <rect x="0" y="0" width="325" height="32" fill="#F3E8FF" rx="6" />
    <text x="15" y="21" font-size="12" font-weight="700" fill="#7E22CE">CANDIDATO EM SOMBRA</text>
    <text x="185" y="21" font-size="10" font-weight="500" fill="#6B21A8">(Estado <tspan font-style="italic">s</tspan><tspan font-size="8" dy="2">p,t</tspan>)</text>
    
    <text x="15" y="56" font-size="10.5" font-weight="600" fill="#0F172A">Estado Candidato:</text>
    <text x="150" y="56" font-size="10.5" fill="#334155"><tspan font-style="italic">s</tspan><tspan font-size="8" dy="2">p,t</tspan><tspan dy="-2"> (Recorrente Escalar)</tspan></text>
    
    <text x="15" y="78" font-size="10.5" font-weight="600" fill="#0F172A">Saída em Sombra:</text>
    <text x="150" y="78" font-size="10.5" font-weight="700" fill="#7E22CE"><tspan font-style="italic">y</tspan><tspan font-size="8" dy="2">prov,t</tspan><tspan dy="-2"> = </tspan><tspan font-style="italic">y</tspan><tspan font-size="8" dy="2">base,t</tspan><tspan dy="-2"> + </tspan><tspan font-style="italic">w</tspan><tspan font-size="8" dy="2">p</tspan><tspan dy="-2"> </tspan><tspan font-style="italic">s</tspan><tspan font-size="8" dy="2">p,t</tspan></text>

    <text x="15" y="100" font-size="10.5" font-weight="600" fill="#0F172A">Treinamento Local:</text>
    <text x="150" y="100" font-size="10" fill="#334155">RTRL exato em paralelo</text>

    <rect x="15" y="120" width="295" height="46" fill="#FFFFFF" stroke="#D8B4FE" rx="4" />
    <text x="162" y="138" font-size="10" font-weight="700" text-anchor="middle" fill="#7E22CE">Acumulação Contrafactual de Evidência</text>
    <text x="162" y="153" font-size="9" text-anchor="middle" fill="#64748B">&#916;&#8466;<tspan font-size="7" dy="2">t</tspan><tspan dy="-2"> = </tspan><tspan font-style="italic">e</tspan><tspan font-size="7" dy="2">base,t</tspan><tspan font-size="7" dy="-4">2</tspan><tspan dy="2"> &#x2212; (</tspan><tspan font-style="italic">y</tspan><tspan font-size="7" dy="2">t</tspan><tspan dy="-2"> &#x2212; </tspan><tspan font-style="italic">y</tspan><tspan font-size="7" dy="2">prov,t</tspan><tspan dy="-2">)</tspan><tspan font-size="7" dy="-4">2</tspan></text>
  </g>

  <!-- Bottom: Probation Decision Gate -->
  <g transform="translate(30, 262)" filter="url(#card-shadow-pt)">
    <rect width="740" height="112" fill="#F8FAFC" stroke="#CBD5E1" stroke-width="1.5" rx="6" />
    
    <!-- Gate Header -->
    <text x="20" y="24" font-size="12" font-weight="700" fill="#0F172A">PORTÃO DE PROVAÇÃO</text>
    <rect x="220" y="10" width="240" height="20" fill="#E0F2FE" rx="10" />
    <text x="340" y="24" font-size="9" font-weight="600" text-anchor="middle" fill="#0369A1">Avaliado no horizonte <tspan font-style="italic">T</tspan><tspan font-size="7.5" dy="2">prob</tspan><tspan dy="-2"> = 50 passos</tspan></text>
    
    <!-- Promotion Branch (Left) -->
    <g transform="translate(20, 36)">
      <rect width="340" height="64" fill="#F0FDF4" stroke="#86EFAC" stroke-width="1.2" rx="4" />
      <text x="12" y="20" font-size="10.5" font-weight="700" fill="#15803D">PROMOVER (Candidato Validado)</text>
      <text x="12" y="38" font-size="9.5" fill="#166534">Condição: Ganho Relativo &gt; <tspan font-style="italic">&#952;</tspan><tspan font-size="7.5" dy="2">promote</tspan><tspan dy="-2"> (0,05 / &gt;5%)</tspan></text>
      <text x="12" y="53" font-size="9" fill="#475569">Ação: <tspan font-style="italic">g</tspan><tspan font-size="7" dy="2">p</tspan><tspan dy="-2"> &#x2192; 1,0 (Acoplado à predição ativa), entra em ATIVO</tspan></text>
    </g>

    <!-- Discard Branch (Right) -->
    <g transform="translate(380, 36)">
      <rect width="340" height="64" fill="#FEF2F2" stroke="#FECACA" stroke-width="1.2" rx="4" />
      <text x="12" y="20" font-size="10.5" font-weight="700" fill="#B91C1C">DESCARTAR (Ganho Insuficiente)</text>
      <text x="12" y="38" font-size="9.5" fill="#991B1B">Condição: Ganho Relativo &#x2264; <tspan font-style="italic">&#952;</tspan><tspan font-size="7.5" dy="2">promote</tspan><tspan dy="-2"> (&#x2264; 5%)</tspan></text>
      <text x="12" y="53" font-size="9" fill="#475569">Ação: Buffers eliminados, slot retorna para DORMENTE</text>
    </g>
  </g>
</svg>"""
d5_svg = """<svg width="800" height="380" viewBox="0 0 800 380" xmlns="http://www.w3.org/2000/svg" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif">
  <defs>
    <marker id="arr5" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#334155" />
    </marker>
  </defs>

  <rect width="800" height="380" fill="#FFFFFF" rx="8" />
  <text x="30" y="32" font-size="16" font-weight="700" fill="#0F172A">D5: Two-Timescale Relevance &amp; Quiescent Retention</text>
  <text x="30" y="50" font-size="12" fill="#64748B">Decoupling fast instantaneous activity from slow structural relevance bridges silent gaps</text>

  <!-- Graph Axis Area -->
  <g transform="translate(60, 80)">
    <!-- Axes -->
    <line x1="40" y1="180" x2="680" y2="180" stroke="#475569" stroke-width="1.5" marker-end="url(#arr5)" />
    <line x1="40" y1="180" x2="40" y2="20" stroke="#475569" stroke-width="1.5" marker-end="url(#arr5)" />
    
    <text x="690" y="184" font-size="10" font-weight="600" fill="#475569">Time t (steps)</text>
    <text x="35" y="15" font-size="10" font-weight="600" text-anchor="end" fill="#475569">Relevance</text>

    <!-- Quiescent Region Highlight -->
    <rect x="140" y="30" width="380" height="150" fill="#F1F5F9" opacity="0.7" />
    <text x="330" y="48" font-size="11" font-weight="600" text-anchor="middle" fill="#64748B">QUIESCENT INTERVAL (Silence: x_t ~ 0, s_t ~ 0)</text>

    <!-- Event 1 -->
    <rect x="70" y="30" width="70" height="150" fill="#FEF3C7" opacity="0.5" />
    <text x="105" y="48" font-size="10" font-weight="700" text-anchor="middle" fill="#B45309">BURST 1</text>

    <!-- Event 2 -->
    <rect x="520" y="30" width="70" height="150" fill="#FEF3C7" opacity="0.5" />
    <text x="555" y="48" font-size="10" font-weight="700" text-anchor="middle" fill="#B45309">BURST 2</text>

    <!-- Naive Fast Curve (Red Dash) -->
    <path d="M 40 170 L 70 170 L 105 50 L 140 60 L 170 170 L 520 170 L 555 50 L 590 60" 
          stroke="#DC2626" stroke-width="2" stroke-dasharray="4,4" fill="none" />
    
    <!-- LEBRE Slow Curve U_ret (Blue Solid) -->
    <path d="M 40 170 L 70 170 L 105 55 L 140 65 Q 260 95 380 120 T 520 135 L 555 50" 
          stroke="#0284C7" stroke-width="2.5" fill="none" />

    <!-- Eviction Threshold Line -->
    <line x1="40" y1="150" x2="660" y2="150" stroke="#94A3B8" stroke-dasharray="2,2" stroke-width="1.2" />
    <text x="665" y="153" font-size="9" fill="#94A3B8">theta_ret</text>

    <!-- Annotation: Naive Eviction Point -->
    <circle cx="165" cy="150" r="4" fill="#DC2626" />
    <text x="175" y="142" font-size="9" font-weight="700" fill="#DC2626">Naive Eviction (False Loss!)</text>

    <!-- Annotation: LEBRE Survival -->
    <text x="330" y="105" font-size="10" font-weight="700" fill="#0284C7">LEBRE U_ret bridges gap (Memory Preserved &gt; 99%)</text>
  </g>

  <!-- Legend -->
  <g transform="translate(100, 290)">
    <rect width="600" height="70" fill="#F8FAFC" stroke="#CBD5E1" stroke-width="1" rx="4" />
    <line x1="20" y1="25" x2="60" y2="25" stroke="#DC2626" stroke-dasharray="4,4" stroke-width="2" />
    <text x="70" y="29" font-size="10" fill="#0F172A">Instantaneous Activity Tracker (collapses in ~15 steps of silence -&gt; triggers catastrophic eviction)</text>
    
    <line x1="20" y1="50" x2="60" y2="50" stroke="#0284C7" stroke-width="2.5" />
    <text x="70" y="54" font-size="10" fill="#0F172A">LEBRE Slow Relevance U_ret (alpha_slow = 0.005, tau ~ 140 steps -&gt; retains state across Poisson gaps)</text>
  </g>
</svg>
"""

# -------------------------------------------------------------
# D6: Resource Elasticity Across Regimes
# -------------------------------------------------------------
d6_svg = """<svg width="800" height="380" viewBox="0 0 800 380" xmlns="http://www.w3.org/2000/svg" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif">
  <defs>
    <marker id="arr6" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#334155" />
    </marker>
  </defs>

  <rect width="800" height="380" fill="#FFFFFF" rx="8" />
  <text x="30" y="32" font-size="16" font-weight="700" fill="#0F172A">D6: Dynamic Resource Elasticity Across Non-Stationary Regimes</text>
  <text x="30" y="50" font-size="12" fill="#64748B">Observed adaptation trajectory on Task A8 (Linear -&gt; Temporal Lag -&gt; Recurrent -&gt; Baseline)</text>

  <!-- 4 Regime Cards -->
  <!-- Regime 1 -->
  <g transform="translate(40, 80)">
    <rect width="165" height="180" fill="#F8FAFC" stroke="#CBD5E1" stroke-width="1.5" rx="6" />
    <rect x="0" y="0" width="165" height="30" fill="#E2E8F0" rx="6" />
    <text x="82" y="20" font-size="11" font-weight="700" text-anchor="middle" fill="#334155">Regime 1: Linear</text>
    
    <text x="12" y="52" font-size="10" font-weight="600" fill="#0F172A">Demand: Linear Only</text>
    <text x="12" y="70" font-size="10" fill="#64748B">Active: K=5 features</text>
    <text x="12" y="86" font-size="10" fill="#64748B">Lags: 0 | States: 0</text>
    
    <rect x="12" y="110" width="140" height="50" fill="#FFFFFF" stroke="#CBD5E1" rx="4" />
    <text x="82" y="132" font-size="13" font-weight="700" text-anchor="middle" fill="#0284C7">~38 FLOPs/step</text>
    <text x="82" y="148" font-size="9" text-anchor="middle" fill="#64748B">[■■□□□□] Low</text>
  </g>

  <!-- Regime 2 -->
  <g transform="translate(225, 80)">
    <rect width="165" height="180" fill="#F0F9FF" stroke="#BAE6FD" stroke-width="1.5" rx="6" />
    <rect x="0" y="0" width="165" height="30" fill="#E0F2FE" rx="6" />
    <text x="82" y="20" font-size="11" font-weight="700" text-anchor="middle" fill="#0369A1">Regime 2: Delay</text>
    
    <text x="12" y="52" font-size="10" font-weight="600" fill="#0F172A">Demand: Temporal Lag</text>
    <text x="12" y="70" font-size="10" fill="#64748B">Active: Linear + Lags</text>
    <text x="12" y="86" font-size="10" fill="#64748B">Lags: 2 | States: 0</text>
    
    <rect x="12" y="110" width="140" height="50" fill="#FFFFFF" stroke="#BAE6FD" rx="4" />
    <text x="82" y="132" font-size="13" font-weight="700" text-anchor="middle" fill="#0284C7">~65 FLOPs/step</text>
    <text x="82" y="148" font-size="9" text-anchor="middle" fill="#64748B">[■■■□□□] Moderate</text>
  </g>

  <!-- Regime 3 -->
  <g transform="translate(410, 80)">
    <rect width="165" height="180" fill="#FEF3C7" stroke="#FDE68A" stroke-width="1.5" rx="6" />
    <rect x="0" y="0" width="165" height="30" fill="#FEF08A" rx="6" />
    <text x="82" y="20" font-size="11" font-weight="700" text-anchor="middle" fill="#92400E">Regime 3: Recurrent</text>
    
    <text x="12" y="52" font-size="10" font-weight="600" fill="#0F172A">Demand: Feedback State</text>
    <text x="12" y="70" font-size="10" fill="#64748B">Active: Linear + Recurr.</text>
    <text x="12" y="86" font-size="10" fill="#64748B">States: N=1 active</text>
    
    <rect x="12" y="110" width="140" height="50" fill="#FFFFFF" stroke="#FDE68A" rx="4" />
    <text x="82" y="132" font-size="13" font-weight="700" text-anchor="middle" fill="#B45309">~92 FLOPs/step</text>
    <text x="82" y="148" font-size="9" text-anchor="middle" fill="#64748B">[■■■■■□] Higher</text>
  </g>

  <!-- Regime 4 -->
  <g transform="translate(595, 80)">
    <rect width="165" height="180" fill="#ECFDF5" stroke="#A7F3D0" stroke-width="1.5" rx="6" />
    <rect x="0" y="0" width="165" height="30" fill="#D1FAE5" rx="6" />
    <text x="82" y="20" font-size="11" font-weight="700" text-anchor="middle" fill="#065F46">Regime 4: Baseline</text>
    
    <text x="12" y="52" font-size="10" font-weight="600" fill="#0F172A">Demand: Linear Shift</text>
    <text x="12" y="70" font-size="10" fill="#64748B">Evicted: State freed</text>
    <text x="12" y="86" font-size="10" fill="#64748B">Reclaimed budget</text>
    
    <rect x="12" y="110" width="140" height="50" fill="#FFFFFF" stroke="#A7F3D0" rx="4" />
    <text x="82" y="132" font-size="13" font-weight="700" text-anchor="middle" fill="#059669">~40 FLOPs/step</text>
    <text x="82" y="148" font-size="9" text-anchor="middle" fill="#64748B">[■■□□□□] Reclaimed</text>
  </g>

  <!-- Explanatory note -->
  <g transform="translate(40, 280)">
    <rect width="720" height="75" fill="#F8FAFC" stroke="#CBD5E1" stroke-width="1" rx="4" />
    <text x="20" y="26" font-size="11" font-weight="700" fill="#0F172A">CONTRAST WITH STATIC RECURRENT BASELINES (e.g. Minimal GRU, Online ESN):</text>
    <text x="20" y="46" font-size="10" fill="#475569">Static baselines permanently consume &gt;= 280 FLOPs/step across all four regimes, regardless of demand.</text>
    <text x="20" y="62" font-size="10" fill="#059669">LEBRE dynamically scales from 38 FLOPs up to 92 FLOPs (transient peak ~206) and safely returns to 40 FLOPs upon eviction.</text>
  </g>
</svg>
"""

# -------------------------------------------------------------
# D7: Architecture vs Current v0.1 Instantiation Scope
# -------------------------------------------------------------
d7_svg = """<svg width="800" height="400" viewBox="0 0 800 400" xmlns="http://www.w3.org/2000/svg" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif">
  <rect width="800" height="400" fill="#FFFFFF" rx="8" />
  <text x="30" y="32" font-size="16" font-weight="700" fill="#0F172A">D7: Architecture Principle vs. Current v0.1 Instantiation</text>
  <text x="30" y="50" font-size="12" fill="#64748B">Demarcating general architectural principles from certified single-state implementation limits</text>

  <!-- Left Column: General Architectural Principle -->
  <g transform="translate(40, 75)">
    <rect width="345" height="290" fill="#F8FAFC" stroke="#94A3B8" stroke-width="1.5" rx="6" />
    <rect x="0" y="0" width="345" height="35" fill="#E2E8F0" rx="6" />
    <text x="172" y="23" font-size="12" font-weight="700" text-anchor="middle" fill="#1E293B">GENERAL ARCHITECTURAL PRINCIPLE</text>
    
    <text x="15" y="60" font-size="11" font-weight="600" fill="#0F172A">Adaptive Computational Structure:</text>
    <text x="15" y="78" font-size="10" fill="#475569">Structures exist only when justified by evidence</text>
    
    <text x="15" y="106" font-size="11" font-weight="600" fill="#0F172A">Multi-State &amp; Latent Scalability:</text>
    <text x="15" y="124" font-size="10" fill="#475569">Principle permits arbitrary N recurrent states</text>
    
    <text x="15" y="152" font-size="11" font-weight="600" fill="#0F172A">Two-Timescale Quiescent Governance:</text>
    <text x="15" y="170" font-size="10" fill="#475569">Decouples fast activity from slow relevance</text>
    
    <text x="15" y="198" font-size="11" font-weight="600" fill="#0F172A">Asymmetric Obsolescence:</text>
    <text x="15" y="216" font-size="10" fill="#475569">Requires evidence of absence before eviction</text>
    
    <text x="15" y="244" font-size="11" font-weight="600" fill="#0F172A">Substrate Neutral:</text>
    <text x="15" y="262" font-size="10" fill="#475569">Applies to software, neuromorphic, or edge hardware</text>
  </g>

  <!-- Right Column: Current v0.1 Instantiation -->
  <g transform="translate(415, 75)">
    <rect width="345" height="290" fill="#EFF6FF" stroke="#93C5FD" stroke-width="1.5" rx="6" />
    <rect x="0" y="0" width="345" height="35" fill="#DBEAFE" rx="6" />
    <text x="172" y="23" font-size="12" font-weight="700" text-anchor="middle" fill="#1D4ED8">CURRENT v0.1 FROZEN INSTANTIATION</text>
    
    <text x="15" y="60" font-size="11" font-weight="600" fill="#0F172A">Scalar Recurrent Capacity (N &lt;= 1):</text>
    <text x="15" y="78" font-size="10" fill="#1E40AF">Strictly bounded to at most 1 active scalar state</text>
    
    <text x="15" y="106" font-size="11" font-weight="600" fill="#0F172A">Milestone M3 Status:</text>
    <text x="15" y="124" font-size="10" fill="#B91C1C">UNOPENED (multi-state coupling not yet validated)</text>
    
    <text x="15" y="152" font-size="11" font-weight="600" fill="#0F172A">Micro-Resource Operating Point:</text>
    <text x="15" y="170" font-size="10" fill="#1E40AF">Mean 90.44 FLOPs/step, 440 bytes persistent RAM</text>
    
    <text x="15" y="198" font-size="11" font-weight="600" fill="#0F172A">Concrete State Classes:</text>
    <text x="15" y="216" font-size="10" fill="#1E40AF">LinearScalarState &amp; GatedScalarState</text>
    
    <text x="15" y="244" font-size="11" font-weight="600" fill="#0F172A">Empirical Scope Limits:</text>
    <text x="15" y="262" font-size="10" fill="#B91C1C">Boundaries on pure shift registers (A2-A4) &amp; Silverbox (B4)</text>
  </g>
</svg>
"""

# -------------------------------------------------------------
# D8: End-to-End Prequential Step Cycle
# -------------------------------------------------------------
d8_svg = """<svg width="800" height="420" viewBox="0 0 800 420" xmlns="http://www.w3.org/2000/svg" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif">
  <defs>
    <marker id="arr8" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#334155" />
    </marker>
  </defs>

  <rect width="800" height="420" fill="#FFFFFF" rx="8" />
  <text x="30" y="32" font-size="16" font-weight="700" fill="#0F172A">D8: Canonical Prequential Execution Cycle (Step t)</text>
  <text x="30" y="50" font-size="12" fill="#64748B">The 8 ordered phases executed causally on every streaming observation</text>

  <!-- Grid of 8 steps: 4 on top, 4 on bottom -->
  <!-- Step 1 -->
  <g transform="translate(30, 75)">
    <rect width="165" height="135" fill="#F8FAFC" stroke="#CBD5E1" stroke-width="1.5" rx="6" />
    <circle cx="24" cy="24" r="12" fill="#0284C7" />
    <text x="24" y="28" font-size="11" font-weight="700" text-anchor="middle" fill="#FFFFFF">1</text>
    <text x="44" y="28" font-size="12" font-weight="700" fill="#0F172A">OBSERVE</text>
    <text x="12" y="56" font-size="10" fill="#334155">Sample x_t in R^D</text>
    <text x="12" y="74" font-size="10" fill="#64748B">Causal normalization</text>
    <text x="12" y="92" font-size="10" fill="#64748B">Bounded probe bank</text>
    <text x="12" y="110" font-size="9" fill="#94A3B8">Q unallocated probes</text>
  </g>

  <!-- Step 2 -->
  <g transform="translate(225, 75)">
    <rect width="165" height="135" fill="#F0FDF4" stroke="#86EFAC" stroke-width="1.5" rx="6" />
    <circle cx="24" cy="24" r="12" fill="#16A34A" />
    <text x="24" y="28" font-size="11" font-weight="700" text-anchor="middle" fill="#FFFFFF">2</text>
    <text x="44" y="28" font-size="12" font-weight="700" fill="#0F172A">PREDICT</text>
    <text x="12" y="56" font-size="10" fill="#334155">y_base = w_base^T x_t</text>
    <text x="12" y="74" font-size="10" fill="#334155">y_rec = w_s * s_t</text>
    <text x="12" y="92" font-size="10" font-weight="700" fill="#15803D">y_hat = y_base + y_rec</text>
    <text x="12" y="110" font-size="9" fill="#16A34A">Emit y_hat to stream</text>
  </g>

  <!-- Step 3 -->
  <g transform="translate(415, 75)">
    <rect width="165" height="135" fill="#FEF3C7" stroke="#FDE68A" stroke-width="1.5" rx="6" />
    <circle cx="24" cy="24" r="12" fill="#D97706" />
    <text x="24" y="28" font-size="11" font-weight="700" text-anchor="middle" fill="#FFFFFF">3</text>
    <text x="44" y="28" font-size="12" font-weight="700" fill="#0F172A">REVEAL</text>
    <text x="12" y="56" font-size="10" fill="#334155">Target y_t arrives</text>
    <text x="12" y="74" font-size="10" fill="#92400E">Prequential boundary</text>
    <text x="12" y="92" font-size="10" fill="#64748B">Compute error signals:</text>
    <text x="12" y="110" font-size="9" fill="#92400E">e_t &amp; e_base,t</text>
  </g>

  <!-- Step 4 -->
  <g transform="translate(605, 75)">
    <rect width="165" height="135" fill="#FEF2F2" stroke="#FECACA" stroke-width="1.5" rx="6" />
    <circle cx="24" cy="24" r="12" fill="#DC2626" />
    <text x="24" y="28" font-size="11" font-weight="700" text-anchor="middle" fill="#FFFFFF">4</text>
    <text x="44" y="28" font-size="12" font-weight="700" fill="#0F172A">ADAPT PARAMS</text>
    <text x="12" y="56" font-size="10" fill="#334155">NLMS step on w_base</text>
    <text x="12" y="74" font-size="10" fill="#334155">Readout w_s update</text>
    <text x="12" y="92" font-size="10" fill="#334155">RTRL Sensitivity S_t</text>
    <text x="12" y="110" font-size="9" fill="#64748B">Shadow w_prov update</text>
  </g>

  <!-- Step 5 -->
  <g transform="translate(605, 245)">
    <rect width="165" height="135" fill="#FDF4FF" stroke="#F5D0FE" stroke-width="1.5" rx="6" />
    <circle cx="24" cy="24" r="12" fill="#A855F7" />
    <text x="24" y="28" font-size="11" font-weight="700" text-anchor="middle" fill="#FFFFFF">5</text>
    <text x="44" y="28" font-size="12" font-weight="700" fill="#0F172A">UPDATE UTILITY</text>
    <text x="12" y="56" font-size="10" fill="#334155">Delta Loss tracking</text>
    <text x="12" y="74" font-size="10" fill="#334155">C x O observability</text>
    <text x="12" y="92" font-size="10" fill="#334155">Slow U_ret (tau~140)</text>
    <text x="12" y="110" font-size="9" fill="#7E22CE">Obsolescence O_obs</text>
  </g>

  <!-- Step 6 -->
  <g transform="translate(415, 245)">
    <rect width="165" height="135" fill="#EFF6FF" stroke="#BFDBFE" stroke-width="1.5" rx="6" />
    <circle cx="24" cy="24" r="12" fill="#3B82F6" />
    <text x="24" y="28" font-size="11" font-weight="700" text-anchor="middle" fill="#FFFFFF">6</text>
    <text x="44" y="28" font-size="12" font-weight="700" fill="#0F172A">PROBATION</text>
    <text x="12" y="56" font-size="10" fill="#334155">Track shadow gain</text>
    <text x="12" y="74" font-size="10" font-weight="600" fill="#1D4ED8">Age &gt;= T_prob = 50</text>
    <text x="12" y="92" font-size="10" font-weight="600" fill="#1D4ED8">Gain &gt; 5% -&gt; Promote</text>
    <text x="12" y="110" font-size="9" fill="#64748B">Else discard / revert</text>
  </g>

  <!-- Step 7 -->
  <g transform="translate(225, 245)">
    <rect width="165" height="135" fill="#FFF1F2" stroke="#FECDD3" stroke-width="1.5" rx="6" />
    <circle cx="24" cy="24" r="12" fill="#E11D48" />
    <text x="24" y="28" font-size="11" font-weight="700" text-anchor="middle" fill="#FFFFFF">7</text>
    <text x="44" y="28" font-size="12" font-weight="700" fill="#0F172A">EVICTION</text>
    <text x="12" y="56" font-size="10" fill="#334155">Hysteresis patience</text>
    <text x="12" y="74" font-size="10" fill="#BE123C">U_ret &lt; theta_ret</text>
    <text x="12" y="92" font-size="10" fill="#BE123C">O_obs &gt; theta_obs</text>
    <text x="12" y="110" font-size="9" fill="#BE123C">30-step confirmation</text>
  </g>

  <!-- Step 8 -->
  <g transform="translate(30, 245)">
    <rect width="165" height="135" fill="#F0FDF4" stroke="#BBF7D0" stroke-width="1.5" rx="6" />
    <circle cx="24" cy="24" r="12" fill="#15803D" />
    <text x="24" y="28" font-size="11" font-weight="700" text-anchor="middle" fill="#FFFFFF">8</text>
    <text x="44" y="28" font-size="12" font-weight="700" fill="#0F172A">RECLAIM</text>
    <text x="12" y="56" font-size="10" fill="#334155">Deallocate memory</text>
    <text x="12" y="74" font-size="10" fill="#15803D">Excise loops</text>
    <text x="12" y="92" font-size="10" fill="#15803D">Compute drops</text>
    <text x="12" y="110" font-size="9" fill="#64748B">Ready for t+1</text>
  </g>

  <!-- Connectors -->
  <line x1="195" y1="142" x2="225" y2="142" stroke="#475569" stroke-width="1.5" marker-end="url(#arr8)" />
  <line x1="390" y1="142" x2="415" y2="142" stroke="#475569" stroke-width="1.5" marker-end="url(#arr8)" />
  <line x1="580" y1="142" x2="605" y2="142" stroke="#475569" stroke-width="1.5" marker-end="url(#arr8)" />
  <path d="M 687 210 L 687 245" stroke="#475569" stroke-width="1.5" marker-end="url(#arr8)" />
  <line x1="605" y1="312" x2="580" y2="312" stroke="#475569" stroke-width="1.5" marker-end="url(#arr8)" />
  <line x1="415" y1="312" x2="390" y2="312" stroke="#475569" stroke-width="1.5" marker-end="url(#arr8)" />
  <line x1="225" y1="312" x2="195" y2="312" stroke="#475569" stroke-width="1.5" marker-end="url(#arr8)" />
</svg>
"""

diagrams = {
    "lebre_high_level_architecture.svg": d1_svg,
    "lebre_lifecycle.svg": d2_svg,
    "lebre_data_control_flow.svg": d3_svg,
    "lebre_shadow_probation.svg": d4_svg,
    "lebre_shadow_probation_ptbr.svg": d4_ptbr_svg,
    "lebre_quiescent_retention.svg": d5_svg,
    "lebre_resource_elasticity.svg": d6_svg,
    "lebre_v01_scope.svg": d7_svg,
    "lebre_prequential_cycle.svg": d8_svg,
}

for filename, content in diagrams.items():
    p = OUT_DIR / filename
    p.write_text(content.strip(), encoding="utf-8")
    print(f"Generated: {p} ({len(content)} bytes)")

print("All canonical SVGs generated successfully.")
