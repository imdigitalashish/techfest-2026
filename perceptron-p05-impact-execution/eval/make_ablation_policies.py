"""E8 (validation seeds) ablation: separate the QP schedule, the legacy feedback (a ~1.2x speed-up)
and the corrected pre-trade feedback. Writes eval/policies/e8_ablation.json from calibration.json."""
import json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
cal = json.load(open(os.path.join(ROOT, "eval", "results", "calibration.json")))
k = cal["kernel"]
ia = dict(inst_cost=cal["inst_cost_cents_per_share2"], g_tr=k["g_tr"], tau_s=k["tau_s"], beta=0.5, max_levels=1, use_limit=False)
specs = [{"kind": "TWAP", "label": "TWAP"},
         {"kind": "IA", "label": "QP_only", **ia, "use_qp": True, "use_feedback": False},
         {"kind": "IA", "label": "IA_sched_only", **ia, "use_qp": True, "use_feedback": True},
         {"kind": "IA", "label": "IA_sched_fixed", **ia, "use_qp": True, "use_feedback": True, "ref_mode": "pre_trade"},
         {"kind": "IA", "label": "TWAP_legacy_fb", **ia, "use_qp": False, "use_feedback": True}]
json.dump(specs, open(os.path.join(ROOT, "eval", "policies", "e8_ablation.json"), "w"), indent=1)
print("wrote eval/policies/e8_ablation.json")
