# smoke_torch

`python eval/kvbench_torch.py --ctx 1024 --n 1 --needles 2 --seed 0 --fracs 0.25 --methods full,int8,int4,int2,streaming,random,h2o,snapkv,knorm,snapkv_qa,rod,rodlex --style literal --rod_layer 8 --rod_bits 2 --halo 0 --threads 4 --name smoke_torch`

torch-cpu · Intel(R) Xeon(R) Platinum 8370C CPU @ 2.80GHz · torch 2.10.0+cpu · wall 30.2 s

| method | keep frac | n_q (ctx) | recall | 95% CI (ctx bootstrap) | stored MiB | answer-time MiB | compression | s/answer (CPU) | needle-block hit |
|---|---|---|---|---|---|---|---|---|---|
| full | 1.0 | 2 (1) | 1.000 | 1.00–1.00 | 35.906 | 35.906 | 1.0× | 0.7 |  |
| h2o | 0.25 | 2 (1) | 0.000 | 0.00–0.00 | 8.969 | 8.969 | 4.0× | 0.417 |  |
| int2 | 1.0 | 2 (1) | 0.000 | 0.00–0.00 | 5.61 | 5.61 | 6.4× | 1.739 |  |
| int4 | 1.0 | 2 (1) | 1.000 | 1.00–1.00 | 10.099 | 10.099 | 3.56× | 0.769 |  |
| int8 | 1.0 | 2 (1) | 1.000 | 1.00–1.00 | 19.075 | 19.075 | 1.88× | 0.752 |  |
| knorm | 0.25 | 2 (1) | 0.000 | 0.00–0.00 | 8.969 | 8.969 | 4.0× | 0.878 |  |
| random | 0.25 | 2 (1) | 0.000 | 0.00–0.00 | 8.969 | 8.969 | 4.0× | 0.934 |  |
| rod | 0.25 | 2 (1) | 0.000 | 0.00–0.00 | 4.533 | 8.533 | 7.92× | 1.954 | 0.0 |
| rodlex | 0.25 | 2 (1) | 1.000 | 1.00–1.00 | 4.473 | 8.473 | 8.03× | 1.433 | 1.0 |
| snapkv | 0.25 | 2 (1) | 0.000 | 0.00–0.00 | 8.969 | 8.969 | 4.0× | 0.664 |  |
| snapkv_qa (oracle) | 0.25 | 2 (1) | 1.000 | 1.00–1.00 | 8.969 | 8.969 | 4.0× | 0.982 |  |
| streaming | 0.25 | 2 (1) | 0.500 | 0.50–0.50 | 8.969 | 8.969 | 4.0× | 0.609 |  |

| keep frac | A − B | Δ recall | 95% CI (paired ctx bootstrap) | contexts |
|---|---|---|---|---|
| 0.25 | rod − streaming | -0.500 | -0.50 … -0.50 | 1 |
| 0.25 | rod − snapkv | +0.000 | +0.00 … +0.00 | 1 |
| 0.25 | rod − h2o | +0.000 | +0.00 … +0.00 | 1 |
| 0.25 | rod − rodlex | -1.000 | -1.00 … -1.00 | 1 |
| 0.25 | snapkv − streaming | -0.500 | -0.50 … -0.50 | 1 |
| 0.25 | h2o − streaming | -0.500 | -0.50 … -0.50 | 1 |
