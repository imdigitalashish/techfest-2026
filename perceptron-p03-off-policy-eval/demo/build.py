"""Build demo/index.html: one self-contained offline page (vanilla JS + inline SVG, no network, system fonts).

Reproduce (from perceptron-p03-off-policy-eval/; standard library only, any python3 >= 3.8):
  python3 demo/build.py                 # writes demo/index.html
  python3 demo/build.py --out /tmp/x.html
Every number on the page is read from a committed result file or computed here from one (see demo/README.md):
  eval/results/obd_slice.json · gate_obd_posthoc.json · obd_block_bootstrap.json · headline.json · decomposer_review.json ·
  sim_bank_runs.csv · demo/results/knob_results.json (pre-registered knob analysis) · demo/data/extract_manifest.json.
Formatted numbers that also appear in eval/results/headline.json are asserted equal to it (the abstract's numbers).
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "eval" / "results"
DEMO = ROOT / "demo"
Z = 1.959963984540054
MINUS = "\u2212"
INPUTS = ["eval/results/obd_slice.json", "eval/results/gate_obd_posthoc.json", "eval/results/obd_block_bootstrap.json",
          "eval/results/headline.json", "eval/results/decomposer_review.json", "eval/results/sim_bank_runs.csv",
          "eval/gate_rule.json", "demo/results/knob_results.json", "demo/data/extract_manifest.json"]


def jload(rel):
    return json.loads((ROOT / rel).read_text())


def sgn(x, d=2, plus=True):
    s = f"{abs(x):.{d}f}"
    if round(x, d) == 0:
        return s
    return (MINUS if x < 0 else ("+" if plus else "")) + s


def k(x, d=2, plus=True):
    """A click rate or difference as clicks per 1,000 impressions."""
    return sgn(1000 * x, d, plus)


def grp(n):
    return f"{n:,.0f}"


def esc(s):
    return html.escape(str(s), quote=True)


def num(text, src, cls="n"):
    return f'<span class="{cls}" data-src="{esc(src)}" tabindex="0">{esc(text)}</span>'


def ans(text, src):
    return f'<span class="ans n" data-src="{esc(src)}" tabindex="0">{esc(text)}</span>'


def stamp(kind, text):
    return f'<span class="stamp stamp-{kind}">{esc(text)}</span>'


def r6(x):
    return float(f"{x:.6g}")


class Checks:
    def __init__(self, hl):
        self.hl, self.done = hl["display"], []

    def eq(self, key, ours):
        want = self.hl[key]
        assert ours == want, f"headline.json display.{key} = {want!r} but the page would show {ours!r}"
        self.done.append(key)
        return ours


# ----------------------------------------------------------------------------------------------------------------- data
def sheet1(pre, gp, bb, ck):
    A, B = pre["a3_halves"]["A_deploy_BTS"], pre["a3_halves"]["B_rollback_to_Random"]
    c = pre["a3_halves"]["cells"]
    S = "eval/results/obd_slice.json → "
    d = {}
    d["B2"] = num(k(c["B2"]["v"], 3, False), S + "a3_halves.cells.B2.v ×1000 (BTS arm, last 42 h)")
    d["R1"] = num(k(c["R1"]["v"], 3, False), S + "a3_halves.cells.R1.v ×1000 (Random arm, first 42 h)")
    d["R2"] = num(k(c["R2"]["v"], 3, False), S + "a3_halves.cells.R2.v ×1000 (Random arm, last 42 h)")
    d["naive"] = ans(ck.eq("a3A_naive_k", k(A["naive"])), S + "a3_halves.A_deploy_BTS.naive ×1000")
    d["naive_hw"] = num("±" + k(Z * A["naive_se"], 2, False), S + "a3_halves.A_deploy_BTS.naive_se ×1.96 ×1000")
    d["ref"] = ans(ck.eq("a3A_truth_k", k(A["truth"])), S + "a3_halves.A_deploy_BTS.truth ×1000 (concurrent A/B arms)")
    d["ref_hw"] = num("±" + k(Z * A["truth_se"], 2, False), S + "a3_halves.A_deploy_BTS.truth_se ×1.96 ×1000")
    d["env"] = num(k(A["true_env_old"]), S + "a3_halves.A_deploy_BTS.true_env_old ×1000 (= R2 − R1)")
    d["env_pct"] = num(f"{c['R2']['v'] / c['R1']['v'] - 1:.0%}", S + "a3_halves.cells.R2.v / R1.v − 1")
    d["overstate"] = num(ck.eq("a3A_overstate", f"{A['naive'] / A['truth'] - 1:.0%}"), S + "a3_halves.A_deploy_BTS.naive / truth − 1")
    dr = A["DR"]
    vhat = c["B2"]["v"] - dr["policy_effect_after"]
    d["dr_vhat"] = num(k(vhat, 3, False), S + "a3_halves.cells.B2.v − a3_halves.A_deploy_BTS.DR.policy_effect_after, ×1000 (DR estimate of the Random arm's last-42-h rate, from BTS logs)")
    d["dr"] = ans(ck.eq("a3A_dr_k", k(dr["policy_effect_after"])), S + "a3_halves.A_deploy_BTS.DR.policy_effect_after ×1000")
    lo, hi = dr["policy_effect_after"] - Z * dr["se"], dr["policy_effect_after"] + Z * dr["se"]
    d["dr_ci"] = (num(ck.eq("a3A_dr_lo", k(lo)), S + "a3_halves.A_deploy_BTS.DR (policy_effect_after − 1.96·se) ×1000") + " … " +
                  num(ck.eq("a3A_dr_hi", k(hi)), S + "a3_halves.A_deploy_BTS.DR (policy_effect_after + 1.96·se) ×1000"))
    hb = bb["halves_A"]
    d["dr_block"] = (num(ck.eq("bb_A_lo", k(hb["block_lo"])), "eval/results/obd_block_bootstrap.json → halves_A.block_lo ×1000") + " … " +
                     num(ck.eq("bb_A_hi", k(hb["block_hi"])), "eval/results/obd_block_bootstrap.json → halves_A.block_hi ×1000"))
    d["ipw"] = num(k(A["IPW"]["policy_effect_after"]), S + "a3_halves.A_deploy_BTS.IPW.policy_effect_after ×1000")
    g = next(x for x in gp["cases"] if x["case"] == "halves · A deploy BTS")
    G = "eval/results/gate_obd_posthoc.json → cases['halves · A deploy BTS']."
    d["ess_pct"] = num(ck.eq("a3A_ess_pct", f"{g['ess_frac']:.1%}"), G + "ess_frac")
    d["ess_pct2"] = num(f"{g['ess_frac']:.2%}", G + "ess_frac")
    d["n_after"] = num(grp(g["n"]), G + "n (BTS impressions in the last 42 h)")
    d["ess_abs"] = num(grp(g["ess_abs"]), G + "ess_abs = ess_frac × n")
    d["z"] = num(sgn(g["z_mean_w"], 1), G + "z_mean_w")
    d["max_w"] = num(grp(g["max_w"]), G + "max_w = (1/80) / smallest logged propensity")
    d["min_ps"] = num(f"{(1 / 80) / g['max_w']:.6f}", G + "(1/80) / max_w (the smallest logged propensity in the last 42 h)")
    assert not g["answer"]
    # pre-registered secondary whole-day pair 25 -> 26 (deploy direction): the failure
    p = pre["a3_daypairs"]["2019-11-25→2019-11-26"]["A_deploy_BTS"]
    P = S + "a3_daypairs['2019-11-25→2019-11-26'].A_deploy_BTS."
    gd = next(x for x in gp["cases"] if x["case"] == "2019-11-25→2019-11-26 · A deploy BTS")
    d["f_dr"] = ans(k(p["DR"]["policy_effect_after"]), P + "DR.policy_effect_after ×1000")
    d["f_dr_plain"] = num(k(p["DR"]["policy_effect_after"]), P + "DR.policy_effect_after ×1000")
    d["f_ci"] = (num(k(p["DR"]["policy_effect_after"] - Z * p["DR"]["se"]), P + "DR (policy_effect_after − 1.96·se) ×1000") + " … " +
                 num(k(p["DR"]["policy_effect_after"] + Z * p["DR"]["se"]), P + "DR (policy_effect_after + 1.96·se) ×1000"))
    d["f_ref"] = ans(k(p["truth"]), P + "truth ×1000 (concurrent A/B arms on 26 Nov)")
    d["f_ref_plain"] = num(k(p["truth"]), P + "truth ×1000 (concurrent A/B arms on 26 Nov)")
    d["f_naive"] = num(k(p["naive"]), P + "naive ×1000")
    d["f_ess"] = num(f"{gd['ess_frac']:.2%}", "eval/results/gate_obd_posthoc.json → cases['2019-11-25→2019-11-26 · A deploy BTS'].ess_frac")
    assert not gd["answer"] and not p["DR"]["S1_ci_contains_0"]
    u = gp["summary"]["unique_instances"]
    U = "eval/results/gate_obd_posthoc.json → summary.unique_instances."
    d["t_listed"] = num(str(u["listed"]), U + "listed")
    d["t_answered"] = num(ck.eq("gate_obd_u_answered", f"{u['answered']}/{u['listed']}"), U + "answered / listed")
    d["t_refin"] = num(ck.eq("gate_obd_u_ref_in_ci", f"{u['answered_ref_in_ci']}/{u['answered']}"), U + "answered_ref_in_ci / answered")
    d["t_refused"] = num(ck.eq("gate_obd_u_s1rej_abst", f"{u['abstained_s1_rejected']}/{u['s1_rejected_total']}"), U + "abstained_s1_rejected / s1_rejected_total")
    d["t_wrong"] = num(ck.eq("gate_obd_u_wrongsign", f"{u['answered_confident_wrong_sign']}/{u['answered_effect_rows']}"), U + "answered_confident_wrong_sign / answered_effect_rows")
    # reverse switch (roll back to Random)
    Bs = S + "a3_halves.B_rollback_to_Random."
    d["b_naive"] = num(ck.eq("a3B_naive_k", k(B["naive"])), Bs + "naive ×1000")
    d["b_ref"] = num(ck.eq("a3B_truth_k", k(B["truth"])), Bs + "truth ×1000")
    d["b_dr"] = num(ck.eq("a3B_dr_k", k(B["DR"]["policy_effect_after"])), Bs + "DR.policy_effect_after ×1000")
    d["b_ci"] = (num(k(B["DR"]["policy_effect_after"] - Z * B["DR"]["se"]), Bs + "DR (policy_effect_after − 1.96·se) ×1000") + " … " +
                 num(k(B["DR"]["policy_effect_after"] + Z * B["DR"]["se"]), Bs + "DR (policy_effect_after + 1.96·se) ×1000"))
    gb = next(x for x in gp["cases"] if x["case"] == "halves · B roll back")
    d["b_ess"] = num(f"{gb['ess_frac']:.1%}", "eval/results/gate_obd_posthoc.json → cases['halves · B roll back'].ess_frac")
    assert gb["answer"] and B["DR"]["policy_effect_after"] + Z * B["DR"]["se"] < 0
    w = pre["window"]
    d["half"] = num(str(w["hours"] // 2), S + "window.hours / 2 (the pre-registered split at the midpoint)")
    d["n_random"] = num(ck.eq("obd_rows_random", grp(w["n_random"])), S + "window.n_random")
    d["n_bts"] = num(ck.eq("obd_rows_bts", grp(w["n_bts"])), S + "window.n_bts")
    d["hours"] = num(ck.eq("obd_hours", str(w["hours"])), S + "window.hours")
    svg = waterfall_real(A, dr)
    return d, svg


def waterfall_real(A, dr):
    """REAL waterfall: dashboard = policy (A/B) + environment; DR's split dashed."""
    pol, env, naive, drp = 1000 * A["truth"], 1000 * A["true_env_old"], 1000 * A["naive"], 1000 * dr["policy_effect_after"]
    W, H, x0, top, bot = 560, 300, 64, 24, 250
    ymax = 1.9
    y = lambda v: bot - (bot - top) * v / ymax
    bars = [("Policy", "A/B check", 0.0, pol, "var(--ok)"), ("The week", "Random's own rate", pol, pol + env, "var(--ink-3)"),
            ("Dashboard", "after − before", 0.0, naive, "var(--ink)")]
    out = [f'<svg class="wf" viewBox="0 0 {W} {H}" role="img" aria-label="Waterfall: dashboard {naive:+.2f} per 1,000 equals policy {pol:+.2f} plus the week {env:+.2f}">']
    for t in (0, 0.5, 1.0, 1.5):
        out.append(f'<line x1="{x0}" x2="{W - 8}" y1="{y(t):.1f}" y2="{y(t):.1f}" class="gridln"/>'
                   f'<text x="{x0 - 8}" y="{y(t) + 5:.1f}" class="tick" text-anchor="end">{t:+.1f}</text>' if t else
                   f'<line x1="{x0}" x2="{W - 8}" y1="{y(0):.1f}" y2="{y(0):.1f}" class="axis"/>'
                   f'<text x="{x0 - 8}" y="{y(0) + 5:.1f}" class="tick" text-anchor="end">0</text>')
    bw, gap = 112, 52
    for i, (lab, sub, a, b, col) in enumerate(bars):
        bx = x0 + 34 + i * (bw + gap)
        out.append(f'<rect x="{bx}" y="{y(max(a, b)):.1f}" width="{bw}" height="{abs(y(a) - y(b)):.1f}" fill="{col}" opacity="{0.9 if i != 1 else 0.55}"/>')
        if i == 0:
            out.append(f'<text x="{bx + bw / 2}" y="{y(b) + 28:.1f}" class="barval" text-anchor="middle" style="fill:#f6f9f2">{sgn(b - a)}</text>')
        else:
            out.append(f'<text x="{bx + bw / 2}" y="{y(max(a, b)) - 10:.1f}" class="barval" text-anchor="middle">{sgn(b - a)}</text>')
        out.append(f'<text x="{bx + bw / 2}" y="{bot + 22}" class="barlab" text-anchor="middle">{lab}</text>'
                   f'<text x="{bx + bw / 2}" y="{bot + 40}" class="barsub" text-anchor="middle">{sub}</text>')
        if i < 2:
            out.append(f'<line x1="{bx + bw}" x2="{bx + bw + gap}" y1="{y(b):.1f}" y2="{y(b):.1f}" class="connector"/>')
    bx = x0 + 34
    out.append(f'<rect x="{bx - 6}" y="{y(drp):.1f}" width="{bw + 12}" height="{y(0) - y(drp):.1f}" class="drbox"/>'
               f'<text x="{bx - 6}" y="{y(drp) - 10:.1f}" class="drlab">DR, logs only: {sgn(drp)}</text>')
    out.append("</svg>")
    return "".join(out)


