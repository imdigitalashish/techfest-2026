"""Render the recorded fallback of the P1 demo into demo/fallback/ (matplotlib, from the same data as the page).

  .venv/bin/python demo/render_fallback.py

Every value comes from demo/web/data.js (built by demo/export_replay.py from the committed results, the validation
runs and the RECORDED live run), so the frames show exactly what the page shows.
"""
from __future__ import annotations

import json
import textwrap
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "demo" / "fallback"
TXT = (ROOT / "demo" / "web" / "data.js").read_text()
P = json.loads(TXT[len("window.P1 = "):].rstrip().rstrip(";"))
C = {**P["canonical"], **P["dropout_canonical"]}
STRATS, DOMS = P["strategies"], P["domains"]
COL = {"fedavg_ab_homo": ("#b34f00", "#e0812f"), "ffa_lora": ("#5f53a0", "#8a80c4"),
       "flexlora": ("#7a6a4b", "#ab9b7a"), "anchor_full": ("#006d75", "#178d95")}
DN = {"wiki": "Wikipedia\nworkstation · 8× data", "pycode": "Python code\nlaptop", "cheaders": "C/C++ headers\nphone",
      "readmes": "READMEs\nraspberry-pi", "manpages": "man pages\ntablet"}
M = "\u2212"
plt.rcParams.update({"font.size": 12, "axes.spines.top": False, "axes.spines.right": False, "figure.dpi": 100,
                     "axes.titleweight": "bold", "axes.titlesize": 14})


def fmt(v: float, nd: int = 3, signed: bool = True) -> str:
    s = f"{abs(v):.{nd}f}"
    if float(s) == 0:
        return s
    return (M if v < 0 else "+" if signed else "") + s


def validation_sentence() -> str:
    """The reviewers' wording, with the ranges read from demo/validation/results.json (as on the live page)."""
    rows = P["validation"]["results"]["rows"]
    s = [r["effect_starter"] for r in rows]
    a = [r["effect_anchor"] for r in rows]
    words = {5: "five"}
    return (f"Most of this gap exists even with nobody unplugged. In the {words.get(len(rows), len(rows))} validation "
            f"seeds, removing the tablet changed the starter's final man-pages loss by {fmt(min(s))} to {fmt(max(s))} "
            f"and AnchorLoRA's by {fmt(min(a))} to {fmt(max(a))}. The full system was less sensitive; this comparison "
            "does not isolate memory's contribution.")


def stamp(fig, text: str) -> None:
    fig.text(0.01, 0.01, text, fontsize=9, color="#56605a", family="monospace")


def frame_gains() -> None:
    fig = plt.figure(figsize=(14, 7.2))
    ax = fig.add_axes([0.06, 0.2, 0.55, 0.66])
    w = 0.19
    for i, s in enumerate(STRATS):
        for j, d in enumerate(DOMS):
            v, lo, hi = (C[f"dropout.{s}.{d}.{k}"] for k in ("gain_mean", "gain_lo_bonf", "gain_hi_bonf"))
            x = j + (i - 1.5) * w
            ax.bar(x, v, w * 0.9, color=COL[s][1], label=P["labels"][s] if j == 0 else None)
            ax.errorbar(x, v, yerr=[[v - lo], [hi - v]], color=COL[s][0], capsize=3, lw=1.4)
            if s in ("anchor_full", "fedavg_ab_homo"):
                ax.text(x, hi + 0.012 if v >= 0 else lo - 0.012, fmt(v), ha="center", va="bottom" if v >= 0 else "top",
                        fontsize=10, color=COL[s][0], weight="bold")
    ax.axhline(0, color="#18201c", lw=1.4)
    ax.set_xlim(-0.5, 5.05)
    ax.text(4.5, 0.012, "untuned", va="bottom", weight="bold")
    ax.set_xticks(range(5), [DN[d] for d in DOMS])
    ax.set_ylabel("improvement over the untuned model (nats/token)")
    ax.set_title("Who gains? Per-domain improvement after round 12 (5 paired seeds, dropout scenario)", loc="left")
    ax.legend(loc="upper right", fontsize=10, frameon=False)
    lines = ["AnchorLoRA minus each baseline,", "mean loss over 5 domains", "(paired by seed, 95% CI;", " negative = AnchorLoRA lower):"]
    for s, k in (("Starter", "spike_vs_fedavg_ab_homo"), ("FFA-LoRA", "spike_vs_ffa_lora"), ("FlexLoRA", "spike_vs_flexlora")):
        lines.append(f"  vs {s:9s} {fmt(C[f'dropout.{k}.macro_mean'])} [{fmt(C[f'dropout.{k}.macro_lo'])}, {fmt(C[f'dropout.{k}.macro_hi'])}]")
    lines += ["", "Domains above untuned (Bonferroni 95%):"]
    for s in ("anchor_full", "fedavg_ab_homo", "ffa_lora", "flexlora"):
        lines.append(f"  {P['short'][s]:10s} {C[f'dropout.{s}.domains_ci_pos_bonf']}/5")
    lines += ["", "Workstation's norm share of the update", "(magnitude diagnostic; equal share 0.20):"]
    for s in ("fedavg_ab_homo", "ffa_lora", "flexlora", "anchor_full"):
        lines.append(f"  {P['short'][s]:10s} {C[f'dropout.{s}.c0_norm_mean']:.2f}")
    fig.text(0.675, 0.86, "\n".join(lines), va="top", family="monospace", fontsize=10.5)
    fig.text(0.06, 0.95, "COMMITTED RUNS · real SmolLM2-135M · real text · SIMULATED device budgets", weight="bold", color="#5a3f94")
    stamp(fig, "source: eval/results/v2_canonical.json (dropout.<strategy>.<domain>.gain_mean/gain_lo_bonf/gain_hi_bonf,\n"
               "dropout.spike_vs_*.macro_*, *.domains_ci_pos_bonf, *.c0_norm_mean); bars: mean of 5 seeds, whiskers Bonferroni 95%")
    fig.savefig(OUT / "frame1_committed_gains.png")
    plt.close(fig)


