"""one-off: derive eval_v051.py / chronos_v051.py from the v0.5 evaluation scripts (kept for provenance)."""
import os
import shutil

H = os.path.dirname(os.path.abspath(__file__))
V5 = os.path.join(H, "..", "LEBRE-V0.46-STABLE-COMPETITIVE-01")
shutil.copy(os.path.join(V5, "eval_v05.py"), os.path.join(H, "eval_v051.py"))
shutil.copy(os.path.join(V5, "chronos_v05.py"), os.path.join(H, "chronos_v051.py"))
p = os.path.join(H, "eval_v051.py"); s = open(p, encoding="utf-8").read()


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (a[:80], s.count(a))
    s = s.replace(a, b)


rep('"""eval_v05.py — PREREG_V05.md, parts 1-3 (online models). Usage: python eval_v05.py internal|heldout|bench04"""',
    '"""eval_v051.py — PREREG_V051.md (online models). Usage: python eval_v051.py internal|heldout|heldout_v05|bench04"""')
rep('''          os.path.join(ROOT, "data", "external_bench04"), os.path.join(ROOT, "data", "external_v05"), B04, V03, HERE, ROOT):''',
    '''          os.path.join(ROOT, "data", "external_bench04"), os.path.join(ROOT, "data", "external_v05"),
          os.path.join(ROOT, "data", "external_v051"), os.path.join(ROOT, "experiments", "LEBRE-V0.46-STABLE-COMPETITIVE-01"),
          B04, V03, HERE, ROOT):''')
rep('import load05  # noqa: E402', 'import load05  # noqa: E402\nimport load051  # noqa: E402')
rep('from lebre_v05 import LebreV05  # noqa: E402', 'from lebre_v05 import LebreV05  # noqa: E402\nfrom lebre_v051 import LebreV051  # noqa: E402')
rep('SEEDS_INT = list(range(2501, 2531))', 'SEEDS_INT = list(range(2561, 2591))')
rep('''    for f, h in (("PREREG_V05.md", "PREREG_V05_SHA256.txt"), ("lebre_v05.py", "FREEZE_V05_SHA256.txt"),
                 ("lebre_v045.py", "FREEZE_V045_COPY_SHA256.txt")):''',
    '''    for f, h in (("PREREG_V051.md", "PREREG_V051_SHA256.txt"), ("lebre_v051.py", "FREEZE_V051_SHA256.txt"),
                 ("lebre_s051.py", "FREEZE_S051_SHA256.txt")):''')
rep('''    m = {"V032": lambda: B.LebreStep(5).m, "V045": lambda: LebreV045(d=5), "V05": lambda: LebreV05(d=5)}[arm]()''',
    '''    m = {"V045": lambda: LebreV045(d=5), "V05": lambda: LebreV05(d=5), "V051": lambda: LebreV051(d=5)}[arm]()''')
rep('''        if arm == "V05":
            yh, parts = m.explain_prediction(); faith = max(faith, abs(yh - sum(c for _, c in parts)) / max(1.0, abs(yh)))
        if t in checks:
            s = m.A if arm == "V05" else m''',
    '''        if arm in ("V05", "V051"):
            yh, parts = m.explain_prediction(); faith = max(faith, abs(yh - sum(c for _, c in parts)) / max(1.0, abs(yh)))
        if t in checks:
            s = m.A if arm == "V05" else (m.S if arm == "V051" else m)''')
rep('''"nmse": float(np.mean(err ** 2) / np.var(y)), "fp": float(fps.mean()),''',
    '''"nmse": float(np.mean(err ** 2) / np.var(y)), "fp": float(fps.mean()), "fp_peak": float(fps.max()),''')
rep('''    if arm in ("V045", "V05"):
        out["coverage"] = m.cover_hits / m.cover_n
    if arm == "V05":
        out["faith_rel"] = faith; out["w_structural_final"] = float(m.wts[0])''',
    '''    out["coverage"] = m.cover_hits / m.cover_n
    if arm in ("V05", "V051"):
        out["faith_rel"] = faith; out["w_structural_final"] = float(m.wts[0])''')
rep('''class V05Step(B.Step):
    def __init__(self, d, season, ts):
        self.m = LebreV05(d=d, season=season); self.t = 0''',
    '''class V05Step(B.Step):
    def __init__(self, d, season, ts, cls=LebreV05):
        self.m = cls(d=d, season=season); self.t = 0''')
rep('''HELD_MODELS = ["LEBRE_V05", "LEBRE_V045", "LEBRE_V032",''', '''HELD_MODELS = ["LEBRE_V051", "LEBRE_V05", "LEBRE_V045", "LEBRE_V032",''')
rep('''    L = load05 if src == "held" else load04
    X, y, _, _, s, _ = L.load(task); ts = int(0.30 * len(X))
    if model_id == "LEBRE_V05":
        m, step = V05Step(X.shape[1], s, ts), True''',
    '''    L = {"held": load051, "held05": load05, "b04": load04}[src]
    X, y, _, _, s, _ = L.load(task); ts = int(0.30 * len(X))
    if model_id == "LEBRE_V051":
        m, step = V05Step(X.shape[1], s, ts, LebreV051), True
    elif model_id == "LEBRE_V05":
        m, step = V05Step(X.shape[1], s, ts), True''')
