"""Synthetic FLN district simulator.

World interface (stable for Builder B)
------------------------------------
`make_world(seed:int, cfg:dict|None)->World` returns a dataclass containing pandas
DataFrames for one synthetic district. All public records are synthetic and must be
converted to contract models before crossing component boundaries.

Fields:
- schools: one row/school. dtypes include udise_code str(11), school_id str,
  school_name str, state_lgd/district_lgd/block_lgd/cluster_id str, rural bool,
  n_teachers int, single_teacher bool, grade3_enrolment int, share_sc/share_st float,
  ptr float, infra_index float, management str.
- children: one row/Grade-3 child. student_raw_id str, udise_code str, grade int,
  gender str, social_category str, home_language_matches_medium bool, theta_read/math
  float, true_read_level/true_math_level int, read_goal/math_goal bool. theta_* and
  true_* are hidden ground truth; public_view() drops them.
- teacher_reports: teacher-administered state assessment rows: student_raw_id,
  udise_code, subject {'language','numeracy'}, reported_level int, assessed_on date,
  source='state_assessment'.
- item_bank: classroom-tool item metadata: item_id, subject, level, competency_code,
  irt_a, irt_b, max_score, instrument='classroom_tool'.
- item_responses: classroom-tool responses: student_raw_id, udise_code, grade,
  item_id, subject, score {0,1}, administered_by='teacher', assessed_on date.
- survey_anchor: independent ASER/PARAKH-like sample child rows with observed_level,
  meets_goal, school/student IDs, subject; truth + small noise.
- udise: UDISE+-like covariate table, same school keys/covariates as schools.
- truth_school/truth_block: hidden true shares and inflation metadata. Hidden.

Meets grade goal proxy: reading level 4 (Std II story text) and maths level >= 3
(subtraction). This is a proxy mapping pending verification against NIPUN Bharat
Lakshya Soochi. Default target rates are placeholders to be replaced with cited
ASER/PARAKH numbers by the lead.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Optional

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class World:
    schools: pd.DataFrame
    children: pd.DataFrame
    teacher_reports: pd.DataFrame
    item_bank: pd.DataFrame
    item_responses: pd.DataFrame
    survey_anchor: pd.DataFrame
    udise: pd.DataFrame
    truth_school: pd.DataFrame
    truth_block: pd.DataFrame
    cfg: dict
    seed: int

    def public_view(self) -> "World":
        child_drop = [c for c in ["theta_read", "theta_math", "true_read_level", "true_math_level", "read_goal", "math_goal"] if c in self.children]
        empty_truth_school = self.truth_school.iloc[0:0].copy()
        empty_truth_block = self.truth_block.iloc[0:0].copy()
        return World(
            schools=self.schools.copy(),
            children=self.children.drop(columns=child_drop).copy(),
            teacher_reports=self.teacher_reports.copy(),
            item_bank=self.item_bank.copy(),
            item_responses=self.item_responses.copy(),
            survey_anchor=self.survey_anchor.copy(),
            udise=self.udise.copy(),
            truth_school=empty_truth_school,
            truth_block=empty_truth_block,
            cfg=self.cfg.copy(),
            seed=self.seed,
        )


READ_CODES = {1: "L.LETTER", 2: "L.WORD", 3: "L.PARA", 4: "L.STORY"}
MATH_CODES = {1: "M.NUM1_9", 2: "M.NUM11_99", 3: "M.SUB", 4: "M.DIV"}


def _levels(theta: np.ndarray, target_goal: float, goal_level: int) -> tuple[np.ndarray, np.ndarray]:
    # Threshold for the goal is chosen by quantile; remaining thresholds spread below/above.
    t_goal = float(np.quantile(theta, 1.0 - target_goal))
    thresholds = np.array([t_goal - 1.35, t_goal - 0.75, t_goal - 0.20, t_goal]) if goal_level == 4 else np.array([t_goal - 1.15, t_goal - 0.55, t_goal, t_goal + 0.7])
    levels = np.digitize(theta, thresholds).astype(int)
    return levels, thresholds


def _item_bank() -> pd.DataFrame:
    rows = []
    for subject, codes in [("language", READ_CODES), ("numeracy", MATH_CODES)]:
        for level, code in codes.items():
            for j in range(4):
                rows.append({
                    "item_id": f"{'L' if subject=='language' else 'M'}{level}_{j+1}",
                    "instrument": "classroom_tool",
                    "subject": subject,
                    "level": level,
                    "competency_code": code,
                    "max_score": 1.0,
                    "irt_a": float(0.85 + 0.15 * j + 0.08 * level),
                    "irt_b": float(-1.5 + 0.85 * level + 0.12 * (j - 1.5)),
                })
    return pd.DataFrame(rows)


def make_world(seed: int, cfg: Optional[dict] = None) -> World:
    cfg = {
        "n_blocks": 6, "n_clusters": 40, "n_schools": 600,
        "target_read_goal": 0.25, "target_math_goal": 0.30,
        "p_inflating_schools": 0.30, "survey_schools": 20, "survey_children_per_school": 10,
        **(cfg or {}),
    }
    rng = np.random.default_rng(seed)
    n_blocks, n_clusters, n_schools = int(cfg["n_blocks"]), int(cfg["n_clusters"]), int(cfg["n_schools"])
    blocks = [f"B{b:02d}" for b in range(1, n_blocks + 1)]
    cluster_blocks = np.array([blocks[i % n_blocks] for i in range(n_clusters)])
    clusters = [f"C{i+1:03d}" for i in range(n_clusters)]
    school_cluster = rng.choice(clusters, size=n_schools, replace=True)
    c_to_b = dict(zip(clusters, cluster_blocks))
    grade3 = rng.integers(5, 61, size=n_schools)
    single = rng.random(n_schools) < 0.10
    n_teachers = np.maximum(1, np.where(single, 1, rng.poisson(4, n_schools) + 1))
    ptr = grade3 / n_teachers
    infra = np.clip(rng.normal(0.58, 0.18, n_schools), 0, 1)
    rural = rng.random(n_schools) < 0.82
    share_sc = rng.beta(2.3, 6.0, n_schools)
    share_st = rng.beta(1.3, 10.0, n_schools)
    udise_codes = [f"2701{i:07d}" for i in range(1, n_schools + 1)]
    schools = pd.DataFrame({
        "school_id": [f"S{i+1:04d}" for i in range(n_schools)], "udise_code": udise_codes,
        "school_name": [f"Synthetic GPS {i+1:04d}" for i in range(n_schools)],
        "state_lgd": "27", "district_lgd": "2701",
        "block_lgd": [c_to_b[c] for c in school_cluster], "cluster_id": school_cluster,
        "management": "government", "rural": rural, "n_teachers": n_teachers,
        "single_teacher": single, "grade3_enrolment": grade3, "share_sc": share_sc,
        "share_st": share_st, "ptr": ptr, "infra_index": infra,
    })
    block_re = {b: rng.normal(0, 0.35) for b in blocks}
    school_re = rng.normal(0, 0.45, n_schools)
    child_rows = []
    for i, s in schools.iterrows():
        n = int(s.grade3_enrolment)
        base_read = block_re[s.block_lgd] + school_re[i] + 0.7 * s.infra_index - 0.018 * max(s.ptr - 25, 0) - (0.35 if s.single_teacher else 0)
        base_math = 0.1 + block_re[s.block_lgd] * 0.9 + school_re[i] * 0.8 + 0.55 * s.infra_index - 0.015 * max(s.ptr - 25, 0) - (0.28 if s.single_teacher else 0)
        p_cat = np.array([s.share_sc, s.share_st, max(0.0, 0.45 - s.share_sc / 2), max(0.0, 1 - s.share_sc - s.share_st - max(0.0, 0.45 - s.share_sc / 2))], dtype=float)
        cats = rng.choice(["sc", "st", "obc", "general"], size=n, p=p_cat / p_cat.sum())
        for j in range(n):
            home = bool(rng.random() < 0.78)
            disadv = (-0.18 if cats[j] in ("sc", "st") else 0.0) + (0.10 if home else -0.12)
            child_rows.append({
                "student_raw_id": f"raw_{s.udise_code}_{j+1:03d}", "udise_code": s.udise_code, "grade": 3,
                "gender": rng.choice(["f", "m", "x"], p=[0.49, 0.50, 0.01]), "social_category": cats[j],
                "home_language_matches_medium": home,
                "theta_read": float(base_read + disadv + rng.normal(0, 0.9)),
                "theta_math": float(base_math + disadv * 0.6 + rng.normal(0, 0.85)),
            })
    children = pd.DataFrame(child_rows)
    children["true_read_level"], read_thr = _levels(children.theta_read.to_numpy(), float(cfg["target_read_goal"]), 4)
    children["true_math_level"], math_thr = _levels(children.theta_math.to_numpy(), float(cfg["target_math_goal"]), 3)
    children["read_goal"] = children.true_read_level >= 4
    children["math_goal"] = children.true_math_level >= 3

    inflating = rng.random(n_schools) < float(cfg["p_inflating_schools"])
    q = np.where(inflating, rng.uniform(0.35, 0.85, n_schools), rng.uniform(0.02, 0.08, n_schools))
    k = np.where(inflating, rng.integers(1, 3, n_schools), 0)
    school_infl = dict(zip(schools.udise_code, inflating))
    school_q = dict(zip(schools.udise_code, q)); school_k = dict(zip(schools.udise_code, k))
    reports = []
    for _, ch in children.iterrows():
        for subj, col in [("language", "true_read_level"), ("numeracy", "true_math_level")]:
            lvl = int(ch[col]); u = ch.udise_code
            if school_infl[u] and rng.random() < school_q[u]:
                lvl = min(4, lvl + int(school_k[u]))
                if lvl == 3 and rng.random() < 0.45: lvl = 4 if subj == "language" else 3
            elif (not school_infl[u]) and rng.random() < school_q[u]:
                lvl = int(np.clip(lvl + rng.choice([-1, 1]), 0, 4))
            reports.append({"student_raw_id": ch.student_raw_id, "udise_code": u, "subject": subj, "reported_level": lvl, "assessed_on": date(2026, 9, 15), "source": "state_assessment"})
    teacher_reports = pd.DataFrame(reports)

    item_bank = _item_bank()
    resp = []
    for _, ch in children.iterrows():
        for _, it in item_bank.iterrows():
            theta = ch.theta_read if it.subject == "language" else ch.theta_math
            p = 1.0 / (1.0 + np.exp(-float(it.irt_a) * (theta - float(it.irt_b))))
            resp.append({"student_raw_id": ch.student_raw_id, "udise_code": ch.udise_code, "grade": 3, "item_id": it.item_id,
                         "subject": it.subject, "score": float(rng.random() < p), "administered_by": "teacher", "assessed_on": date(2026, 9, 20)})
    item_responses = pd.DataFrame(resp)

    sample_schools = rng.choice(schools.udise_code, size=min(int(cfg["survey_schools"]), n_schools), replace=False)
    survey = []
    for u in sample_schools:
        kids = children[children.udise_code == u].sample(n=min(int(cfg["survey_children_per_school"]), int((children.udise_code == u).sum())), random_state=int(rng.integers(1e9)))
        for _, ch in kids.iterrows():
            for subj, col, goal in [("language", "true_read_level", 4), ("numeracy", "true_math_level", 3)]:
                obs = int(ch[col])
                if rng.random() < 0.05: obs = int(np.clip(obs + rng.choice([-1, 1]), 0, 4))
                survey.append({"student_raw_id": ch.student_raw_id, "udise_code": u, "subject": subj, "observed_level": obs,
                               "meets_goal": bool(obs >= goal), "source": "aser_anchor", "assessed_on": date(2026, 9, 25)})
    survey_anchor = pd.DataFrame(survey)
    udise = schools[["udise_code", "school_name", "state_lgd", "district_lgd", "block_lgd", "cluster_id", "management", "rural", "n_teachers", "single_teacher", "grade3_enrolment", "share_sc", "share_st", "ptr", "infra_index"]].copy()
    trows = []
    for u, g in children.groupby("udise_code"):
        rep = teacher_reports[teacher_reports.udise_code == u]
        trows.append({"udise_code": u, "true_read_goal_rate": float(g.read_goal.mean()), "true_math_goal_rate": float(g.math_goal.mean()),
                      "inflating_school": bool(school_infl[u]), "inflation_q": float(school_q[u]), "inflation_k": int(school_k[u]),
                      "reported_read_goal_rate": float((rep[rep.subject == "language"].reported_level >= 4).mean()),
                      "reported_math_goal_rate": float((rep[rep.subject == "numeracy"].reported_level >= 3).mean())})
    truth_school = pd.DataFrame(trows)
    truth_block = schools.merge(truth_school, on="udise_code").groupby("block_lgd").agg(
        n_children=("grade3_enrolment", "sum"), true_read_goal_rate=("true_read_goal_rate", "mean"), true_math_goal_rate=("true_math_goal_rate", "mean"),
        inflating_rate=("inflating_school", "mean")).reset_index()
    cfg = cfg.copy(); cfg["read_thresholds"] = read_thr.tolist(); cfg["math_thresholds"] = math_thr.tolist()
    return World(schools, children, teacher_reports, item_bank, item_responses, survey_anchor, udise, truth_school, truth_block, cfg, seed)
