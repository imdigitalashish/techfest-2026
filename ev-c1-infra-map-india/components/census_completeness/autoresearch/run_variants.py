"""Lead-driven first pass of the ratchet: rewrite PARAMS in estimator.py, run the frozen eval, log to results.tsv,
keep the best. (Later passes: an agent edits estimator.py code following program.md.)"""
import datetime as dt, os, re, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); EST = os.path.join(os.path.dirname(HERE), "estimator.py")
PY = sys.executable; TSV = os.path.join(HERE, "results.tsv")
VARIANTS = [
    ("baseline: two-source Chapman, r=150 m, union fallback if m<3", {"mode": "chapman", "radius_m": 150, "min_matches": 3}),
    ("union only (no completeness correction)", {"mode": "union", "radius_m": 150, "min_matches": 3}),
    ("Chapman, tighter radius r=50 m", {"mode": "chapman", "radius_m": 50, "min_matches": 3}),
    ("Chapman, looser radius r=500 m", {"mode": "chapman", "radius_m": 500, "min_matches": 3}),
    ("calibration: ln(official) ~ ln(BEV regs) only (no charger data)", {"mode": "calib", "radius_m": 150, "min_matches": 3}),
    ("calibration: ln(official) ~ ln(BEV regs) + ln(union)", {"mode": "calib", "obs": "union", "radius_m": 150, "min_matches": 3}),
    ("calibration: ln(official) ~ ln(BEV regs) + ln(Chapman)", {"mode": "calib", "obs": "chapman", "radius_m": 150, "min_matches": 3}),
]
src = open(EST).read(); commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
if not os.path.exists(TSV):
    open(TSV, "w").write("timestamp\tcommit\thypothesis\tmetric_dev_median_abs_log_err\tdelta_vs_best\tkept\tnotes\n")
best, best_params = None, None
for hyp, params in VARIANTS:
    open(EST, "w").write(re.sub(r"^PARAMS = .*$", f"PARAMS = {params!r}", src, flags=re.M))
    out = subprocess.run([PY, "-W", "ignore", os.path.join(HERE, "eval.py")], capture_output=True, text=True).stdout
    metric = float(re.search(r"METRIC dev_median_abs_log_err=([\d.]+)", out).group(1))
    delta = None if best is None else metric - best
    kept = best is None or metric < best - 0.02  # noise margin
    if kept:
        best, best_params = metric, params
    sec = re.search(r"secondary (.*)", out).group(1).split(" params=")[0]
    open(TSV, "a").write(f"{dt.datetime.now().isoformat(timespec='seconds')}\t{commit}\t{hyp}\t{metric:.4f}\t"
                         f"{'' if delta is None else f'{delta:+.4f}'}\t{'yes' if kept else 'no'}\t{sec}\n")
    print(f"{metric:.4f} {'KEEP' if kept else 'drop'} | {hyp}")
open(EST, "w").write(re.sub(r"^PARAMS = .*$", f"PARAMS = {best_params!r}", src, flags=re.M))
print("best:", best, best_params)
