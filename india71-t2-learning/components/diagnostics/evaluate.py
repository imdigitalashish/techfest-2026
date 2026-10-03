from __future__ import annotations

from sklearn.metrics import accuracy_score, f1_score, brier_score_loss
from eval.sim.world import make_world
from components.diagnostics.engine import aser_rule, bayes_irt, adaptive_test


def main() -> None:
    w = make_world(101, {"n_schools": 80, "n_clusters": 8})
    rows = w.children.sample(n=800, random_state=101)
    for subject, true_col, goal_col, thr_key in [("language", "true_read_level", "read_goal", "read_thresholds"), ("numeracy", "true_math_level", "math_goal", "math_thresholds")]:
        y=[]; pred=[]; prob=[]; cat_items=[]
        for _, ch in rows.iterrows():
            d = bayes_irt(ch.student_raw_id, ch.udise_code, 3, subject, w.item_responses, w.item_bank, w.cfg[thr_key])
            c, used = adaptive_test(ch.student_raw_id, ch.udise_code, 3, subject, w.item_responses, w.item_bank, w.cfg[thr_key])
            y.append(int(ch[true_col])); pred.append(d.level); prob.append(d.meets_grade_goal); cat_items.append(len(used))
        print(f"{subject}: level_accuracy={accuracy_score(y,pred):.3f} macro_f1={f1_score(y,pred,average='macro'):.3f} brier_meets_goal={brier_score_loss([int(v) for v in rows[goal_col]], prob):.3f} mean_items_full=16.0 mean_items_cat={sum(cat_items)/len(cat_items):.2f}")

if __name__ == "__main__":
    main()
