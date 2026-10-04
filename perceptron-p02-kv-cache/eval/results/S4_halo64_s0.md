# S4_halo64_s0

`python eval/kvbench_torch.py --ctx 4096 --n 12 --needles 4 --seed 0 --fracs 0.1,0.25,0.5 --methods rod --style literal --rod_layer 5 --rod_bits 4 --rod_scorer softmax_lift --rod_qsel content --lex_qsel content --kvp_fracs 0.1,0.25 --halo 64 --threads 8 --name S4_halo64_s0`

torch-cpu · Intel(R) Xeon(R) Platinum 8370C CPU @ 2.80GHz · torch 2.10.0+cpu · wall 696.6 s

| method | keep frac | n_q (ctx) | recall | 95% CI (ctx bootstrap) | stored MiB | answer-time MiB | compression | s/answer (CPU) | needle-block hit |
|---|---|---|---|---|---|---|---|---|---|
| rod | 0.1 | 48 (12) | 0.854 | 0.73–0.96 | 7.072 | 11.072 | 18.22× | 1.32 | 0.875 |
| rod | 0.25 | 48 (12) | 0.500 | 0.35–0.65 | 16.651 | 30.817 | 7.74× | 3.014 | 1.0 |
| rod | 0.5 | 48 (12) | 0.542 | 0.40–0.67 | 32.611 | 62.654 | 3.95× | 5.703 | 1.0 |

| keep frac | A − B | Δ recall | 95% CI (paired ctx bootstrap) | contexts |
|---|---|---|---|---|
