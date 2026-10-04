"""Generate eval/policies/test.json from eval/results/calibration.json (train-seed calibration only)."""
import json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
cal = json.load(open(os.path.join(ROOT, "eval", "results", "calibration.json")))
k = cal["kernel"]
ia = dict(inst_cost=cal["inst_cost_cents_per_share2"], g_tr=k["g_tr"], tau_s=k["tau_s"])
specs = [{"kind": "TWAP", "label": "TWAP"},
         {"kind": "VWAP", "label": "VWAP", "cum_profile": cal["vwap_cum_profile"]},
         {"kind": "IA", "label": "IA_full", **ia, "beta": 0.5, "max_levels": 1, "use_qp": True, "use_feedback": True, "use_limit": True},
         {"kind": "IA", "label": "IA_sched_only", **ia, "beta": 0.5, "max_levels": 1, "use_qp": True, "use_feedback": True, "use_limit": False},
         {"kind": "IA", "label": "TWAP_touch_limit", **ia, "beta": 0.0, "max_levels": 1, "use_qp": False, "use_feedback": False, "use_limit": True}]
json.dump(specs, open(os.path.join(ROOT, "eval", "policies", "test.json"), "w"), indent=1)
print("wrote eval/policies/test.json")
