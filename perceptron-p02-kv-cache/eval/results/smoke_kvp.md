# smoke_kvp

`python eval/kvbench_torch.py --ctx 1024 --n 1 --needles 4 --seed 999 --fracs 0.1,0.25 --methods full,streaming,snapkv,h2o,knorm,rod,rodlex,kvp_streaming,kvp_snapkv,kvp_observed,kvp_knorm,kvp_expected,kvp_tova --style literal --rod_layer 5 --rod_bits 4 --rod_scorer softmax_lift --rod_qsel content --lex_qsel content --kvp_fracs 0.1 --halo 0 --threads 8 --name smoke_kvp`

torch-cpu · Intel(R) Xeon(R) Platinum 8370C CPU @ 2.80GHz · torch 2.10.0+cpu · wall 60.3 s

| method | keep frac | n_q (ctx) | recall | 95% CI (ctx bootstrap) | stored MiB | answer-time MiB | compression | s/answer (CPU) | needle-block hit |
|---|---|---|---|---|---|---|---|---|---|
| full | 1.0 | 4 (1) | 1.000 | 1.00–1.00 | 38.062 | 38.062 | 1.0× | 0.502 |  |
| h2o | 0.1 | 4 (1) | 0.000 | 0.00–0.00 | 3.812 | 3.812 | 9.98× | 0.317 |  |
| h2o | 0.25 | 4 (1) | 0.000 | 0.00–0.00 | 9.5 | 9.5 | 4.01× | 0.325 |  |
| knorm | 0.1 | 4 (1) | 0.000 | 0.00–0.00 | 3.812 | 3.812 | 9.98× | 0.446 |  |
| knorm | 0.25 | 4 (1) | 0.000 | 0.00–0.00 | 9.5 | 9.5 | 4.01× | 0.468 |  |
| kvp_expected | 0.1 | 4 (1) | 0.000 | 0.00–0.00 | 3.781 | 3.781 | 10.07× | 0.317 |  |
| kvp_knorm | 0.1 | 4 (1) | 0.000 | 0.00–0.00 | 3.781 | 3.781 | 10.07× | 0.894 |  |
| kvp_observed | 0.1 | 4 (1) | 0.000 | 0.00–0.00 | 3.781 | 3.781 | 10.07× | 0.32 |  |
| kvp_snapkv | 0.1 | 4 (1) | 0.000 | 0.00–0.00 | 3.781 | 3.781 | 10.07× | 0.397 |  |
| kvp_streaming | 0.1 | 4 (1) | 0.000 | 0.00–0.00 | 3.781 | 3.781 | 10.07× | 0.412 |  |
| kvp_tova | 0.1 | 4 (1) | 0.000 | 0.00–0.00 | 3.781 | 3.781 | 10.07× | 0.382 |  |
| rod | 0.1 | 4 (1) | 0.000 | 0.00–0.00 | 2.169 | 2.169 | 17.55× | 0.41 | 0.0 |
| rod | 0.25 | 4 (1) | 1.000 | 1.00–1.00 | 4.988 | 8.988 | 7.63× | 1.305 | 1.0 |
| rodlex | 0.1 | 4 (1) | 0.000 | 0.00–0.00 | 1.88 | 1.88 | 20.25× | 0.409 | 0.0 |
| rodlex | 0.25 | 4 (1) | 0.500 | 0.50–0.50 | 4.723 | 8.723 | 8.06× | 1.055 | 0.75 |
| snapkv | 0.1 | 4 (1) | 0.000 | 0.00–0.00 | 3.812 | 3.812 | 9.98× | 0.403 |  |
| snapkv | 0.25 | 4 (1) | 0.000 | 0.00–0.00 | 9.5 | 9.5 | 4.01× | 0.331 |  |
| streaming | 0.1 | 4 (1) | 0.000 | 0.00–0.00 | 3.812 | 3.812 | 9.98× | 0.41 |  |
| streaming | 0.25 | 4 (1) | 0.250 | 0.25–0.25 | 9.5 | 9.5 | 4.01× | 0.447 |  |

| keep frac | A − B | Δ recall | 95% CI (paired ctx bootstrap) | contexts |
|---|---|---|---|---|
| 0.1 | rod − streaming | +0.000 | +0.00 … +0.00 | 1 |
| 0.1 | rod − snapkv | +0.000 | +0.00 … +0.00 | 1 |
| 0.1 | rod − h2o | +0.000 | +0.00 … +0.00 | 1 |
| 0.1 | rod − knorm | +0.000 | +0.00 … +0.00 | 1 |
| 0.1 | rod − rodlex | +0.000 | +0.00 … +0.00 | 1 |
| 0.1 | rod − kvp_streaming | +0.000 | +0.00 … +0.00 | 1 |
| 0.1 | rod − kvp_snapkv | +0.000 | +0.00 … +0.00 | 1 |
| 0.1 | rod − kvp_observed | +0.000 | +0.00 … +0.00 | 1 |
| 0.1 | rod − kvp_knorm | +0.000 | +0.00 … +0.00 | 1 |
| 0.1 | rod − kvp_expected | +0.000 | +0.00 … +0.00 | 1 |
| 0.1 | rodlex − streaming | +0.000 | +0.00 … +0.00 | 1 |
| 0.1 | snapkv − streaming | +0.000 | +0.00 … +0.00 | 1 |
| 0.1 | h2o − streaming | +0.000 | +0.00 … +0.00 | 1 |
| 0.25 | rod − streaming | +0.750 | +0.75 … +0.75 | 1 |
| 0.25 | rod − snapkv | +1.000 | +1.00 … +1.00 | 1 |
| 0.25 | rod − h2o | +1.000 | +1.00 … +1.00 | 1 |
| 0.25 | rod − knorm | +1.000 | +1.00 … +1.00 | 1 |
| 0.25 | rod − rodlex | +0.500 | +0.50 … +0.50 | 1 |
| 0.25 | rodlex − streaming | +0.250 | +0.25 … +0.25 | 1 |
| 0.25 | snapkv − streaming | -0.250 | -0.25 … -0.25 | 1 |
| 0.25 | h2o − streaming | -0.250 | -0.25 … -0.25 | 1 |
