"""API cost of the frontier-model baselines on the 300-call test sample.

  python -m eval.taubench.cost          -> eval/results/taubench/cost__test__sample300.json

Price: Azure Retail Prices API (https://prices.azure.com/api/retail/prices), "gpt 4.1 mini Inp glbl Tokens" $0.0004/1K and
"gpt 4.1 mini Outp glbl Tokens" $0.0016/1K, armRegionName swedencentral (the deployment's region, GlobalStandard SKU),
effectiveStartDate 2025-04-01, retrieved 2026-10-04.
cascade_aoai: prompt/completion tokens as reported by the API for every call (measured).
llm_judge_aoai: the resumed run logged usage for only 3 calls, so prompt tokens are counted exactly offline with the model's
tokenizer (tiktoken o200k_base, + chat-format overhead). The method is validated against the cascade's measured usage.
Completion tokens use the 3 measured judge calls' mean.
"""
from __future__ import annotations

import json
from pathlib import Path

import tiktoken

from eval.taubench.run import JUDGE_SYS, sample, transcript
from eval.taubench.replay import TB, load_items
from components.checker import taubench_cascade as tc

ROOT = Path(__file__).resolve().parents[2]
RES = ROOT / "eval" / "results" / "taubench"
PRICE_IN, PRICE_OUT = 0.0004 / 1000, 0.0016 / 1000  # USD per token
ENC = tiktoken.get_encoding("o200k_base")
OVERHEAD = 3 + 2 * 4  # reply priming + per-message framing for system + user (OpenAI chat format)


def ntok(system: str, user: str) -> int:
    return len(ENC.encode(system)) + len(ENC.encode(user)) + OVERHEAD


def main():
    items = sample(load_items("test"), 300)
    policy = (TB / "tau_bench" / "envs" / "retail" / "wiki.md").read_text()
    judge_prompt = [ntok(JUDGE_SYS, f"STORE POLICY:\n{policy}\n\nCONVERSATION SO FAR:\n{transcript(it)}\n\nPROPOSED CALL: "
                                    f"{it['tool']}({json.dumps(it['args'])})") for it in items]
    cas = json.loads((RES / "cascade_aoai__test__sample300.json").read_text())
    jdg = json.loads((RES / "llm_judge_aoai__test__sample300.json").read_text())
    # validate the offline count on the cascade: recount its resolver prompts for the calls it actually made
    by_id = {it["item_id"]: it for it in items}
    est = 0
    for r in cas["rows"]:
        calls = [x for x in r["reasons"] if x.startswith("model_calls=")]
        n = int(calls[0].split("=")[1]) if calls else 0
        if n:
            it = by_id[r["item_id"]]
            per = ntok(tc.RESOLVE_SYS, f"CONVERSATION:\n{transcript(it)}\n\nPROPOSED CALL: {it['tool']}({json.dumps(it['args'])})\n\n"
                                       f"CONCERN: x. Is this value supported by what the user said or by the tool data?")
            est += n * per
    cu = cas["api_usage"]
    j_comp = jdg["api_usage"]["completion_tokens"] / max(1, jdg["api_usage"]["calls"])
    jt_in = sum(judge_prompt)
    out = {
        "price_usd_per_1k": {"input": 0.0004, "output": 0.0016, "source": "Azure Retail Prices API, swedencentral, gpt 4.1 mini Inp/Outp glbl Tokens, effective 2025-04-01, retrieved 2026-10-04"},
        "n_guarded_calls": len(items),
        "cascade_aoai": {"model_calls": cu["calls"], "prompt_tokens": cu["prompt_tokens"], "completion_tokens": cu["completion_tokens"],
                         "usd_total": round(cu["prompt_tokens"] * PRICE_IN + cu["completion_tokens"] * PRICE_OUT, 4),
                         "offline_prompt_token_estimate": est,
                         "offline_estimate_error": round(est / cu["prompt_tokens"] - 1, 4)},
        "llm_judge_aoai": {"model_calls": len(items), "prompt_tokens_counted": jt_in, "completion_tokens_est": round(j_comp * len(items)),
                           "usd_total": round(jt_in * PRICE_IN + j_comp * len(items) * PRICE_OUT, 4)},
    }
    for k in ("cascade_aoai", "llm_judge_aoai"):
        out[k]["usd_per_guarded_call"] = round(out[k]["usd_total"] / len(items), 6)
    (RES / "cost__test__sample300.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