def sheet2(pre, gp, bb, ck):
    a2 = pre["a2"]
    S = "eval/results/obd_slice.json → a2."
    d = {"truth": ans(ck.eq("obd_ctr_bts_k3", k(a2["truth"], 3, False)), S + "truth ×1000 (BTS arm's own click rate in the 84 h)"),
         "truth_plain": num(k(a2["truth"], 3, False), S + "truth ×1000 (BTS arm's own click rate in the 84 h)"),
         "truth_hw": num("±" + k(Z * a2["truth_se"], 3, False), S + "truth_se ×1.96 ×1000"),
         "dr": ans(ck.eq("a2_hourly_dr_k3", k(a2["P-hourly"]["DR"]["value"], 3, False)), S + "P-hourly.DR.value ×1000"),
         "dr_relerr": num(ck.eq("a2_hourly_dr_relerr", f"{a2['P-hourly']['DR']['rel_err']:.1%}"), S + "P-hourly.DR.rel_err"),
         "n": num(grp(a2["P-hourly"]["n"]), S + "P-hourly.n (Random-arm impressions)"),
         "random_ctr": num(ck.eq("obd_ctr_random_k", k(a2["random_ctr"], 2, False)), S + "random_ctr ×1000")}
    g = next(x for x in gp["cases"] if x["case"] == "Analysis 2 Random→V(BTS) P-hourly")
    d["ess_pct"] = num(f"{g['ess_frac']:.1%}", "eval/results/gate_obd_posthoc.json → cases['Analysis 2 Random→V(BTS) P-hourly'].ess_frac")
    d["z"] = num(sgn(g["z_mean_w"], 1), "eval/results/gate_obd_posthoc.json → cases['Analysis 2 Random→V(BTS) P-hourly'].z_mean_w")
    assert g["answer"]
    a1 = pre["a1"]
    d["a1_cells"] = num(ck.eq("a1_changed", f"{a1['cells_ratio_ge_1.5']}/20"), "eval/results/obd_slice.json → a1.cells_ratio_ge_1.5 (of the 20 busiest cells)")
    d["a1_med"] = num(ck.eq("a1_median_ratio", f"{a1['median_ratio']:.0f}"), "eval/results/obd_slice.json → a1.median_ratio")
    dm = bb["dm_refit"]
    d["dm_se"] = num(f"{1000 * dm['se_refit']:.3f}", "eval/results/obd_block_bootstrap.json → dm_refit.se_refit ×1000")
    d["dm_se_old"] = num(f"{1000 * dm['se_fixed_reported']:.4f}", "eval/results/obd_block_bootstrap.json → dm_refit.se_fixed_reported ×1000")
    rows = []
    for pol, plab in (("P-static", "static prior (standard OBD protocol)"), ("P-hourly", "hourly reconstruction")):
        for e in ("IPW", "SNIPW", "DM", "DR"):
            r = a2[pol][e]
            rows.append(dict(pol=pol, plab=plab, e=e, v=1000 * r["value"], lo=1000 * (r["value"] - Z * r["se"]), hi=1000 * (r["value"] + Z * r["se"]),
                             ok=r["consistent"], rel=r["rel_err"], src=f"{S}{pol}.{e}.value / se ×1000"))
    svg = forest(rows, 1000 * a2["truth"], 1000 * Z * a2["truth_se"], 1000 * dm["se_refit"])
    return d, svg


