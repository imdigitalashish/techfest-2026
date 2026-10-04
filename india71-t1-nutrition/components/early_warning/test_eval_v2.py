import pandas as pd

from components.early_warning import eval_v2


def test_pool_excludes_infants_and_non_normal():
    df = pd.DataFrame({"obs_status": ["normal", "normal", "mam", "normal"], "age_days": [100, 183, 400, 900]})
    out = eval_v2.pool_of(df)
    assert list(out.age_days) == [183, 900]


def test_episode_rankable_flag():
    rows = []
    for m in range(8):  # child A: 0-7 months old; child B: 12-19 months old
        rows.append(("A", m, 30 * m, -1.0 if m < 6 else -2.5))
        rows.append(("B", m, 365 + 30 * m, -1.0 if m < 6 else -2.5))
    truth = pd.DataFrame(rows, columns=["child_key", "month_index", "age_days", "true_wlz"]).assign(measured_on=pd.NaT)
    ep = eval_v2.episodes(truth).set_index("child_key")
    assert ep.loc["A", "onset"] == 6 and not ep.loc["A", "rankable"]  # window starts at ~3 months: infant pathway
    assert ep.loc["B", "rankable"]
