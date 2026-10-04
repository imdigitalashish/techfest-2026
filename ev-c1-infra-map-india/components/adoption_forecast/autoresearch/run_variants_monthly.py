"""Ratchet pass for C9 v2 (monthly eval): rewrite PARAMS_M in forecaster.py, run the frozen eval_monthly.py,
log to results_monthly.tsv, keep the best (must beat best DEV WAPE by > 0.01)."""
import datetime as dt, os, re, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); EST = os.path.join(os.path.dirname(HERE), "forecaster.py")
PY = sys.executable; TSV = os.path.join(HERE, "results_monthly.tsv")
PG = lambda w, phi: {"method": "pooled_growth", "w": w, "phi": phi}  # noqa: E731
SL = lambda k, w, phi: {"method": "share_logit", "k": k, "w": w, "phi": phi}  # noqa: E731
VARIANTS = [
    ("baseline: naive12 (next 12 months = last 12 months)", {"method": "naive12"}),
    ("pooled growth, national only, damped 0.5", PG(0.0, 0.5)),
    ("pooled growth, 50:50 state/national, damped 0.5", PG(0.5, 0.5)),
    ("pooled growth, national only, undamped", PG(0.0, 1.0)),
    ("EV-share logit trend k=2, pooled 50:50, damped 0.5", SL(2, 0.5, 0.5)),
    ("EV-share logit trend k=2, pooled 50:50, undamped", SL(2, 0.5, 1.0)),
    ("EV-share logit trend k=3, pooled 50:50, damped 0.5", SL(3, 0.5, 0.5)),
    ("ensemble: pooled growth (nat, 0.5) + share-logit (k2, 50:50, 0.5)", {"method": "ensemble", "members": [PG(0.0, 0.5), SL(2, 0.5, 0.5)]}),
    ("ensemble: pooled growth (nat, 1.0) + share-logit (k2, 50:50, 1.0)", {"method": "ensemble", "members": [PG(0.0, 1.0), SL(2, 0.5, 1.0)]}),
]
src = open(EST).read(); commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
if not os.path.exists(TSV):
    open(TSV, "w").write("timestamp\tcommit\thypothesis\tmetric_dev_wape_12m\tdelta_vs_best\tkept\tnotes\n")
best, best_params = None, None
for hyp, params in VARIANTS:
    open(EST, "w").write(re.sub(r"^PARAMS_M = .*$", f"PARAMS_M = {params!r}", src, flags=re.M))
    out = subprocess.run([PY, "-W", "ignore", os.path.join(HERE, "eval_monthly.py")], capture_output=True, text=True).stdout
    metric = float(re.search(r"METRIC dev_wape=([\d.]+)", out).group(1))
    delta = None if best is None else metric - best
    kept = best is None or metric < best - 0.01
    if kept:
        best, best_params = metric, params
    sec = re.search(r"secondary (.*)", out).group(1).split(" params=")[0]
    open(TSV, "a").write(f"{dt.datetime.now().isoformat(timespec='seconds')}\t{commit}\t{hyp}\t{metric:.4f}\t"
                         f"{'' if delta is None else f'{delta:+.4f}'}\t{'yes' if kept else 'no'}\t{sec}\n")
    print(f"{metric:.4f} {'KEEP' if kept else 'drop'} | {hyp}")
open(EST, "w").write(re.sub(r"^PARAMS_M = .*$", f"PARAMS_M = {best_params!r}", src, flags=re.M))
print("best:", best, best_params)