def forest(rows, t, thw, dm_se_refit):
    W, H, xl, xr, top, rh = 620, 46 * len(rows) + 70, 220, 600, 30, 46
    lo, hi = 4.35, 5.55
    x = lambda v: xl + (xr - xl) * (v - lo) / (hi - lo)
    out = [f'<svg class="forest" viewBox="0 0 {W} {H}" role="img" aria-label="Forest plot of eight estimates of the Thompson-sampling click rate against its A/B arm">',
           f'<rect x="{x(t - thw):.1f}" y="{top - 14}" width="{x(t + thw) - x(t - thw):.1f}" height="{rh * len(rows) + 10}" class="refband"/>',
           f'<line x1="{x(t):.1f}" x2="{x(t):.1f}" y1="{top - 14}" y2="{top + rh * len(rows) - 4}" class="refline"/>',
           f'<text x="{x(t):.1f}" y="{top - 18}" class="reflab" text-anchor="middle">A/B check {t:.3f}</text>']
    for v in (4.5, 5.0, 5.5):
        out.append(f'<text x="{x(v):.1f}" y="{top + rh * len(rows) + 18}" class="tick" text-anchor="middle">{v:.1f}</text>')
    for i, r in enumerate(rows):
        yy = top + i * rh + rh / 2 - 6
        if i == 4:
            out.append(f'<line x1="8" x2="{W - 8}" y1="{top + i * rh - 6}" y2="{top + i * rh - 6}" class="sep"/>')
        if i % 4 == 0:
            out.append(f'<text x="8" y="{yy - 12}" class="grp">{esc(r["plab"])}</text>')
        col = "var(--ink)" if r["ok"] else "var(--red)"
        out.append(f'<text x="22" y="{yy + 5}" class="rowlab">{r["e"]}</text>'
                   f'<text x="{xl - 12}" y="{yy + 5}" class="rowval" text-anchor="end">{r["v"]:.3f}</text>'
                   f'<line x1="{x(r["lo"]):.1f}" x2="{x(r["hi"]):.1f}" y1="{yy}" y2="{yy}" stroke="{col}" stroke-width="3"/>'
                   f'<circle cx="{x(r["v"]):.1f}" cy="{yy}" r="{6 if r["e"] == "DR" and r["pol"] == "P-hourly" else 4.5}" fill="{col}"><title>{esc(r["src"])}</title></circle>')
        if not r["ok"]:
            out.append(f'<ellipse cx="{x(r["v"]):.1f}" cy="{yy}" rx="15" ry="11" class="redcircle"/>')
            if r["pol"] == "P-static":
                a, b = r["v"] - Z * dm_se_refit, r["v"] + Z * dm_se_refit
                out.append(f'<line x1="{x(a):.1f}" x2="{x(b):.1f}" y1="{yy + 9}" y2="{yy + 9}" class="refit"/>')
    out.append("</svg>")
    return "".join(out)


