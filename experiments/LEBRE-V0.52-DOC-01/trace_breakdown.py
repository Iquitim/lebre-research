"""trace_breakdown.py — aggregates the EXT-01 Renode execution traces (Disassembly format, ~300 steps in the middle of two
development series) by function and by instruction class, with the same per-instruction cycle model as
EXT-01/mcu/cycles_estimate.py. Output: TRACE_BREAKDOWN.csv (series, group_type, group, instructions, cycles)."""
import os, re, sys
from collections import Counter
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "LEBRE-V0.52-EXT-01", "mcu"))
from cycles_estimate import cost
TR = os.path.join(__import__("tempfile").gettempdir(), "claude", "lebre_mcu")
rx = re.compile(r"^0x([0-9a-f]+):\s+([0-9a-f]+)\s+(\S+)\s*(.*?)\s*\[([^\[\]]*)\]$")
rows = []
for tag in ("ons_vg", "bdg2"):
    R = []
    for line in open(os.path.join(TR, f"trace_{tag}.txt"), encoding="utf-8", errors="replace"):
        m = rx.match(line.strip())
        if m:
            R.append((int(m.group(1), 16), len(m.group(2)) // 2, m.group(3).lower(), m.group(4).strip().lower(), m.group(5).strip().replace(' (entry)', '')))
    fi, fc, ki, kc = Counter(), Counter(), Counter(), Counter()
    for j, (pc, sz, mn, ops, fn) in enumerate(R):
        c, k = cost(mn, ops, j + 1 < len(R) and R[j + 1][0] != pc + sz)
        fi[fn] += 1; fc[fn] += c; ki[k.split(":")[0]] += 1; kc[k.split(":")[0]] += c
    for f in fi: rows.append((tag, "function", f, fi[f], fc[f]))
    for k in ki: rows.append((tag, "class", k, ki[k], kc[k]))
    print(tag, len(R), "instr", sum(fc.values()), "cycles", sum(fc.values()) / len(R))
df = pd.DataFrame(rows, columns=["series", "group_type", "group", "instructions", "cycles"])
df.to_csv(os.path.join(HERE, "TRACE_BREAKDOWN.csv"), index=False)
for tag in ("ons_vg", "bdg2"):
    d = df[(df.series == tag)]; tot = d[d.group_type == "class"].cycles.sum()
    print(d.assign(share=d.cycles / tot).sort_values(["group_type", "cycles"], ascending=[True, False]).head(25).to_string(index=False))
