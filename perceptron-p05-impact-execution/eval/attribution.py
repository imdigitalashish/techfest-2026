"""Pre-registered E8 analysis: attribute the IA_sched_only gain to the QP schedule vs front-loading.

Contrasts (paired by seed; bootstrap 95% CI, 10k resamples, RandomState(0), seeds sorted):
  A  QP main effect           = 1/2[(QP_only - TWAP) + (IA_sched_only - TWAP_legacy_fb)]
  B  front-loading main effect = 1/2[(TWAP_legacy_fb - TWAP) + (IA_sched_only - QP_only)]
  C  interaction               = (IA_sched_only - TWAP_legacy_fb) - (QP_only - TWAP)
  D  corrected feedback        = IA_sched_fixed - QP_only
Usage: .venv/bin/python eval/attribution.py [--exp E8_ablation_val]
Writes eval/results/<exp>_attribution.md and .json.
"""
import argparse, json, os
import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
METRICS = ["is_bps", "own_impact_bps", "instant_bps", "drift_bps"]


def ci(d, n=10000):
    bm = np.random.RandomState(0).choice(d, size=(n, len(d))).mean(1)
    return float(np.percentile(bm, 2.5)), float(np.percentile(bm, 97.5))


def verdict(a, b):
    ea = a[1] > 0 or a[2] < 0
    eb = b[1] > 0 or b[2] < 0
    return {(True, False): "QP schedule", (False, True): "front-loading", (True, True): "both",
            (False, False): "unattributed at this n"}[(ea, eb)]


LABELS = ["TWAP", "QP_only", "TWAP_legacy_fb", "IA_sched_only", "IA_sched_fixed"]


def analyze(df, exp=""):
    """Pure function of the experiment CSV (used by eval/claims.py; review sol #3)."""
    labels = LABELS
    seeds = sorted(set.intersection(*[set(df[df.label == l].seed) for l in labels]))
    out = dict(exp=exp, n_seeds=len(seeds), seeds=[seeds[0], seeds[-1]],
               integrity=dict(pre_window_identical=bool(df.pre_window_identical.all()),
                              all_filled=bool((df.filled == df.qty).all())), arms={}, contrasts={})
    for m in METRICS:
        P = df[df.seed.isin(seeds)].pivot(index="seed", columns="label", values=m).loc[seeds]
        for l in labels:
            out["arms"].setdefault(l, {})[m] = float(P[l].mean())
            if l != "TWAP":
                d = (P[l] - P["TWAP"]).values
                out["arms"][l][f"d_{m}_vs_TWAP"] = [float(d.mean()), *ci(d)]
        con = {"A_qp_main": 0.5 * ((P.QP_only - P.TWAP) + (P.IA_sched_only - P.TWAP_legacy_fb)),
               "B_frontload_main": 0.5 * ((P.TWAP_legacy_fb - P.TWAP) + (P.IA_sched_only - P.QP_only)),
               "C_interaction": (P.IA_sched_only - P.TWAP_legacy_fb) - (P.QP_only - P.TWAP),
               "D_fixed_feedback": P.IA_sched_fixed - P.QP_only}
        for k, v in con.items():
            out["contrasts"].setdefault(k, {})[m] = [float(v.values.mean()), *ci(v.values)]
    c = out["contrasts"]
    # Amendment A1 (eval/preregistration.md): signed labels with a +/-0.02 bps equivalence margin
    MARGIN = 0.02
    lab = lambda t: ("detected (" + ("−" if t[0] < 0 else "+") + ")") if (t[1] > 0 or t[2] < 0) else (
        "negligible" if (t[1] >= -MARGIN and t[2] <= MARGIN) else "unresolved")
    out["a1_margin_bps"] = MARGIN
    out["a1_labels"] = {k: {m: lab(c[k][m]) for m in ("is_bps", "own_impact_bps")} for k in c}
    out["a1_interaction_detected"] = {m: lab(c["C_interaction"][m]).startswith("detected") for m in ("is_bps", "own_impact_bps")}
    out["attribution_is"] = verdict(c["A_qp_main"]["is_bps"], c["B_frontload_main"]["is_bps"])
    out["attribution_own"] = verdict(c["A_qp_main"]["own_impact_bps"], c["B_frontload_main"]["own_impact_bps"])
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--exp", default="E8_ablation_val"); a = ap.parse_args()
    df = pd.read_csv(os.path.join(ROOT, "eval", "results", f"{a.exp}.csv"))
    out = analyze(df, a.exp)
    labels, seeds, c = LABELS, list(range(out["seeds"][0], out["seeds"][1] + 1)), out["contrasts"]
    json.dump(out, open(os.path.join(ROOT, "eval", "results", f"{a.exp}_attribution.json"), "w"), indent=1)
    f = lambda t: f"{t[0]:+.4f} [{t[1]:+.4f}, {t[2]:+.4f}]"
    L = [f"# {a.exp}: pre-registered attribution (eval/preregistration.md, E8)", "",
         f"n = {len(seeds)} validation seeds ({seeds[0]}–{seeds[-1]}), synced twins. Integrity: pre-window identical "
         f"{out['integrity']['pre_window_identical']}, all filled {out['integrity']['all_filled']}. Values: mean in bps "
         "with 95% paired-bootstrap CI.", "",
         "| arm | ΔIS vs TWAP | Δown impact | Δinstant | Δdrift |", "|---|---|---|---|---|"]
    for l in labels[1:]:
        L.append(f"| {l} | " + " | ".join(f(out['arms'][l][f'd_{m}_vs_TWAP']) for m in METRICS) + " |")
    L += ["", "| contrast | IS | own impact | instant | drift |", "|---|---|---|---|---|"]
    for k in c:
        L.append(f"| {k} | " + " | ".join(f(c[k][m]) for m in METRICS) + " |")
    L += ["", "**Amendment A1 labels** (signed; 'negligible' = CI within ±0.02 bps):", "",
          "| contrast | IS | own impact |", "|---|---|---|"]
    for k in c:
        L.append(f"| {k} | {out['a1_labels'][k]['is_bps']} | {out['a1_labels'][k]['own_impact_bps']} |")
    if any(out["a1_interaction_detected"].values()):
        L += ["", "Interaction detected: main effects are not interpreted alone (A1 rule 3)."]
    L += ["", f"Legacy classifier (pre-A1; not used in deliverables): IS → {out['attribution_is']}; own impact → {out['attribution_own']}."]
    open(os.path.join(ROOT, "eval", "results", f"{a.exp}_attribution.md"), "w").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