def sim_waterfall():
    rows = [r for r in csv.DictReader(open(RES / "sim_bank_runs.csv")) if r["scenario"] == "S1_drift_masks_gain" and r["estimator"] == "DECOMP"]
    m = lambda key: math.fsum(float(r[key]) for r in rows) / len(rows)
    est = [("Policy", "OPE (DR)", 100 * m("delta"), 100 * float(rows[0]["truth"])),
           ("User mix", "shift", 100 * m("mix_hat"), 100 * float(rows[0]["mix_true"])),
           ("Season", "response drift", 100 * m("drift_hat"), 100 * float(rows[0]["drift_true"]))]
    naive = 100 * m("naive")
    W, H, x0, top, bot = 620, 330, 60, 30, 270
    lo, hi = -10.5, 10.5
    y = lambda v: top + (bot - top) * (hi - v) / (hi - lo)
    out = [f'<svg class="wf" viewBox="0 0 {W} {H + 26}" role="img" aria-label="Simulator waterfall: dashboard {naive:+.1f} points is policy {est[0][2]:+.1f} plus mix {est[1][2]:+.1f} plus season {est[2][2]:+.1f}">']
    for t in (-10, -5, 0, 5, 10):
        out.append(f'<line x1="{x0}" x2="{W - 8}" y1="{y(t):.1f}" y2="{y(t):.1f}" class="{"axis" if t == 0 else "gridln"}"/>'
                   f'<text x="{x0 - 8}" y="{y(t) + 5:.1f}" class="tick" text-anchor="end">{sgn(t, 0) if t else "0"}</text>')
    bw, gap, cum = 100, 38, 0.0
    for i, (lab, sub, v, tv) in enumerate(est):
        bx = x0 + 22 + i * (bw + gap)
        a, b = cum, cum + v
        out.append(f'<rect x="{bx}" y="{y(max(a, b)):.1f}" width="{bw}" height="{abs(y(a) - y(b)):.1f}" fill="{"var(--ok)" if v > 0 else "var(--red)"}" opacity="0.8"/>'
                   f'<line x1="{bx - 6}" x2="{bx + bw + 6}" y1="{y(cum + tv):.1f}" y2="{y(cum + tv):.1f}" class="truthln"/>'
                   f'<text x="{bx + bw / 2}" y="{(y(max(a, b)) - 8) if v > 0 else (y(min(a, b)) + 20):.1f}" class="barval" text-anchor="middle">{sgn(v, 1)}</text>'
                   f'<text x="{bx + bw / 2}" y="{bot + 26}" class="barlab" text-anchor="middle">{lab}</text>'
                   f'<text x="{bx + bw / 2}" y="{bot + 44}" class="barsub" text-anchor="middle">{sub}</text>')
        out.append(f'<line x1="{bx + bw}" x2="{bx + bw + gap}" y1="{y(b):.1f}" y2="{y(b):.1f}" class="connector"/>')
        cum = b
    bx = x0 + 22 + 3 * (bw + gap)
    out.append(f'<rect x="{bx}" y="{y(0):.1f}" width="{bw}" height="{y(naive) - y(0):.1f}" fill="var(--ink)" opacity="0.85"/>'
               f'<text x="{bx + bw / 2}" y="{y(naive) + 20:.1f}" class="barval" text-anchor="middle">{sgn(naive, 1)}</text>'
               f'<text x="{bx + bw / 2}" y="{bot + 26}" class="barlab" text-anchor="middle">Dashboard</text>'
               f'<text x="{bx + bw / 2}" y="{bot + 44}" class="barsub" text-anchor="middle">after − before</text>')
    out.append(f'<text x="{x0}" y="{H + 20}" class="barsub">Bars: our estimates (mean of {len(rows)} seeds) · dashed: simulator ground truth</text></svg>')
    return "".join(out), dict(policy=est[0][2], policy_true=est[0][3], mix=est[1][2], mix_true=est[1][3], season=est[2][2], season_true=est[2][3],
                              naive=naive, seeds=len(rows))


