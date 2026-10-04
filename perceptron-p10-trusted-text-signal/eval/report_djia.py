"""Render the pre-registered DJIA text-utility result: PYTHONPATH=. .venv/bin/python eval/report_djia.py"""
import json
from pathlib import Path

r = json.loads(Path("eval/results/text_utility_djia_v1.json").read_text())
g = json.loads(Path("eval/results/exploratory_djia_gap.json").read_text())
m, P = r["meta"], r["primary"]
f = lambda x: f"{x:.3f}"
pc = lambda x: f"{100 * x:.1f}%"
L = ["# Text-utility test on unseen data — Kaggle DJIA news (pre-registered)", "",
     "Pre-registration: [`eval/preregistration/2026-10-04-text-utility-djia.md`](../preregistration/2026-10-04-text-utility-djia.md) "
     "(commit `dd8bcd1`, 12:55:28 IST, before any run on the real data). Code: `eval/text_utility_djia.py` (unchanged since registration).", "",
     "Reproduce: `bash eval/fetch_djia.sh && PYTHONPATH=. P10_DEVICE=cpu nice -n 10 .venv/bin/python eval/text_utility_djia.py && "
     "PYTHONPATH=. .venv/bin/python eval/exploratory_djia_gap.py && PYTHONPATH=. .venv/bin/python eval/report_djia.py`", "",
     f"Target {m['target']} (next session open-to-close, %). Train {m['train'][0]}→{m['train'][1]} ({m['n_train']}) · calibration "
     f"{m['cal'][0]}→{m['cal'][1]} ({m['n_cal']}) · test {m['test'][0]}→{m['test'][1]} ({m['n_test']} days). α = {m['alpha']}.", "",
     "## Primary result (decision rule applied by the script)", "",
     f"**Decision: {P['decision']}.** Mean Winkler improvement of fusion over price-only = {P['mean_winkler_improvement']:+.4f} "
     f"({100 * P['relative_improvement']:+.2f}% relative); one-sided block-bootstrap p = {P['p_one_sided']:.2f}; "
     f"90% CI of the mean difference [{P['boot_90ci_of_mean'][0]:+.3f}, {P['boot_90ci_of_mean'][1]:+.3f}].", "",
     "| Model | Winkler | Coverage | Mean width | Cov. high-vol | Pinball q05 / q50 / q95 | IC (median) | Our ACI: coverage / width | Linear QR: Winkler / coverage |",
     "|---|---|---|---|---|---|---|---|---|"]
for n, x in r["models"].items():
    pb = x["pinball"]
    L.append(f"| {n} | {f(x['winkler'])} | {pc(x['coverage'])} | {f(x['mean_width'])} | {pc(x['coverage_high_vol'])} | "
             f"{pb['q05']:.4f} / {pb['q50']:.4f} / {pb['q95']:.4f} | {x['ic_spearman_median']:.3f} | {pc(x['aci']['coverage'])} / {f(x['aci']['mean_width'])} | "
             f"{f(x['linear_qr']['winkler'])} / {pc(x['linear_qr']['coverage'])} |")
s = r["secondary_linear_qr"]
L += ["", f"Model-family check (linear quantile regression): improvement {s['mean_winkler_improvement']:+.3f}, one-sided p = {s['p_one_sided']:.3f} "
      "(text makes the linear model worse).", "",
      "## Exploratory (after the run; no decision weight)",
      "- Volatility channel: Spearman correlation of |y| with each text feature on the test period: " +
      ", ".join(f"{k.replace('spearman_abs_y_vs_', '')} {v:+.3f}" for k, v in r["exploratory"].items()) + ".",
      f"- Why price-only is so strong (IC {r['models']['price_only']['ic_spearman_median']:.2f}): the overnight gap continues into the "
      f"open-to-close return (Spearman gap vs y: train {g['train']['spearman_gap_vs_y']:.2f}, test {g['test']['spearman_gap_vs_y']:.2f}; "
      f"the open equals the previous close on {pc(g['test']['frac_open_equals_prev_close'])} of test days). This pattern is consistent with "
      "stale index opening prints (the mechanism is UNVERIFIED: no source opened), so absolute intraday predictability here is not a "
      "tradeable claim. Both arms include the gap, so the text comparison is unaffected.", "",
      "## Reading", "- One index, ≈500 test days: a null result is \"no evidence\", not proof that text never helps.",
      "- Together with StockNet (fusion ≈ price-only on pinball and coverage), we found no setting where text measurably improved "
      "calibrated intervals. The pitch is therefore reframed (see the abstract): trust and coverage guarantees for a text channel, "
      "with dropping text as the k = ∞ end of the price-of-robustness curve."]
Path("eval/results/text_utility_djia_v1.md").write_text("\n".join(L) + "\n")
print("\n".join(L[9:13]))
