"""Summarise eval/results/<tag>_*.jsonl into eval/results/<tag>_summary.md and <tag>_canonical.json.

Usage: python -m eval.summarize --tag v2

Statistics: every comparison between strategies is *paired by seed* (same seed ⇒ identical device availability
schedule and identical initial anchor), with a two-sided 95 % t-interval over seeds. Per-domain gains are
untuned-model loss minus final loss (the untuned loss is seed-independent because B starts at 0).
The canonical JSON holds every number the deliverables may quote (checked by scripts/check_numbers.py).
"""
from __future__ import annotations

import argparse
import json
import statistics
from collections import defaultdict
from pathlib import Path

from components.device_simulator import DEFAULT_PROFILES

OUT = Path(__file__).resolve().parent / "results"
STARTER = "fedavg_ab_homo"
SPIKE = "anchor_full"
PUBLISHED = ["ffa_lora", "flexlora", "fedavg_ab_het"]
ORDER = ["fedavg_ab_homo", "ffa_lora", "flexlora", "fedavg_ab_het", "anchor_naive", "anchor_full",
         "anchor_full_nonorm", "anchor_full_tauact", "anchor_full_seg", "anchor_full_sqrtn", "anchor_full_decay"]
LABEL = {
    "fedavg_ab_homo": "Starter: FedAvg on A,B, rank 8 everywhere",
    "ffa_lora": "FFA-LoRA (ICLR 2024): frozen A, FedAvg on B, rank 8",
    "flexlora": "FlexLoRA (arXiv 2402.11505): product average + SVD, device ranks",
    "fedavg_ab_het": "HetLoRA-style: FedAvg on A,B, zero-padded device ranks",
    "anchor_naive": "Ablation: frozen shared A + device ranks, n_k weights only",
    "anchor_full": "**AnchorLoRA (ours)**",
    "anchor_full_nonorm": "AnchorLoRA without step normalisation",
    "anchor_full_tauact": "AnchorLoRA, τ_eff from actual steps",
    "anchor_full_seg": "AnchorLoRA + PreLort-style per-column averaging",
    "anchor_full_sqrtn": "AnchorLoRA, √n weights",
    "anchor_full_decay": "AnchorLoRA, memory decayed 0.5^age",
}
DATA = {p.domain: p.n_train_blocks for p in DEFAULT_PROFILES}


def tcrit(n: int, k: int = 1) -> float:
    """Two-sided 95 % t critical value; k > 1 applies a Bonferroni correction for k simultaneous intervals."""
    from scipy import stats

    return float(stats.t.ppf(1 - 0.05 / (2 * k), n - 1))


def ci(vals: list[float], k: int = 1) -> tuple[float, float | None, float | None]:
    m = statistics.mean(vals)
    if len(vals) < 2:
        return m, None, None
    h = tcrit(len(vals), k) * statistics.stdev(vals) / len(vals) ** 0.5
    return m, m - h, m + h


def validate(runs: list[dict], path: Path) -> dict:
    """Refuse to pool duplicate (strategy, seed) rows or dirty-tree runs; return the provenance table."""
    seen, prov = set(), defaultdict(set)
    for r in runs:
        key = (r["strategy"], r["seed"])
        if key in seen:
            raise SystemExit(f"{path.name}: duplicate run {key} — refusing to pool")
        seen.add(key)
        env = r.get("env", {})
        if env.get("dirty"):
            raise SystemExit(f"{path.name}: run {key} was produced from a dirty tree — refusing to pool")
        prov[r["strategy"]].add((env.get("commit", "n/a"), env.get("code_sha", "n/a"), env.get("data_digest", "n/a"),
                                 env.get("model_revision", "n/a")))
    return prov


def micro(per_domain: dict[str, float]) -> float:
    tot = sum(DATA[d] for d in per_domain)
    return sum(DATA[d] * v for d, v in per_domain.items()) / tot


def fmt_ci(m, lo, hi, nd=4, signed=True) -> str:
    f = f"{{:{'+' if signed else ''}.{nd}f}}"
    return f.format(m) + ("" if lo is None else f" [{f.format(lo)}, {f.format(hi)}]")


def paired(by: dict, a: str, b: str, key) -> list[tuple[int, float]]:
    bmap = {r["seed"]: key(r) for r in by.get(b, [])}
    return sorted((r["seed"], key(r) - bmap[r["seed"]]) for r in by.get(a, []) if r["seed"] in bmap)


