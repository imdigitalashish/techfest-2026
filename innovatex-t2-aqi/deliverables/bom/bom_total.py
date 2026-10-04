"""Kit totals from bom.csv (prices the lead saw on the vendor pages; see verified_by_lead_ist). Rows whose subsystem
starts with 'alt' or ends with '_option' are alternatives and are NOT in the kit total.
Run: python bom_total.py → bom_total.json"""
import csv, json, os
HERE = os.path.dirname(os.path.abspath(__file__))
rows = list(csv.DictReader(open(os.path.join(HERE, "bom.csv"))))
kit = [r for r in rows if not (r["subsystem"].startswith("alt") or r["subsystem"].endswith("_option"))]
by = {}
for r in kit:
    by[r["subsystem"]] = by.get(r["subsystem"], 0) + int(r["qty_per_kit"]) * int(r["unit_inr_incl_gst"])
per_node = sum(int(r["unit_inr_incl_gst"]) for r in kit if r["subsystem"] == "node")
total = sum(by.values())
out = {"kit_total_inr": total, "by_subsystem_inr": by, "per_node_inr": per_node, "n_nodes": 4,
       "wind_share_of_total": round(by.get("wind", 0) / total, 3),
       "out_of_stock_items_in_kit": [r["item"] for r in kit if "out" in r["stock_seen"].lower()],
       "not_included": ["5 V buck converters", "cabling, glands, connectors", "masts and mounting", "radiation shields",
                        "SIM + data plan", "gateway power supply", "installation labour", "reference co-location", "maintenance"],
       "note": "Parts as listed on vendor pages, incl. GST, single-unit retail. Not an installed or lifetime cost."}
json.dump(out, open(os.path.join(HERE, "bom_total.json"), "w"), indent=1)
print(json.dumps(out, indent=1))