rep('''    if model_id in ("LEBRE_V05", "LEBRE_V045"):''', '''    if model_id in ("LEBRE_V051", "LEBRE_V05", "LEBRE_V045"):''')
rep('''    if model_id == "LEBRE_V05":
        out["faith_rel"] = m.faith; out["w_final"]''', '''    if model_id in ("LEBRE_V051", "LEBRE_V05"):
        out["faith_rel"] = m.faith; out["w_final"]''')
rep('''    L = load05 if src == "held" else load04
    X, y, _, _, s, _ = L.load(task); T = len(X); ts = int(0.30 * T)
    sc = CausalStandardScaler(d=X.shape[1])
    m = {"V05": lambda: LebreV05(d=X.shape[1], season=s),''',
    '''    L = {"held": load051, "held05": load05, "b04": load04}[src]
    X, y, _, _, s, _ = L.load(task); T = len(X); ts = int(0.30 * T)
    sc = CausalStandardScaler(d=X.shape[1])
    m = {"V051": lambda: LebreV051(d=X.shape[1], season=s), "V05": lambda: LebreV05(d=X.shape[1], season=s),''')
rep('''    K4.load = load05.load            # set inside each worker''', '''    K4.load = load051.load           # set inside each worker''')
rep('''def calib(tasks):
    K4.load = load05.load''', '''def calib(tasks):
    K4.load = load051.load''')
rep('''load05.load(t)[4] is None and c["gamma"] != 0.05)]''', '''load051.load(t)[4] is None and c["gamma"] != 0.05)]''')
rep('''for a in ("V032", "V045", "V05")]''', '''for a in ("V045", "V05", "V051")]''')
rep('"INTERNAL_V05_RESULTS.csv"', '"INTERNAL_V051_RESULTS.csv"')
rep('''        tasks = list(load05.TASKS)''', '''        tasks = list(load051.TASKS)''')
rep('''(["CTRL_SEASONAL_NAIVE"] if load05.load(t)[4] else [])''', '''(["CTRL_SEASONAL_NAIVE"] if load051.load(t)[4] else [])''')
rep('"HELDOUT_V05_RESULTS.csv"', '"HELDOUT_V051_RESULTS.csv"')
rep('''for a in ("V05", "V045", "V032", "NLIN") for o in OFFSETS]''', '''for a in ("V051", "V05", "NLIN") for o in OFFSETS]''')
rep('''            pd.DataFrame(list(ex.map(offset_one, ojobs, chunksize=1))).to_csv(os.path.join(HERE, "HELDOUT_V05_OFFSETS.csv"), index=False)''',
    '''            pd.DataFrame(list(ex.map(offset_one, ojobs, chunksize=1))).to_csv(os.path.join(HERE, "HELDOUT_V051_OFFSETS.csv"), index=False)
    elif part == "heldout_v05":
        jobs = [("held05", t, "LEBRE_V051", s, {}) for t in load05.TASKS for s in SEEDS_EXT]
        with ProcessPoolExecutor(16) as ex:
            pd.DataFrame(list(ex.map(ext_one, jobs, chunksize=1))).to_csv(os.path.join(HERE, "HELDOUT05_V051_RESULTS.csv"), index=False)''')
rep('''jobs = [("b04", t, "LEBRE_V05", s, {}) for t in load04.TASKS for s in SEEDS_EXT]''', '''jobs = [("b04", t, "LEBRE_V051", s, {}) for t in load04.TASKS for s in SEEDS_EXT]''')
rep('"BENCH04_V05_RESULTS.csv"', '"BENCH04_V051_RESULTS.csv"')
rep('''for a in ("V05", "NLIN") for o in OFFSETS]''', '''for a in ("V051",) for o in OFFSETS]''')
rep('"BENCH04_V05_OFFSETS.csv"', '"BENCH04_V051_OFFSETS.csv"')
open(p, "w", encoding="utf-8").write(s)

q = os.path.join(H, "chronos_v051.py"); t = open(q, encoding="utf-8").read()
for a, b in [('"""chronos_v05.py — PREREG_V05.md', '"""chronos_v051.py — PREREG_V051.md'),
             ('os.path.join(ROOT, "data", "external_v05")):', 'os.path.join(ROOT, "data", "external_v051")):'),
             ('import load05  # noqa: E402', 'import load051 as load05  # noqa: E402'),
             ('    import eval_v05\n    eval_v05.check()', '    import eval_v051\n    eval_v051.check()'),
             ('"HELDOUT_CHRONOS_RESULTS.csv"', '"HELDOUT_V051_CHRONOS_RESULTS.csv"')]:
    assert t.count(a) == 1, a
    t = t.replace(a, b)
open(q, "w", encoding="utf-8").write(t)
print("ok")