def frame_outage() -> None:
    fig = plt.figure(figsize=(14, 6.6))
    ax = fig.add_axes([0.06, 0.15, 0.56, 0.7])
    base = P["untuned"]["manpages"]
    ax.axvspan(4.5, 9.5, color="#ece6f6")

    for s in STRATS:
        seeds = P["replay"]["runs"][s]
        pts = None
        for seed in seeds.values():
            xs = [0] + [r["round"] for r in seed["rounds"] if r["eval"]]
            ys = [0] + [base - r["eval"]["manpages"] for r in seed["rounds"] if r["eval"]]
            ax.scatter(xs[1:], ys[1:], s=14, color=COL[s][1], alpha=0.6)
            pts = [ys] if pts is None else pts + [ys]
        mean = [sum(c) / len(c) for c in zip(*pts)]
        ax.plot(xs, mean, color=COL[s][0], lw=3, label=P["labels"][s])
        ax.text(12.2, mean[-1], f"{P['short'][s]} {fmt(mean[-1])}", color=COL[s][0], va="center", weight="bold")
    ax.axhline(0, color="#18201c", lw=1.3)
    ax.set_xlim(-0.3, 14.6)
    lo = ax.get_ylim()[0]
    ax.text(7, lo + 0.008, "tablet offline, rounds 5–9 (forced outage)", ha="center", color="#5a3f94", weight="bold")
    ax.set_xticks(range(13))
    ax.set_xlabel("round (evaluated at 3, 6, 9, 12; nothing claimed between checkpoints)")
    ax.set_ylabel("man-page improvement over untuned (nats/token)")
    ax.set_title("The tablet goes offline for rounds 5–9: what happens to its domain?", loc="left")
    lines = ["Worst point above the untuned model", "(mean of 5 seeds; positive = worse):"]
    for s in ("fedavg_ab_homo", "flexlora", "ffa_lora", "anchor_full"):
        lines.append(f"  {P['short'][s]:10s} {fmt(C[f'dropout.{s}.outage_peak_rise_mean'])}"
                     f"  (worst seed {fmt(C[f'dropout.{s}.outage_peak_rise_max'])})")
    lines += ["", "AnchorLoRA: below untuned at every", "evaluated round in every seed."]
    fig.text(0.65, 0.8, "\n".join(lines), va="top", family="monospace", fontsize=10.5)
    fig.text(0.06, 0.94, "COMMITTED RUNS · real SmolLM2-135M · real text · SIMULATED device budgets", weight="bold", color="#5a3f94")
    stamp(fig, "plotted: base_per_domain_smollm2-135m.json manpages − eval/results/logs/v2_dropout_<strategy>_s<seed>.json "
               "eval.per_domain_loss.manpages (positive = better);\npeaks: v2_dropout_canonical.json "
               "*.outage_peak_rise_mean/max (trained − untuned: positive = worse)")
    fig.savefig(OUT / "frame2_committed_outage.png")
    plt.close(fig)