# ------------------------------------------------------------------------------------------------------------- knob data
def knob_data(kr):
    EST = ("IPW", "SNIPW")
    series = {}
    for key, s in kr["series"].items():
        rows = s["rows"]
        f = {"ess": [r6(r["ess_frac"]) for r in rows], "z": [round(r["z"], 3) for r in rows],
             "ref": [r6(1000 * r["ref"]) for r in rows], "sref": [r6(1000 * r["se_ref"]) for r in rows], "srefc": [r6(1000 * r["se_ref_cl"]) for r in rows],
             "why": ["; ".join(r["why"]) for r in rows]}
        bits = []
        for r in rows:
            b = int(r["answer"])
            for j, e in enumerate(EST):
                for i, ep in enumerate(("E1", "E1_cl", "E2", "E2_cl")):
                    b |= int(r[e][ep]) << (1 + 4 * j + i)
            bits.append(b)
        f["bits"] = bits
        for e in EST:
            f[e] = {"v": [r6(1000 * r[e]["v"]) for r in rows], "s": [r6(1000 * r[e]["se"]) for r in rows], "sc": [r6(1000 * r[e]["se_cl"]) for r in rows],
                    "m": [r6(1000 * r[e]["miss"]) for r in rows], "mc": [r6(1000 * r[e]["miss_cl"]) for r in rows]}
        series[key] = {"period": s["period"], "label": s["label"], "source": s["source"], "n": s["n_logging"], "n_other": s["n_other"],
                       "max_x": s["max_far_weight"], "hours": s["hours"], "f": f, "summary": s["summary"]}
    pred = {}
    for key, g in kr["predictions"].items():
        gate = g.get("gate", {})
        m = re.search(r"first abstain (\d\.\d\d)", gate.get("predicted", ""))
        pred[key] = {"items": g, "gate_alpha": float(m.group(1)) if m else None,
                     "gate_all": gate.get("predicted", "").startswith("abstain at every"), "gate_never": gate.get("predicted") == "never"}
    hits = sum(1 for g in kr["predictions"].values() for v in g.values() if isinstance(v, dict) and v.get("grade") == "hit")
    total = sum(1 for g in kr["predictions"].values() for v in g.values() if isinstance(v, dict) and "grade" in v)
    plab = {p_["id"]: p_["label"].split(" · ")[0] for p_ in kr["periods"]}
    iname = {"gate": "gate", "E1_IPW": "IPS interval holds the check", "E2_IPW": "IPS S1 test"}
    misses = []
    for key, g in kr["predictions"].items():
        for item, v in g.items():
            if isinstance(v, dict) and v.get("grade", "hit") not in ("hit", "n/a"):
                pid, src = key.split("·")
                note = v["grade"].split("(", 1)[1].rstrip(")") if "(" in v["grade"] else ""
                misses.append(f"{plab[pid]}, {'BTS' if src == 'SB' else 'Random'} logs, {iname.get(item, item)}: predicted {v['predicted']}; "
                              f"observed {v['result']}" + (f" ({note})" if note else ""))
    tot = {}
    for e in EST:
        for iv in ("row", "cluster"):
            for ep in ("E1", "E2"):
                tot[f"{e}_{iv}_{ep}"] = {c: sum(s["summary"][f"{e}_{iv}"][ep][c] for s in kr["series"].values())
                                         for c in ("answered_hold", "answered_miss", "unnecessary_abstention", "justified_abstention")}
    # where the IPW row-level answered misses are (computed, not typed)
    where = []
    for key, s in kr["series"].items():
        al = [r["a"] for r in s["rows"] if r["answer"] and not r["IPW"]["E1"]]
        if al:
            where.append({"key": key, "label": s["label"], "source": s["source"], "from": min(al), "to": max(al), "count": len(al),
                          "max_miss": 1000 * max(r["IPW"]["miss"] for r in s["rows"] if r["answer"] and not r["IPW"]["E1"])})
    return {"grid": kr["grid"], "periods": kr["periods"], "sources": kr["sources"], "series": series, "pred": pred,
            "hits": hits, "total": total, "misses": misses, "totals": tot, "where": where, "rule": kr["rule"], "prereg": kr["prereg"],
            "repro": [sum(c["ok"] for c in kr["reproduction"]), len(kr["reproduction"])],
            "xcheck": [sum(bool(v) for v in kr["crosscheck"].values()), len(kr["crosscheck"])],
            "p1p2": [sum(all(v2 for k2, v2 in v.items() if isinstance(v2, bool)) for v in kr["p1_p2"].values()), len(kr["p1_p2"])]}


