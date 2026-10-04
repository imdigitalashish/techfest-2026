# T3_alias_s2

`python eval/kvbench_torch.py --ctx 4096 --n 12 --needles 4 --seed 2 --fracs 0.1,0.25 --methods full,streaming,snapkv,kvp_expected,rod,rodlex --style alias --rod_layer 5 --rod_bits 4 --rod_scorer softmax_lift --rod_qsel content --lex_qsel content --kvp_fracs 0.1,0.25 --halo 0 --threads 8 --name T3_alias_s2`

torch-cpu · Intel(R) Xeon(R) Platinum 8370C CPU @ 2.80GHz · torch 2.10.0+cpu · wall 1115.1 s

| method | keep frac | n_q (ctx) | recall | 95% CI (ctx bootstrap) | stored MiB | answer-time MiB | compression | s/answer (CPU) | needle-block hit |
|---|---|---|---|---|---|---|---|---|---|
| full | 1.0 | 48 (12) | 0.104 | 0.04–0.17 | 128.307 | 128.307 | 1.0× | 1.252 |  |
| kvp_expected | 0.1 | 48 (12) | 0.000 | 0.00–0.00 | 12.815 | 12.815 | 10.01× | 0.837 |  |
| kvp_expected | 0.25 | 48 (12) | 0.021 | 0.00–0.06 | 32.062 | 32.062 | 4.0× | 0.793 |  |
| rod | 0.1 | 48 (12) | 0.208 | 0.12–0.29 | 7.044 | 11.044 | 18.22× | 1.419 | 0.2292 |
| rod | 0.25 | 48 (12) | 0.167 | 0.08–0.25 | 16.587 | 30.587 | 7.74× | 2.916 | 0.8372 |
| rodlex | 0.1 | 48 (12) | 0.146 | 0.08–0.21 | 6.406 | 12.406 | 20.03× | 1.414 | 0.7292 |
| rodlex | 0.25 | 48 (12) | 0.188 | 0.10–0.29 | 16.031 | 31.198 | 8.0× | 2.802 | 0.9767 |
| snapkv | 0.1 | 48 (12) | 0.000 | 0.00–0.00 | 12.831 | 12.831 | 10.0× | 0.719 |  |
| snapkv | 0.25 | 48 (12) | 0.000 | 0.00–0.00 | 32.081 | 32.081 | 4.0× | 0.69 |  |
| streaming | 0.1 | 48 (12) | 0.062 | 0.02–0.12 | 12.831 | 12.831 | 10.0× | 0.513 |  |
| streaming | 0.25 | 48 (12) | 0.146 | 0.06–0.23 | 32.081 | 32.081 | 4.0× | 0.559 |  |

| keep frac | A − B | Δ recall | 95% CI (paired ctx bootstrap) | contexts |
|---|---|---|---|---|
| 0.1 | rod − streaming | +0.146 | +0.04 … +0.25 | 12 |
| 0.1 | rod − snapkv | +0.208 | +0.12 … +0.29 | 12 |
| 0.1 | rod − rodlex | +0.062 | -0.02 … +0.15 | 12 |
| 0.1 | rod − kvp_expected | +0.208 | +0.12 … +0.29 | 12 |
| 0.1 | rodlex − streaming | +0.083 | -0.02 … +0.17 | 12 |
| 0.1 | snapkv − streaming | -0.062 | -0.12 … -0.02 | 12 |
| 0.25 | rod − streaming | +0.021 | -0.08 … +0.12 | 12 |
| 0.25 | rod − snapkv | +0.167 | +0.08 … +0.25 | 12 |
| 0.25 | rod − rodlex | -0.021 | -0.15 … +0.08 | 12 |
| 0.25 | rod − kvp_expected | +0.146 | +0.04 … +0.25 | 12 |
| 0.25 | rodlex − streaming | +0.042 | -0.06 … +0.15 | 12 |
| 0.25 | snapkv − streaming | -0.146 | -0.23 … -0.06 | 12 |