def live_frames() -> list:
    rec = P["recorded"]["events"]
    gh = P["validation"]["ghosts"]["0"]
    band = P["validation"]["results"]["band"]
    rounds = {}
    for e in rec:
        if e["ev"] == "round":
            rounds.setdefault(e["round"], {})[e["fed"]] = e
    figs = []
    rng = max(abs(v) for r in rounds.values() for e in r.values() for v in e["delta"].values()) * 1.15
    for t in sorted(rounds):
        fig = plt.figure(figsize=(14, 7.4))
        for i, f in enumerate(("fedavg_ab_homo", "anchor_full")):
            ax = fig.add_axes([0.05 + i * 0.48, 0.47, 0.42, 0.34])
            e = rounds[t][f]
            vals = [-e["delta"][d] for d in DOMS]
            ax.bar(range(5), vals, 0.56, color=COL[f][1])
            for j, v in enumerate(vals):
                ax.text(j, v + (0.01 if v >= 0 else -0.01), fmt(v), ha="center", va="bottom" if v >= 0 else "top",
                        color=COL[f][0], fontsize=10, weight="bold")
                g = gh[f][str(t)][DOMS[j]]
                ax.hlines(-g, j - 0.36, j + 0.36, colors="#18201c", linestyles="dashed", lw=1.5)
            ax.axhline(0, color="#18201c", lw=1.2)
            ax.set_ylim(-rng, rng)
            ax.set_xticks(range(5), ["Wikipedia", "Python", "C headers", "READMEs", "man pages"], fontsize=10)
            name = "Starter (FedAvg on A,B · r8 · data-weighted)" if f == "fedavg_ab_homo" else "AnchorLoRA"
            ax.set_title(f"{name}: after round {t}", loc="left", color=COL[f][0], fontsize=13)
            dev = e["devices"]["c4"]
            note = f"fresh updates {e['fresh']}/5 · tablet: {dev['state']}"
            if dev.get("memory") == "reused":
                note += f", reusing its last update (age {dev['memory_age']}/4)"
            elif dev.get("memory") == "expired":
                note += f", memory expired (age {dev['memory_age']} > 4)"
            ax.text(0, -rng * 0.97, note, fontsize=10, color="#3f4944")
        ax = fig.add_axes([0.05, 0.08, 0.69, 0.28])
        out = [r for r in sorted(rounds) if rounds[r]["anchor_full"]["devices"]["c4"]["state"] == "unplugged" and r <= t]
        for r in out:
            ax.axvspan(r - 0.5, min(r + 0.5, 6), color="#ece6f6")
        for f in ("fedavg_ab_homo", "anchor_full"):
            b = band[f"unplug.{f}"]
            rs = sorted(int(k) for k in b)
            ax.fill_between(rs, [-b[str(r)][0] for r in rs], [-b[str(r)][1] for r in rs], color=COL[f][1], alpha=0.16, lw=0)
            gx = [0] + sorted(int(k) for k in gh[f])
            ax.plot(gx, [0] + [-gh[f][str(r)]["manpages"] for r in gx[1:]], color=COL[f][0], ls="--", lw=1.6, alpha=0.75)
            xs = [0] + [r for r in sorted(rounds) if r <= t]
            ys = [0] + [-rounds[r][f]["delta"]["manpages"] for r in xs[1:]]
            ax.plot(xs, ys, color=COL[f][0], lw=3, marker="o", label="Starter" if f == "fedavg_ab_homo" else "AnchorLoRA")
        ax.axhline(0, color="#18201c", lw=1.2)
        ax.set_xlim(0, 6.6)
        ax.set_xticks(range(7))
        ax.set_title("Tablet's domain (man pages): solid = this run · dashed = ghost (same seed, nobody unplugged)\n"
                     "band = reference for tablet-only outage from round 2 (5 validation seeds)", loc="left", fontsize=10.5)
        if t >= 2:
            fig.text(0.765, 0.36, textwrap.fill(validation_sentence(), 44), va="top", fontsize=9, color="#18201c")
        ax.legend(loc="upper left", fontsize=10, frameon=False)
        fig.text(0.05, 0.975, "RECORDED, not live · validation run, seed 0, tablet unplugged by script from round 2\n"
                 "reduced config (batch 1×64, eval 8×64 tok/domain, 6 rounds) · Δ vs untuned on the same eval subset\n"
                 "SIMULATED device budgets · real SmolLM2-135M · real text", color="#5a3f94", weight="bold", fontsize=11, va="top")
        stamp(fig, "source: demo/fallback/recorded_live_s0.jsonl (live engine events) · ghosts + band: "
                   "demo/validation/runs/ghost_s0.json, demo/validation/results.json\nunplug = in-process Flower grid node "
                   "removed (LocalGrid.kill_node), not an OS-process kill")
        fig.savefig(OUT / f"frame3_recorded_live_r{t}.png")
        figs.append(fig)
    return figs


def gif(figs: list) -> None:
    from PIL import Image

    frames = []
    for t in range(1, len(figs) + 1):
        im = Image.open(OUT / f"frame3_recorded_live_r{t}.png").convert("RGB")
        frames.append(im.resize((im.width * 2 // 3, im.height * 2 // 3)))
    frames[0].save(OUT / "recorded_live.gif", save_all=True, append_images=frames[1:], duration=1600, loop=0)
    for f in figs:
        plt.close(f)


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    frame_gains()
    frame_outage()
    figs = live_frames()
    gif(figs)
    print("wrote", ", ".join(sorted(p.name for p in OUT.glob("*.png"))), "+ recorded_live.gif")
