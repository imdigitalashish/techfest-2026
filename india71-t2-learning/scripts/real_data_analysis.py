#!/usr/bin/env python3
"""Real public-data checks for state-level FLN commensurability claims."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
ASER = ROOT / "data" / "public" / "aser2024_state_std3.csv"
PARAKH = ROOT / "data" / "public" / "parakh2024_grade3_state.csv"
UDISE = ROOT / "data" / "public" / "udise2425_state.csv"
OUT = ROOT / "eval" / "results" / "real_data_analysis.md"
COMMAND = "python3 scripts/extract_parakh2024_state.py && python3 scripts/extract_udise2425_state.py && python3 scripts/real_data_analysis.py"

READING = "Std III read Std II level text"
SUBTRACTION = "Std III at least subtraction"


def state_key(value: str) -> str:
    aliases = {
        "Delhi": "NCT of Delhi",
        "Jammu & Kashmir": "Jammu and Kashmir",
    }
    return aliases.get(value, value)


def fmt(value: float) -> str:
    return f"{value:.3f}"


def corr_pair(df: pd.DataFrame, x: str, y: str) -> dict[str, float | int]:
    clean = df[[x, y]].dropna()
    if len(clean) < 3:
        return {"n": len(clean), "r": np.nan, "rho": np.nan}
    return {
        "n": int(len(clean)),
        "r": float(stats.pearsonr(clean[x], clean[y]).statistic),
        "rho": float(stats.spearmanr(clean[x], clean[y]).statistic),
    }


def rank_comparison(df: pd.DataFrame, left: str, right: str) -> tuple[dict[str, float | int], pd.DataFrame]:
    clean = df[["state", left, right]].dropna().copy()
    clean["left_rank"] = clean[left].rank(ascending=False, method="min").astype(int)
    clean["right_rank"] = clean[right].rank(ascending=False, method="min").astype(int)
    clean["abs_rank_diff"] = (clean["left_rank"] - clean["right_rank"]).abs()
    metrics = corr_pair(clean, left, right)
    metrics["mean_abs_rank_difference"] = float(clean["abs_rank_diff"].mean())
    disagreements = clean.sort_values(["abs_rank_diff", "state"], ascending=[False, True]).head(5)
    return metrics, disagreements[["state", "left_rank", "right_rank", "abs_rank_diff"]]


def loso_linear(df: pd.DataFrame, x: str, y: str) -> dict[str, float | int]:
    clean = df[[x, y]].dropna().copy()
    preds = []
    baselines = []
    actuals = []
    for idx in clean.index:
        train = clean.drop(index=idx)
        test_x = float(clean.loc[idx, x])
        actual = float(clean.loc[idx, y])
        slope, intercept = np.polyfit(train[x].to_numpy(float), train[y].to_numpy(float), deg=1)
        preds.append(float(slope * test_x + intercept))
        baselines.append(float(train[y].mean()))
        actuals.append(actual)
    actual_arr = np.array(actuals)
    return {
        "n": int(len(clean)),
        "linear_loso_mae": float(np.mean(np.abs(np.array(preds) - actual_arr))),
        "baseline_loso_mae": float(np.mean(np.abs(np.array(baselines) - actual_arr))),
    }


def top_bottom_changes(aser: pd.DataFrame, indicator: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    pivot = (
        aser[(aser["school_type"] == "government") & (aser["indicator"] == indicator) & (aser["state"] != "All India")]
        .pivot(index="state", columns="year", values="value_pct")
        .dropna(subset=[2022, 2024])
        .reset_index()
    )
    pivot["change_pp"] = pivot[2024] - pivot[2022]
    cols = ["state", 2022, 2024, "change_pp"]
    return pivot.sort_values(["change_pp", "state"], ascending=[False, True]).head(5)[cols], pivot.sort_values(["change_pp", "state"]).head(5)[cols]


def md_table(df: pd.DataFrame, columns: list[str] | None = None) -> str:
    show = df if columns is None else df[columns]
    headers = [str(col) for col in show.columns]
    rows = []
    for _, row in show.iterrows():
        rendered = []
        for value in row.tolist():
            if isinstance(value, float):
                rendered.append(f"{value:.2f}")
            else:
                rendered.append(str(value))
        rows.append(rendered)
    widths = [
        max(len(headers[i]), *(len(row[i]) for row in rows)) if rows else len(headers[i])
        for i in range(len(headers))
    ]

    def line(values: list[str]) -> str:
        return "| " + " | ".join(value.ljust(widths[i]) for i, value in enumerate(values)) + " |"

    separator = "| " + " | ".join("-" * widths[i] for i in range(len(headers))) + " |"
    return "\n".join([line(headers), separator, *[line(row) for row in rows]])


def main() -> None:
    aser = pd.read_csv(ASER)
    aser["state"] = aser["state"].map(state_key)
    aser["value_pct"] = pd.to_numeric(aser["value_pct"])
    parakh = pd.read_csv(PARAKH)
    parakh["state"] = parakh["state"].map(state_key)
    parakh["value_pct"] = pd.to_numeric(parakh["value_pct"])
    udise = pd.read_csv(UDISE)
    udise["state"] = udise["state"].map(state_key)

    aser_2024 = (
        aser[(aser["school_type"] == "government") & (aser["year"] == 2024)]
        .pivot(index="state", columns="indicator", values="value_pct")
        .rename(columns={READING: "aser_reading", SUBTRACTION: "aser_subtraction"})
        .reset_index()
    )
    parakh_pivot = (
        parakh.pivot(index="state", columns="subject", values="value_pct")
        .rename(columns={"Language": "parakh_language", "Mathematics": "parakh_mathematics"})
        .reset_index()
    )
    learning = aser_2024.merge(parakh_pivot, on="state", how="inner")

    reading_metrics, reading_disagree = rank_comparison(learning, "aser_reading", "parakh_language")
    math_metrics, math_disagree = rank_comparison(learning, "aser_subtraction", "parakh_mathematics")
    reading_link = loso_linear(learning, "parakh_language", "aser_reading")
    math_link = loso_linear(learning, "parakh_mathematics", "aser_subtraction")

    udise_features = udise[udise["state"] != "India"].copy()
    udise_features["single_teacher_school_share"] = udise_features["single_teacher_schools"] / udise_features["schools"]
    cov = udise_features.merge(learning, on="state", how="inner")
    cov_rows = []
    for covariate, label in [("single_teacher_school_share", "Single-teacher school share"), ("ptr", "PTR")]:
        for outcome, outcome_label in [("aser_reading", "ASER 2024 govt reading"), ("parakh_language", "PARAKH Grade 3 Language")]:
            metrics = corr_pair(cov, covariate, outcome)
            cov_rows.append({"covariate": label, "outcome": outcome_label, **metrics})
    cov_table = pd.DataFrame(cov_rows)

    reading_top, reading_bottom = top_bottom_changes(aser, READING)
    math_top, math_bottom = top_bottom_changes(aser, SUBTRACTION)

    lines = [
        "# Real public-data state-level learning checks",
        "",
        f"Command: `{COMMAND}`",
        "",
        "Caveat: ASER is a rural household oral assessment of fixed reading/arithmetic levels, while PARAKH is a school-based written assessment reporting average percent correct. These are different constructs and populations; this is a state-level concordance check, not an individual-score equivalence claim.",
        "",
        "## ASER 2024 vs PARAKH 2024",
        "",
        "| Pair | n | Pearson r | Spearman rho | Mean absolute rank difference |",
        "|---|---:|---:|---:|---:|",
        f"| ASER govt Std III reading vs PARAKH Grade 3 Language | {reading_metrics['n']} | {fmt(reading_metrics['r'])} | {fmt(reading_metrics['rho'])} | {reading_metrics['mean_abs_rank_difference']:.2f} |",
        f"| ASER govt Std III subtraction vs PARAKH Grade 3 Mathematics | {math_metrics['n']} | {fmt(math_metrics['r'])} | {fmt(math_metrics['rho'])} | {math_metrics['mean_abs_rank_difference']:.2f} |",
        "",
        "Top rank disagreements: ASER reading vs PARAKH Language",
        "",
        md_table(reading_disagree.rename(columns={"left_rank": "aser_rank", "right_rank": "parakh_rank"})),
        "",
        "Top rank disagreements: ASER subtraction vs PARAKH Mathematics",
        "",
        md_table(math_disagree.rename(columns={"left_rank": "aser_rank", "right_rank": "parakh_rank"})),
        "",
        "## Linking check: PARAKH state average to ASER state percentage",
        "",
        "| Link | n | LOSO linear MAE (pp) | LOSO mean-baseline MAE (pp) |",
        "|---|---:|---:|---:|",
        f"| PARAKH Language -> ASER reading | {reading_link['n']} | {reading_link['linear_loso_mae']:.2f} | {reading_link['baseline_loso_mae']:.2f} |",
        f"| PARAKH Mathematics -> ASER subtraction | {math_link['n']} | {math_link['linear_loso_mae']:.2f} | {math_link['baseline_loso_mae']:.2f} |",
        "",
        "## UDISE+ covariates vs learning",
        "",
        md_table(cov_table),
        "",
        "## ASER government-school change, 2022 to 2024",
        "",
        "Reading: top 5 gains",
        "",
        md_table(reading_top),
        "",
        "Reading: bottom 5 changes",
        "",
        md_table(reading_bottom),
        "",
        "Subtraction: top 5 gains",
        "",
        md_table(math_top),
        "",
        "Subtraction: bottom 5 changes",
        "",
        md_table(math_bottom),
        "",
    ]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines), encoding="utf-8")

    print(f"wrote {OUT}")
    print(
        "reading/lang "
        f"n={reading_metrics['n']} r={fmt(reading_metrics['r'])} rho={fmt(reading_metrics['rho'])} "
        f"MARD={reading_metrics['mean_abs_rank_difference']:.2f} "
        f"LOSO_MAE={reading_link['linear_loso_mae']:.2f} baseline={reading_link['baseline_loso_mae']:.2f}"
    )
    print(
        "subtraction/math "
        f"n={math_metrics['n']} r={fmt(math_metrics['r'])} rho={fmt(math_metrics['rho'])} "
        f"MARD={math_metrics['mean_abs_rank_difference']:.2f} "
        f"LOSO_MAE={math_link['linear_loso_mae']:.2f} baseline={math_link['baseline_loso_mae']:.2f}"
    )


if __name__ == "__main__":
    main()