def scenario_section(tag: str, scen: str, runs: list[dict], canon: dict) -> list[str]:
    by = defaultdict(list)
    for r in runs:
        by[r["strategy"]].append(r)
    base = runs[0]["base_macro_loss"]
    base_dom = json.loads((OUT / "base_per_domain_smollm2-135m.json").read_text())
    canon["base.macro"] = base
    canon["base.micro"] = micro(base_dom)
    for d, v in base_dom.items():
        canon[f"base.{d}"] = v
    cfg = runs[0]["config"]
    prov = validate(runs, OUT / f"{tag}_{scen}.jsonl")
    shas = sorted({r.get("env", {}).get("code_sha", "n/a") for r in runs})
    dirty = False
    strats = [s for s in ORDER if s in by] + [s for s in by if s not in ORDER]
    L = [f"## Scenario `{scen}` (`{tag}_{scen}.jsonl`)", "",
         f"{cfg['model_id']}, LoRA on {', '.join(cfg['targets'])}, r_max {cfg['r_max']}, α {cfg['alpha']}, "
         f"{cfg['rounds']} rounds, batch {cfg['batch_size']}×{cfg['seq_len']}, lr {cfg['lr']}. "
         f"Untuned model: macro **{base:.4f}**, micro {micro(base_dom):.4f}. Code: `{', '.join(shas)}`"
         f". Loss = next-token cross-entropy (nats/token) on held-out blocks.", "",
         "Provenance (commit · code_sha · data_digest · model_revision) per strategy: "
         + "; ".join(f"{s}: " + ", ".join("·".join(x) for x in sorted(v)) for s, v in sorted(prov.items())) + ". "
         "Different code hashes are accepted only because `git diff` between them touches analysis scripts and new "
         "strategy registrations, and reruns across revisions are bit-identical (thought node 11:45).", "",
         "Columns: macro = mean domain loss; micro = data-volume-weighted loss (the objective n_k-weighted FedAvg "
         "optimises); c0 share (proj.) = <c_0,P>/‖P‖² (unbounded); c0 share (norm) = ‖c_0‖/Σ‖c_j‖ (bounded, fair share "
         "0.2); agg. error = ‖P−Σc_k‖/‖Σc_k‖ of the full update; max spike = largest rise between evaluations every 3 "
         "rounds; upload = logical fp32 uplink only.", "",
         "| Strategy | n | macro ↓ (mean ± sd) | Δ macro vs starter, 95 % CI | worst domain ↓ | micro ↓ | c0 share (proj.) | "
         "c0 share (norm) | agg. error | max spike | upload MB / device |",
         "|---|---|---|---|---|---|---|---|---|---|---|"]
    for s in strats:
        rs = by[s]
        mac = [r["final_macro_loss"] for r in rs]
        p = paired(by, s, STARTER, lambda r: r["final_macro_loss"]) if s != STARTER else []
        dm, dlo, dhi = ci([v for _, v in p]) if p else (None, None, None)
        mic = [micro(r["final_per_domain_loss"]) for r in rs]
        up = statistics.mean(statistics.mean(r["upload_mb"].values()) for r in rs)
        k = f"{scen}.{s}"
        canon.update({f"{k}.n": len(rs), f"{k}.macro_mean": statistics.mean(mac),
                      f"{k}.macro_sd": statistics.stdev(mac) if len(mac) > 1 else 0.0,
                      f"{k}.worst_mean": statistics.mean(r["final_worst_loss"] for r in rs),
                      f"{k}.micro_mean": statistics.mean(mic),
                      f"{k}.c0_share_mean": statistics.mean(r["dominance_c0"] for r in rs),

                      f"{k}.agg_err_mean": statistics.mean(r["aggregation_error"] for r in rs),
                      f"{k}.max_spike_max": max(r["max_spike"] for r in rs),
                      f"{k}.upload_mb_mean": up,
                      f"{k}.weak_gain_mean": statistics.mean(r["weak_gain"] for r in rs)})
        if dm is not None:
            canon.update({f"{k}.d_vs_starter_mean": dm})
            if dlo is not None:
                canon.update({f"{k}.d_vs_starter_lo": dlo, f"{k}.d_vs_starter_hi": dhi})
        nsh = [r["dominance_c0_norm"] for r in rs if "dominance_c0_norm" in r]
        if len(nsh) == len(rs):
            canon[f"{k}.c0_norm_mean"] = statistics.mean(nsh)
        tr = [r["truncation_error"] for r in rs if r.get("truncation_error") is not None]
        if tr:
            canon[f"{k}.trunc_err_mean"] = statistics.mean(tr)
        L.append(f"| {LABEL.get(s, s)} | {len(rs)} | {statistics.mean(mac):.4f} ± "
                 f"{(statistics.stdev(mac) if len(mac) > 1 else 0):.4f} | "
                 f"{fmt_ci(dm, dlo, dhi) if dm is not None else '—'} | {canon[f'{k}.worst_mean']:.4f} | "
                 f"{canon[f'{k}.micro_mean']:.4f} | {canon[f'{k}.c0_share_mean']:.3f} | "
                 f"{format(canon[f'{k}.c0_norm_mean'], '.3f') if f'{k}.c0_norm_mean' in canon else 'n/a'} | "
                 f"{100 * canon[f'{k}.agg_err_mean']:.1f} %"
                 f"{(' (served trunc. ' + format(100 * canon[f'{k}.trunc_err_mean'], '.1f') + ' %)') if f'{k}.trunc_err_mean' in canon else ''} | "
                 f"{canon[f'{k}.max_spike_max']:.4f} | {up:.2f} |")
    # spike vs every published baseline, paired
    L += ["", f"**AnchorLoRA vs each baseline** (paired by seed; Δ = AnchorLoRA − baseline; negative = AnchorLoRA better):", "",
          "| Baseline | shared seeds | Δ macro, 95 % CI | Δ worst domain, 95 % CI | Δ micro, 95 % CI | Δ per seed (macro) |",
          "|---|---|---|---|---|---|"]
    for b in [STARTER] + PUBLISHED + ["anchor_naive"]:
        if b not in by or SPIKE not in by:
            continue
        pm = paired(by, SPIKE, b, lambda r: r["final_macro_loss"])
        if not pm:
            continue
        pw = paired(by, SPIKE, b, lambda r: r["final_worst_loss"])
        pu = paired(by, SPIKE, b, lambda r: micro(r["final_per_domain_loss"]))
        cm, cw, cu = ci([v for _, v in pm]), ci([v for _, v in pw]), ci([v for _, v in pu])
        canon[f"{scen}.spike_vs_{b}.n"] = len(pm)
        for nm, c in (("macro", cm), ("worst", cw), ("micro", cu)):
            canon[f"{scen}.spike_vs_{b}.{nm}_mean"] = c[0]
            if c[1] is not None:
                canon[f"{scen}.spike_vs_{b}.{nm}_lo"], canon[f"{scen}.spike_vs_{b}.{nm}_hi"] = c[1], c[2]
        L.append(f"| {LABEL.get(b, b)} | {','.join(str(s) for s, _ in pm)} | {fmt_ci(*cm)} | {fmt_ci(*cw)} | "
                 f"{fmt_ci(*cu)} | " + ", ".join(f"s{s}: {v:+.4f}" for s, v in pm) + " |")
    # per-domain gains vs the untuned model
    doms = list(base_dom)
    L += ["", "**Per-domain gain vs the untuned model** (untuned − final, nats/token; mean [marginal 95 % CI] over seeds; "
              f"device data volume: {', '.join(f'{d} {DATA[d]}' for d in doms)} blocks). Last column: domains whose "
              "lower bound is > 0, marginal / Bonferroni-simultaneous over the 5 domains (exploratory; the pre-specified "
              "primary comparison is the paired macro Δ vs the starter):", "",
          "| Strategy | " + " | ".join(doms) + " | domains > 0 (marg. / Bonf.) |", "|---" * (len(doms) + 2) + "|"]
    for s in strats:
        cells, pos, posb = [], 0, 0
        for d in doms:
            g = [base_dom[d] - r["final_per_domain_loss"][d] for r in by[s]]
            m, lo, hi = ci(g)
            _, blo, bhi = ci(g, k=len(doms))
            if blo is not None:
                canon[f"{scen}.{s}.{d}.gain_lo_bonf"], canon[f"{scen}.{s}.{d}.gain_hi_bonf"] = blo, bhi
                posb += blo > 0
            canon[f"{scen}.{s}.{d}.gain_mean"] = m
            canon[f"{scen}.{s}.{d}.final_mean"] = statistics.mean(r["final_per_domain_loss"][d] for r in by[s])
            if lo is not None:
                canon[f"{scen}.{s}.{d}.gain_lo"], canon[f"{scen}.{s}.{d}.gain_hi"] = lo, hi
                pos += lo > 0
            cells.append(fmt_ci(m, lo, hi, nd=3))
        canon[f"{scen}.{s}.domains_ci_pos"] = pos
        canon[f"{scen}.{s}.domains_ci_pos_bonf"] = posb
        L.append(f"| {s} | " + " | ".join(cells)
                 + (f" | {pos} / {posb} of {len(doms)} |" if len(by[s]) > 1 else " | — |"))
    # per-domain paired difference spike vs starter
    if SPIKE in by and STARTER in by:
        L += ["", "**Per-domain paired Δ, AnchorLoRA − starter** (negative = AnchorLoRA better):", "",
              "| " + " | ".join(doms) + " |", "|---" * len(doms) + "|"]
        cells = []
        for d in doms:
            pd = paired(by, SPIKE, STARTER, lambda r, d=d: r["final_per_domain_loss"][d])
            c = ci([v for _, v in pd])
            canon[f"{scen}.spike_vs_starter.{d}_mean"] = c[0]
            if c[1] is not None:
                canon[f"{scen}.spike_vs_starter.{d}_lo"], canon[f"{scen}.spike_vs_starter.{d}_hi"] = c[1], c[2]
            cells.append(fmt_ci(*c, nd=3))
        L.append("| " + " | ".join(cells) + " |")
    return L + [""]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", default="v2")
    args = ap.parse_args()
    canon: dict = {}
    lines = [f"# Results `{args.tag}` (auto-generated: `python -m eval.summarize --tag {args.tag}`)", ""]
    for path in sorted(OUT.glob(f"{args.tag}_*.jsonl")):
        runs = [json.loads(l) for l in path.read_text().splitlines() if l.strip()]
        if runs:
            lines += scenario_section(args.tag, runs[0]["scenario"], runs, canon)
    (OUT / f"{args.tag}_summary.md").write_text("\n".join(lines) + "\n")
    (OUT / f"{args.tag}_canonical.json").write_text(json.dumps(canon, indent=1, sort_keys=True) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
