"""Logit-parity checks for the torch engine (run on the VM after setup_torch.sh).

(1) Explicit-cache engine (chunked prefill + one incremental step) vs the HF reference forward, with KV kept in
    fp32 (should agree to float rounding) and in fp16 (the deployed setting; small, reported deviation).
(2) HF torch vs MLX (mlx_lm, same dequantised weights, CPU) on a short prompt: cross-backend parity.
Usage: python eval/parity_torch.py  -> prints one JSON line; exit 1 if (1) with fp32 KV disagrees.
"""
import json
import sys
from pathlib import Path

import torch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kvbench_torch as kb  # noqa: E402


def engine_logits(E, ids):
    c = kb.Cache(nl=E.nl)
    T = len(ids) - 1
    for a in range(0, T, 64):
        E.forward(ids[a:min(a + 64, T)], a, c)
    h, _ = E.forward(ids[-1:], T, c)
    return E.model.lm_head(h[:, -1, :])[0]


def main():
    torch.set_num_threads(8)
    model = kb.load_model()
    snap = kb.glob.glob(kb.os.path.expanduser("~/.cache/huggingface/hub/models--mlx-community--Llama-3.2-1B-Instruct-4bit/snapshots/*"))[0]
    tok = kb.AutoTokenizer.from_pretrained(snap)
    E = kb.Engine(model, tok)
    text = (kb.ROOT / ".data" / "haystack.txt").read_text().split("\n")[7][:1200]
    ids = tok.encode(kb.chat(tok, text + "\n\nSummarise the text in one sentence."), add_special_tokens=False)[:300]
    with torch.inference_mode():
        ref = model(torch.tensor([ids])).logits[0, -1].float()
    out = {"n_tokens": len(ids)}
    for name, dt in (("fp32_kv", torch.float32), ("fp16_kv", torch.float16)):
        kb.KV_DTYPE = dt
        with torch.inference_mode():
            lg = engine_logits(E, ids).float()
        out[name] = {"max_abs_dlogit": round(float((lg - ref).abs().max()), 5),
                     "argmax_equal": bool(lg.argmax() == ref.argmax()),
                     "top5_overlap": len(set(lg.topk(5).indices.tolist()) & set(ref.topk(5).indices.tolist()))}
    kb.KV_DTYPE = torch.float16
    try:
        import mlx.core as mx
        from mlx_lm import load
        from mlx_lm.utils import dequantize_model
        mx.set_default_device(mx.cpu)
        mm, _ = load(kb.MODEL_ID)
        mm = dequantize_model(mm)
        mm.set_dtype(mx.float32)
        short = ids[:32]
        ml = torch.tensor(mm(mx.array([short]))[0, -1].tolist())
        with torch.inference_mode():
            tl = model(torch.tensor([short])).logits[0, -1].float()
        out["mlx_vs_torch_32tok"] = {"max_abs_dlogit": round(float((ml - tl).abs().max()), 5),
                                     "argmax_equal": bool(ml.argmax() == tl.argmax())}
    except Exception as e:  # MLX parity is informative, not a gate
        out["mlx_vs_torch_32tok"] = f"skipped: {type(e).__name__}: {e}"
    print(json.dumps(out))
    ok = out["fp32_kv"]["argmax_equal"] and out["fp32_kv"]["max_abs_dlogit"] < 1e-2
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
