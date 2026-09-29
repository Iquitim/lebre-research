"""gen_data.py — writes series_data.h with one DEVELOPMENT series (raw inputs as float32, target with NaN for missing,
quarantine flags) for the firmware. Usage: gen_data.py <task> [final]  (final: pre-registered reserve run only)"""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..", "LEBRE-V0.52-PROTO-01")))
import data_v052 as D
task = sys.argv[1]
final = len(sys.argv) > 2 and sys.argv[2] == "final"
d = D.load(task, final=final)            # development unless the pre-registered run passes 'final'
X, y, q, s = d["X"].astype(np.float32), d["y"].astype(np.float32), d["quarantine"].astype(np.uint8), d["season"] or 0
s2 = 168 if task.startswith("bdg2") else 0
fl = lambda v: "NAN" if not np.isfinite(v) else repr(float(v)) + "f"
with open(os.path.join(HERE, "series_data.h"), "w", encoding="utf-8", newline="\n") as f:
    f.write(f"/* {task} */\n#include <math.h>\n#define SER_T {len(y)}\n#define SER_DX {X.shape[1]}\n")
    f.write(f"#define SER_SEASON {s}\n#define SER_SEASON2 {s2}\n")
    f.write("static const float ser_x[] = {" + ",".join(fl(v) for v in X.ravel()) + "};\n")
    f.write("static const float ser_y[] = {" + ",".join(fl(v) for v in y) + "};\n")
    f.write("static const unsigned char ser_q[] = {" + ",".join(str(int(v)) for v in q) + "};\n")
print(task, "T", len(y), "dx", X.shape[1], "season", s, s2)
