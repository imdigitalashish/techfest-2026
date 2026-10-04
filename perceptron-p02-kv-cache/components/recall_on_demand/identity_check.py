"""Identity / plumbing checks for RoD (Supervisor 16:24 spot-check). Dev seed only (100); never a test split.

I1  exact-KV assembly: resident KV + the ORIGINAL KV of every evicted block (re-ordered as RoD assembles it) must
    reproduce the full cache's first-answer-token logits and greedy answers.
I2  re-prefill plumbing: re-prefilling the whole evicted span [ev0, ev1) in ONE pass on top of the sinks (i.e. with its
    true prefix) must reproduce the original KV of that span and the full cache's answers.
I3  bookkeeping: resident positions + all evicted 64-token blocks partition [0, T) exactly (no gap, no duplicate).
Also logs, per keep fraction, the budget arithmetic RoD uses (B, B_res, B_rec, m, stored bytes).
Usage (VM, ~/p02): HF_HUB_OFFLINE=1 ~/venv_kvp/bin/python components/recall_on_demand/identity_check.py
"""
from __future__ import annotations

import json
import random
import sys
from pathlib import Path

import torch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "eval"))
import kvbench_torch as kb  # noqa: E402

CFG = {"layer": 5, "bits": 4, "scorer": "softmax_lift", "lexical": False, "qsel": "content"}


@torch.inference_mode()
def first_logits(E, store, T, q_ids):
    c = store.fork()
    h, _ = E.forward(q_ids, T, c)
    return E.model.lm_head(h[:, -1, :])[0].float()


def main():
    torch.set_num_threads(int(sys.argv[1]) if len(sys.argv) > 1 else 4)
    snap = kb.glob.glob(kb.os.path.expanduser("~/.cache/huggingface/hub/models--mlx-community--Llama-3.2-1B-Instruct-4bit/snapshots/*"))[0]
    tok = kb.AutoTokenizer.from_pretrained(snap)
    E = kb.Engine(kb.load_model(), tok)
    paras = (ROOT / ".data" / "haystack.txt").read_text(encoding="utf-8").split("\n")
    ctx_ids, qs = kb.make_sample(tok, paras, 4096, 4, random.Random(100), "literal")
    T = len(ctx_ids)
    Kf, Vf, _, caps = E.prefill(ctx_ids)
    full = kb.Cache(Kf, Vf)
    ref = [(first_logits(E, full, T, q), E.answer(full, T, q)) for q, _ in qs]
    out = {"seed": 100, "T": T, "per_keep": {}}
    for f in (0.1, 0.25, 0.5, 1.0):
        B = max(kb.N_SINK + kb.N_RECENT + 1, round(f * T))
        st = kb.rod_build(E, Kf, Vf, ctx_ids, B, CFG, caps)
        ev0, ev1 = st["ev0"], st["ev1"]
        nblk = -(-(ev1 - ev0) // kb.BLOCK)
        res_pos = list(range(kb.N_SINK)) + list(range(T - (st["B_res"] - kb.N_SINK), T))
        blk_pos = [p for b in range(nblk) for p in range(ev0 + b * kb.BLOCK, min(ev0 + (b + 1) * kb.BLOCK, ev1))]
        i3 = sorted(res_pos + blk_pos) == list(range(T))
        # I1: resident + exact KV of all evicted blocks, appended after the resident KV as RoD does
        aug = kb.Cache([torch.cat([st["Kr"][l], Kf[l][:, :, ev0:ev1]], 2) for l in range(E.nl)],
                       [torch.cat([st["Vr"][l], Vf[l][:, :, ev0:ev1]], 2) for l in range(E.nl)])
        i1 = [(float((first_logits(E, aug, T, q) - ref[i][0]).abs().max()), E.answer(aug, T, q) == ref[i][1])
              for i, (q, _) in enumerate(qs)]
        # I2: re-prefill [ev0, ev1) in one pass after the sinks
        c = kb.Cache([k[:, :, :kb.N_SINK] for k in st["Kr"]], [v[:, :, :kb.N_SINK] for v in st["Vr"]])
        E.forward(st["ids"][ev0:ev1].tolist(), ev0, c)
        kv_diff = max(float((c.tk[l].float() - Kf[l][:, :, ev0:ev1].float()).abs().max()) for l in range(E.nl))
        aug2 = kb.Cache([torch.cat([st["Kr"][l], c.tk[l]], 2) for l in range(E.nl)],
                        [torch.cat([st["Vr"][l], c.tv[l]], 2) for l in range(E.nl)])
        i2 = [E.answer(aug2, T, q) == ref[i][1] for i, (q, _) in enumerate(qs)]
        out["per_keep"][str(f)] = {"B": B, "B_res": st["B_res"], "B_rec": st["B_rec"], "m": st["B_rec"] // kb.BLOCK,
                                   "evicted_tokens": ev1 - ev0, "n_blocks": nblk, "stored_MiB": round(st["stored_bytes"] / 2**20, 3),
                                   "I3_partition_ok": i3, "I1_max_abs_dlogit": round(max(x[0] for x in i1), 5),
                                   "I1_answers_equal": sum(x[1] for x in i1), "I2_max_abs_dkv": round(kv_diff, 4),
                                   "I2_answers_equal": sum(i2), "n_questions": len(qs)}
        print(f, json.dumps(out["per_keep"][str(f)]), flush=True)
    out["full_answers"] = [r[1] for r in ref]
    out["command"] = "HF_HUB_OFFLINE=1 ~/venv_kvp/bin/python components/recall_on_demand/identity_check.py 4"
    (ROOT / "eval" / "results" / "identity_check_dev100.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
