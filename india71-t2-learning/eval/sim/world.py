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
    """Vectorised simulator (same distributions as the original loop version; different RNG stream).

    cfg["inflation_need_corr"] (default 0.0): if > 0, schools with lower true performance are more
    likely to inflate (logit P(inflate) = logit(p_inflating_schools) - corr * z, where z is the
    standardised school mean reading ability). Used only for the allocation stress test.
    """
    cfg = {
        "n_blocks": 6, "n_clusters": 40, "n_schools": 600,
        "target_read_goal": 0.25, "target_math_goal": 0.30,
        "p_inflating_schools": 0.30, "survey_schools": 20, "survey_children_per_school": 10,
        "inflation_need_corr": 0.0,
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
    udise_codes = np.array([f"2701{i:07d}" for i in range(1, n_schools + 1)])
    block_of_school = np.array([c_to_b[c] for c in school_cluster])
    schools = pd.DataFrame({
        "school_id": [f"S{i+1:04d}" for i in range(n_schools)], "udise_code": udise_codes,
        "school_name": [f"Synthetic GPS {i+1:04d}" for i in range(n_schools)],
        "state_lgd": "27", "district_lgd": "2701",
        "block_lgd": block_of_school, "cluster_id": school_cluster,
        "management": "government", "rural": rural, "n_teachers": n_teachers,
        "single_teacher": single, "grade3_enrolment": grade3, "share_sc": share_sc,
        "share_st": share_st, "ptr": ptr, "infra_index": infra,
    })
    block_re = {b: rng.normal(0, 0.35) for b in blocks}
    school_re = rng.normal(0, 0.45, n_schools)
    bre = np.array([block_re[b] for b in block_of_school])
    excess_ptr = np.maximum(ptr - 25, 0)
    base_read = bre + school_re + 0.7 * infra - 0.018 * excess_ptr - np.where(single, 0.35, 0.0)
    base_math = 0.1 + bre * 0.9 + school_re * 0.8 + 0.55 * infra - 0.015 * excess_ptr - np.where(single, 0.28, 0.0)
    # children: one row per enrolled Grade-3 child
    sch_idx = np.repeat(np.arange(n_schools), grade3)
    n_child = int(grade3.sum())
    j_in_school = np.concatenate([np.arange(1, int(k) + 1) for k in grade3])
    p_obc = np.maximum(0.0, 0.45 - share_sc / 2)
    p_cat = np.stack([share_sc, share_st, p_obc, np.maximum(0.0, 1 - share_sc - share_st - p_obc)], axis=1)
    p_cat = p_cat / p_cat.sum(axis=1, keepdims=True)
    cdf = np.cumsum(p_cat, axis=1)[sch_idx]
    cat_idx = (rng.random(n_child)[:, None] > cdf).sum(axis=1).clip(0, 3)
    cats = np.array(["sc", "st", "obc", "general"])[cat_idx]
    home = rng.random(n_child) < 0.78
    gender = rng.choice(np.array(["f", "m", "x"]), size=n_child, p=[0.49, 0.50, 0.01])
    disadv = np.where(np.isin(cats, ["sc", "st"]), -0.18, 0.0) + np.where(home, 0.10, -0.12)
    theta_read = base_read[sch_idx] + disadv + rng.normal(0, 0.9, n_child)
    theta_math = base_math[sch_idx] + disadv * 0.6 + rng.normal(0, 0.85, n_child)
    child_udise = udise_codes[sch_idx]
    children = pd.DataFrame({
        "student_raw_id": [f"raw_{u}_{j:03d}" for u, j in zip(child_udise, j_in_school)],
        "udise_code": child_udise, "grade": 3, "gender": gender, "social_category": cats,
        "home_language_matches_medium": home, "theta_read": theta_read, "theta_math": theta_math,
    })
    children["true_read_level"], read_thr = _levels(children.theta_read.to_numpy(), float(cfg["target_read_goal"]), 4)
    children["true_math_level"], math_thr = _levels(children.theta_math.to_numpy(), float(cfg["target_math_goal"]), 3)
    children["read_goal"] = children.true_read_level >= 4
    children["math_goal"] = children.true_math_level >= 3

    p0 = float(cfg["p_inflating_schools"]); corr = float(cfg["inflation_need_corr"])
    if corr > 0:
        z = pd.Series(theta_read).groupby(sch_idx).mean().reindex(range(n_schools)).fillna(0).to_numpy()
        z = (z - z.mean()) / max(z.std(), 1e-9)
        logit = np.log(p0 / (1 - p0)) - corr * z
        p_infl = 1 / (1 + np.exp(-logit))
        p_infl = p_infl * (p0 / p_infl.mean())
        inflating = rng.random(n_schools) < np.clip(p_infl, 0, 1)
    else:
        inflating = rng.random(n_schools) < p0
    q = np.where(inflating, rng.uniform(0.35, 0.85, n_schools), rng.uniform(0.02, 0.08, n_schools))
    k = np.where(inflating, rng.integers(1, 3, n_schools), 0)
    rep_frames = []
    for subj, col in [("language", "true_read_level"), ("numeracy", "true_math_level")]:
        lvl = children[col].to_numpy().astype(int).copy()
        infl_c = inflating[sch_idx]; q_c = q[sch_idx]; k_c = k[sch_idx]
        u1 = rng.random(n_child); u2 = rng.random(n_child); sign = rng.choice(np.array([-1, 1]), size=n_child)
        up = infl_c & (u1 < q_c)
        lvl_up = np.minimum(4, lvl + k_c)
        if subj == "language":
            lvl_up = np.where((lvl_up == 3) & (u2 < 0.45), 4, lvl_up)
        noise = (~infl_c) & (u1 < q_c)
        new = np.where(up, lvl_up, np.where(noise, np.clip(lvl + sign, 0, 4), lvl))
        rep_frames.append(pd.DataFrame({"student_raw_id": children.student_raw_id.to_numpy(), "udise_code": child_udise, "subject": subj,
                                        "reported_level": new.astype(int), "assessed_on": date(2026, 9, 15), "source": "state_assessment"}))
    teacher_reports = pd.concat(rep_frames, ignore_index=True)

    item_bank = _item_bank()
    resp_frames = []
    for subj, theta in [("language", theta_read), ("numeracy", theta_math)]:
        bank = item_bank[item_bank.subject == subj]
        a = bank.irt_a.to_numpy(); b = bank.irt_b.to_numpy()
        p = 1.0 / (1.0 + np.exp(-a[None, :] * (theta[:, None] - b[None, :])))
        score = (rng.random(p.shape) < p).astype(float)
        resp_frames.append(pd.DataFrame({
            "student_raw_id": np.repeat(children.student_raw_id.to_numpy(), len(bank)),
            "udise_code": np.repeat(child_udise, len(bank)), "grade": 3,
            "item_id": np.tile(bank.item_id.to_numpy(), n_child), "subject": subj,
            "score": score.ravel(), "administered_by": "teacher", "assessed_on": date(2026, 9, 20)}))
    item_responses = pd.concat(resp_frames, ignore_index=True)

    sample_schools = rng.choice(udise_codes, size=min(int(cfg["survey_schools"]), n_schools), replace=False)
    survey = []
    for u in sample_schools:
        kids = children[children.udise_code == u]
        kids = kids.sample(n=min(int(cfg["survey_children_per_school"]), len(kids)), random_state=int(rng.integers(1e9)))
        for subj, col, goal in [("language", "true_read_level", 4), ("numeracy", "true_math_level", 3)]:
            obs = kids[col].to_numpy().astype(int)
            flip = rng.random(len(obs)) < 0.05
            obs = np.where(flip, np.clip(obs + rng.choice(np.array([-1, 1]), size=len(obs)), 0, 4), obs)
            survey.append(pd.DataFrame({"student_raw_id": kids.student_raw_id.to_numpy(), "udise_code": u, "subject": subj, "observed_level": obs,
                                        "meets_goal": obs >= goal, "source": "aser_anchor", "assessed_on": date(2026, 9, 25)}))
    survey_anchor = pd.concat(survey, ignore_index=True)
    udise = schools[["udise_code", "school_name", "state_lgd", "district_lgd", "block_lgd", "cluster_id", "management", "rural", "n_teachers", "single_teacher", "grade3_enrolment", "share_sc", "share_st", "ptr", "infra_index"]].copy()
    tr = children.groupby("udise_code", sort=True).agg(true_read_goal_rate=("read_goal", "mean"), true_math_goal_rate=("math_goal", "mean"))
    rr = teacher_reports.assign(g=lambda d: np.where(d.subject == "language", d.reported_level >= 4, d.reported_level >= 3)).groupby(["udise_code", "subject"]).g.mean().unstack()
    truth_school = tr.join(rr.rename(columns={"language": "reported_read_goal_rate", "numeracy": "reported_math_goal_rate"})).reset_index()
    meta = pd.DataFrame({"udise_code": udise_codes, "inflating_school": inflating, "inflation_q": q.astype(float), "inflation_k": k.astype(int)})
    truth_school = truth_school.merge(meta, on="udise_code")[["udise_code", "true_read_goal_rate", "true_math_goal_rate", "inflating_school", "inflation_q", "inflation_k", "reported_read_goal_rate", "reported_math_goal_rate"]]
    truth_school["true_read_goal_rate"] = truth_school.true_read_goal_rate.astype(float)
    truth_school["true_math_goal_rate"] = truth_school.true_math_goal_rate.astype(float)
    truth_block = schools.merge(truth_school, on="udise_code").groupby("block_lgd").agg(
        n_children=("grade3_enrolment", "sum"), true_read_goal_rate=("true_read_goal_rate", "mean"), true_math_goal_rate=("true_math_goal_rate", "mean"),
        inflating_rate=("inflating_school", "mean")).reset_index()
    cfg = cfg.copy(); cfg["read_thresholds"] = read_thr.tolist(); cfg["math_thresholds"] = math_thr.tolist()
    return World(schools, children, teacher_reports, item_bank, item_responses, survey_anchor, udise, truth_school, truth_block, cfg, seed)
