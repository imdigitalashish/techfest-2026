"""Lead-driven first pass of the ratchet: rewrite PARAMS in estimator.py, run the frozen eval, log to results.tsv,
keep the best. (Later passes: an agent edits estimator.py code following program.md.)"""
import datetime as dt, os, re, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); EST = os.path.join(os.path.dirname(HERE), "forecaster.py")
PY = sys.executable; TSV = os.path.join(HERE, "results.tsv")
VARIANTS = [
    ("baseline: naive (next year = this year)", {"method": "naive"}),
    ("1-year growth extrapolation (CAGR-style)", {"method": "growth", "phi": 1.0}),
    ("damped growth phi=0.5", {"method": "growth", "phi": 0.5}),
    ("pooled growth: state/national 50:50, phi=0.5", {"method": "pooled_growth", "w": 0.5, "phi": 0.5}),
    ("pooled growth: national only, phi=0.5", {"method": "pooled_growth", "w": 0.0, "phi": 0.5}),
    ("EV-share logistic trend (k=3), pooled 50:50", {"method": "share_logit", "k": 3, "w": 0.5, "phi": 1.0}),
    ("EV-share logistic trend (k=3), pooled 50:50, damped 0.5", {"method": "share_logit", "k": 3, "w": 0.5, "phi": 0.5}),
    ("EV-share logistic trend (k=2), pooled 50:50, damped 0.5", {"method": "share_logit", "k": 2, "w": 0.5, "phi": 0.5}),
]
src = open(EST).read(); commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
if not os.path.exists(TSV):
    open(TSV, "w").write("timestamp\tcommit\thypothesis\tmetric_dev_wape\tdelta_vs_best\tkept\tnotes\n")
best, best_params = None, None
for hyp, params in VARIANTS:
    open(EST, "w").write(re.sub(r"^PARAMS = .*$", f"PARAMS = {params!r}", src, flags=re.M))
    out = subprocess.run([PY, "-W", "ignore", os.path.join(HERE, "eval.py")], capture_output=True, text=True).stdout
    metric = float(re.search(r"METRIC dev_wape=([\d.]+)", out).group(1))
    delta = None if best is None else metric - best
    kept = best is None or metric < best - 0.01  # noise margin
    if kept:
        best, best_params = metric, params
    sec = re.search(r"secondary (.*)", out).group(1).split(" params=")[0]
    open(TSV, "a").write(f"{dt.datetime.now().isoformat(timespec='seconds')}\t{commit}\t{hyp}\t{metric:.4f}\t"
                         f"{'' if delta is None else f'{delta:+.4f}'}\t{'yes' if kept else 'no'}\t{sec}\n")
    print(f"{metric:.4f} {'KEEP' if kept else 'drop'} | {hyp}")
open(EST, "w").write(re.sub(r"^PARAMS = .*$", f"PARAMS = {best_params!r}", src, flags=re.M))
print("best:", best, best_params)