def sweep_data(dec, ck):
    pts = []
    for key, v in dec.items():
        if key.startswith("drift"):
            pts.append({"drift": float(key[5:]), "truth": 100 * v["truth"]["effect_after"], "naive": 100 * v["naive_mean"], "dr": 100 * v["dr_mean"],
                        "naive_ok": v["naive_sign_ok"], "naive_rmse": 100 * v["naive_rmse"], "dr_rmse": 100 * v["dr_rmse"], "dr_cover": v["dr_cover"],
                        "seeds": v["seeds"], "src": f"eval/results/decomposer_review.json → [{key}] truth.effect_after, naive_mean, naive_sign_ok, naive_rmse, dr_mean, dr_rmse, dr_cover (×100)"})
    pts.sort(key=lambda p: p["drift"])
    ck.eq("sweep_points", str(len(pts)))
    ck.eq("sweep_dr_rmse_max_pp", f"{max(p['dr_rmse'] for p in pts):.1f}")
    ck.eq("sweep_naive_rmse_max_pp", f"{max(p['naive_rmse'] for p in pts):.1f}")
    return pts


# ------------------------------------------------------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(DEMO / "index.html"))
    args = ap.parse_args()
    pre, gp, bb, hl = jload("eval/results/obd_slice.json"), jload("eval/results/gate_obd_posthoc.json"), jload("eval/results/obd_block_bootstrap.json"), jload("eval/results/headline.json")
    dec, kr, man, rule = jload("eval/results/decomposer_review.json"), jload("demo/results/knob_results.json"), jload("demo/data/extract_manifest.json"), jload("eval/gate_rule.json")
    assert kr["rule"] == rule, "knob results were computed with a different gate rule"
    assert {k_: v["sha256"] for k_, v in man["files"].items()} == kr["extract"], "knob results do not match the vendored extract"
    ck = Checks(hl)
    s1, wf1 = sheet1(pre, gp, bb, ck)
    s2, fp2 = sheet2(pre, gp, bb, ck)
    wf4, s4w = sim_waterfall()
    ck.eq("s1_naive_pp", sgn(s4w["naive"], 1))
    ck.eq("s1_truth_pp", sgn(s4w["policy_true"], 1))
    ck.eq("bank_seeds", str(s4w["seeds"]))
    sweep = sweep_data(dec, ck)
    knob = knob_data(kr)
    digests = {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest()[:12] for p in INPUTS}
    data = {"knob": knob, "sweep": sweep, "s4": s4w, "digests": digests, "headline_checks": len(ck.done),
            "extract": {k_: v for k_, v in man["files"].items()}}
    tpl = (DEMO / "page.template.html").read_text()
    fill = {**{f"S1_{k_}": v for k_, v in s1.items()}, **{f"S2_{k_}": v for k_, v in s2.items()}}
    fill.update({"S1_WATERFALL": wf1, "S2_FOREST": fp2, "S4_WATERFALL": wf4,
             "S4_POLICY": num(sgn(s4w["policy"], 1), "eval/results/sim_bank_runs.csv → S1_drift_masks_gain, DECOMP rows, mean(delta) ×100"),
             "S4_POLICY_TRUE": num(sgn(s4w["policy_true"], 1), "eval/results/sim_bank_runs.csv → S1_drift_masks_gain truth ×100"),
             "S4_NAIVE": num(sgn(s4w["naive"], 1), "eval/results/sim_bank_runs.csv → S1_drift_masks_gain, DECOMP rows, mean(naive) ×100"),
             "S4_SEEDS": num(str(s4w["seeds"]), "eval/results/sim_bank_runs.csv → S1_drift_masks_gain seeds"),
             "S4_WRONG": num(ck.eq("s1_naive_wrong", "30/30"), "eval/results/headline.json → display.s1_naive_wrong (sim_bank_runs.csv S1 naive wrong-sign seeds)"),
             "STAMP_REAL": stamp("real", "Real data"), "STAMP_POST": stamp("post", "Post hoc"),
             "RULE_ESS": num(f"{rule['tau_ess']:.0%}", "eval/gate_rule.json → tau_ess (frozen, b4e95ae)"),
             "RULE_Z": num(f"{rule['tau_z']:g}", "eval/gate_rule.json → tau_z (frozen, b4e95ae)"),
             "K_PERIODS": num(str(len(kr["periods"])), "demo/results/knob_results.json → periods"),
             "K_GRID": num(str(len(kr["grid"])), "demo/results/knob_results.json → grid"),
             "PREREG_TIME": esc(kr["prereg"]["registered_at"]), "PREREG_COMMIT": esc(kr["prereg"]["commit"][:7]),
             "EXTRACT_MB": f"{sum(v['bytes'] for v in man['files'].values()) / 1e6:.2f}",
             "DIGESTS": " · ".join(f"{esc(p.split('/')[-1])} {d}" for p, d in digests.items()),
             "DATA_JSON": json.dumps(data, separators=(",", ":"), ensure_ascii=False, allow_nan=False).replace("</", "<\\/")})
    def sub(m):
        key = m.group(1)
        if key not in fill:
            raise KeyError(f"template placeholder {{{{{key}}}}} has no value")
        return fill[key]
    out = re.sub(r"\{\{([A-Za-z0-9_]+)\}\}", sub, tpl)
    assert "{{" not in out
    assert not re.search(r"""(src|href)\s*=\s*["']https?://""", out), "no external resources allowed"
    Path(args.out).write_text(out)
    print(f"wrote {args.out} ({len(out.encode()) / 1e3:.0f} kB); {len(ck.done)} numbers asserted equal to eval/results/headline.json")


if __name__ == "__main__":
    main()
