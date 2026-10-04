# Frameworks and benchmarks: primary-source notes

**Access date for all linked sources: 2026-10-04.** This note records what first-party sources establish; time-sensitive leaderboard scores are a snapshot from that date. “UNVERIFIED” marks claims not confirmed by the reviewed primary sources.

## FlowerTune LLM Leaderboard

FlowerTune LLM has four tracks—General NLP, Finance, Medical, and Code—built around federated instruction tuning. The public evaluation instructions say to use their exact evaluation code and command for submissions; track scores are ranked by the average over each track’s evaluation datasets. Finance uses accuracy on Financial PhraseBank (FPB), FIQA, and Twitter Financial News Sentiment (TFNS); its evaluator applies 4-bit quantization for leaderboard submissions. [S1][S2][S3]

### Finance baseline and fixed setup

The published finance template uses Mistral-7B-v0.3 and `flwrlabs/fingpt-sentiment-train`; its `flwr-version-target` is 1.39.0. The static training data is split IID into 50 client partitions, with 10% sampled per round (5 of 50), over 200 rounds. The README says static app configuration and the 50-SuperNode count must remain unchanged for eligible leaderboard submissions. [S4][S5]

Key baseline settings: 4-bit model quantization; LoRA rank `r=32`, alpha `64`, dropout `0.075`; sequence length 512; per-device batch 16; 3 epochs with max 10 steps/client; learning-rate range `5e-5` to `1e-6`; checkpoint every 5 rounds. The server strategy is FedAvg with a communication-cost tracker. The Finance app pins `peft==0.6.2` (not 0.21.0), so PEFT 0.21 options below should not be mistaken for the exact installed baseline version. [S4][S6][S7]

The Finance evaluator maps model responses to sentiment labels and computes `accuracy_score` for each of FPB, FIQA, and TFNS. FPB uses the `sentences_50agree` configuration; TFNS uses its validation split; FIQA sentiment scores are mapped into labels. [S3]

| Published baseline (Finance) | FPB | FIQA | TFNS | Mean accuracy |
|---|---:|---:|---:|---:|
| Default template | 44.55% | 62.50% | 28.77% | 45.27% |

Flower’s evaluation README calls the template results the leaderboard lower bound and confirms ranking by average. [S2]

### Finance leaderboard snapshot (live page, accessed 2026-10-04)

| Rank | Team | Base model | Comm. cost | Mean | FPB | FIQA | TFNS | Submitted |
|---:|---|---|---:|---:|---:|---:|---:|---|
| 1 | ZeroOne.AI | Qwen2.5-7B | 30.1 GB | 84.58 | 85.89 | 83.22 | 84.63 | 14.01.26 |
| 2 | FL-finetune-JB-DC | Qwen2.5-7B | 3.8 GB | 75.51 | 80.69 | 71.05 | 74.79 | 20.04.25 |
| 3 | FL-finetune-JB-DC | Qwen2.5-7B | 3.8 GB | 74.95 | 79.54 | 75.65 | 69.68 | 20.04.25 |
| 4 | Massimo R. Scamarcia | SmolLM2-1.7B-Instruct | 10.7 GB | 67.90 | 71.37 | 56.58 | 75.75 | 09.02.25 |
| 5 | Nut Chukamphaeng | Qwen2.5-7B | 1.0 GB | 65.52 | 68.23 | 60.85 | 67.50 | 16.12.24 |
| 11 | Baseline | Mistral-7B-v0.3 | 101.6 GB | 45.27 | 44.55 | 62.50 | 28.77 | 01.10.24 |

The page’s leaderboard table was rendered and inspected directly; scores and ranks can change, so re-check before using them as current results. Its FAQ states a 13B base-model parameter ceiling and a 200-GB communication limit. [S8][S9]

## Flower 1.39 API, strategy, simulation, and deployment

The finance app config explicitly targets Flower 1.39.0. Flower’s 1.39.x API documents `ServerApp` as the server-side entry point and `ClientApp` as client-side task handlers; the finance example makes the arrangement concrete: `@app.main()` starts a strategy on a `Grid`, while the client’s `@app.train()` receives a `Message`, loads its local partition, trains, and returns a reply message. [S4][S6][S7][S10][S11]

`Message` carries a `RecordDict` content payload and metadata including message type, destination node, group/round ID, TTL, and reply relationship. Built-in strategies pass model/config records to clients and aggregate returned model arrays and metrics. The `Strategy` abstraction controls client sampling, train/evaluate instructions, aggregation, and evaluation; Flower documents FedAvg and FedAdam, callback/method customization, and custom strategies. The Finance example subclasses FedAvg to track transferred bytes. [S12][S13][S7]

Simulation uses the same `ClientApp` logic as deployment. Flower’s SimulationRuntime schedules and manages client apps through a backend (Ray by default), allocates configurable CPU/memory/GPU resources, queues work into batches, and materializes clients ephemerally as needed. For local runs, `flwr run` submits through a managed local SuperLink to the SimulationRuntime. [S14][S15]

In deployment, a long-running SuperLink communicates and schedules work; SuperNodes connect to it; SuperExec processes launch/manage short-lived ServerApp and ClientApp processes. The deployment guide shows a SuperLink plus two SuperNodes, and Docker guidance documents subprocess/process isolation. [S16][S17]

## Partitioners, FedLLM-Bench, and Dolly-15k

Flower Datasets provides `IidPartitioner` and `DirichletPartitioner` among its partitioners. The Finance baseline uses IID—not Dirichlet—partitioning. `DirichletPartitioner` accepts `num_partitions`, a target-label column (`partition_by`), and a positive concentration `alpha`; `alpha` can be scalar or one value per partition. Optional controls include `min_partition_size` (default 10), `self_balancing` (default false), shuffling (default true), and seed (default 42). Flower’s implementation example uses 10 partitions, `alpha=0.5`, `min_partition_size=10`, and `self_balancing=True`. These are example settings, not mandated benchmark values. [S5][S18]

FedLLM-Bench is a separate realistic benchmark with client-siloed data: Fed-Aya, Fed-ChatbotIT, and Fed-WildChat for instruction tuning, plus Fed-ChatbotPA for preference alignment. Its paper reports:

| Dataset | Clients | Samples | Mean samples/client (± SD) |
|---|---:|---:|---:|
| Fed-Aya | 38 | 25,513 | 671 ± 815 |
| Fed-ChatbotIT | 237 | 6,166 | 26 ± 33 |
| Fed-WildChat | 100 | 52,703 | 527 ± 477 |
| Fed-ChatbotPA | 747 | 9,508 | 13 ± 21 |

These are naturally client-partitioned benchmark datasets, not values produced by a Flower Dirichlet split. The FedLLM-Bench repository points to the paper and data downloads; it does not describe the FlowerTune Finance training dataset. [S19][S20]

Databricks’ Dolly-15k card describes over 15,000 human-generated, English instruction-following records across eight categories and lists CC BY-SA 3.0. The card is a dataset description, not a federated partition specification. **UNVERIFIED:** no Dolly-15k Dirichlet alpha or client split value is prescribed by the reviewed card or FlowerTune sources. [S21]

## Device-availability traces

Flower’s simulation documentation names client availability as a scenario to simulate, but the reviewed Flower sources do not establish a packaged, first-party availability-trace dataset. **UNVERIFIED:** that is a finding about the reviewed sources, not proof no Flower-compatible traces exist elsewhere. As a primary-source alternative, FedScale documents two pickle-serialized traces: device computation/communication capacity, and device availability keyed by client ID with duration, active/inactive intervals, finish time, and model; it names `client_device_capacity` and `client_behave_trace`. The reviewed sources do not verify a direct FedScale-to-Flower trace adapter. [S14][S22]

## PEFT 0.21.0 LoRA options and Llama targets

PEFT 0.21.0’s `LoraConfig` supports `r`, `target_modules` (exact/suffix list matching or regex string), `exclude_modules`, `lora_alpha`, `lora_dropout`, `bias` (`none`, `all`, `lora_only`), `modules_to_save`, `use_rslora`, weight initialization choices, and layer/rank/alpha patterns. `target_modules="all-linear"` selects linear/Conv1D layers (excluding the output layer for a Transformers `PreTrainedModel`). The architecture defaults in PEFT 0.21.0 map Llama and Llama 4 to `q_proj` and `v_proj`; Mistral has the same default pair. [S23][S24]

## Sources (all accessed 2026-10-04)

- **[S1] FlowerTune LLM benchmark overview and four tracks:** [Flower repository README](https://github.com/flwrlabs/flower/blob/1435ea5e8d734070c7a7d30d73823900ad587e83/benchmarks/flowertune-llm/README.md).
- **[S2] Evaluation datasets, baseline table, ranking rule:** [evaluation README, lines 14–49](https://github.com/flwrlabs/flower/blob/1435ea5e8d734070c7a7d30d73823900ad587e83/benchmarks/flowertune-llm/evaluation/README.md#L14-L49).
- **[S3] Finance datasets, quantization, accuracy code:** [Finance evaluation README](https://github.com/flwrlabs/flower/blob/1435ea5e8d734070c7a7d30d73823900ad587e83/benchmarks/flowertune-llm/evaluation/finance/README.md#L1-L41); [evaluator code](https://github.com/flwrlabs/flower/blob/1435ea5e8d734070c7a7d30d73823900ad587e83/benchmarks/flowertune-llm/evaluation/finance/benchmarks.py#L14-L80) and [accuracy calculation](https://github.com/flwrlabs/flower/blob/1435ea5e8d734070c7a7d30d73823900ad587e83/benchmarks/flowertune-llm/evaluation/finance/benchmarks.py#L93-L138).
- **[S4] Flower 1.39 target and Finance training configuration:** [Finance `pyproject.toml`, lines 33–74](https://github.com/flwrlabs/flower/blob/1435ea5e8d734070c7a7d30d73823900ad587e83/examples/flowertune-llm-finance/pyproject.toml#L33-L74).
- **[S5] Finance client count, IID split, sampling, rounds, locked config:** [Finance README, lines 44–60](https://github.com/flwrlabs/flower/blob/1435ea5e8d734070c7a7d30d73823900ad587e83/examples/flowertune-llm-finance/README.md#L44-L60); [dataset partitioner code](https://github.com/flwrlabs/flower/blob/1435ea5e8d734070c7a7d30d73823900ad587e83/examples/flowertune-llm-finance/flowertune_finance/dataset.py#L63-L75).
- **[S6] Finance model quantization and LoRA config:** [Finance models.py, lines 23–55](https://github.com/flwrlabs/flower/blob/1435ea5e8d734070c7a7d30d73823900ad587e83/examples/flowertune-llm-finance/flowertune_finance/models.py#L23-L55).
- **[S7] ServerApp, ClientApp, FedAvg subclass:** [server_app.py, lines 16–52](https://github.com/flwrlabs/flower/blob/1435ea5e8d734070c7a7d30d73823900ad587e83/examples/flowertune-llm-finance/flowertune_finance/server_app.py#L16-L52); [client_app.py, lines 33–100](https://github.com/flwrlabs/flower/blob/1435ea5e8d734070c7a7d30d73823900ad587e83/examples/flowertune-llm-finance/flowertune_finance/client_app.py#L33-L100); [strategy.py, lines 13–80](https://github.com/flwrlabs/flower/blob/1435ea5e8d734070c7a7d30d73823900ad587e83/examples/flowertune-llm-finance/flowertune_finance/strategy.py#L13-L80).
- **[S8] Live Finance leaderboard table:** [FlowerTune Finance leaderboard](https://flower.ai/benchmarks/llm-leaderboard/finance).
- **[S9] Official leaderboard rules/FAQ:** [FlowerTune LLM Leaderboard](https://flower.ai/benchmarks/llm-leaderboard).
- **[S10] ServerApp API:** [Flower Framework ServerApp reference](https://flower.ai/docs/framework/ref-api/flwr.serverapp.ServerApp.html).
- **[S11] ClientApp API:** [Flower Framework ClientApp reference](https://flower.ai/docs/framework/ref-api/flwr.clientapp.ClientApp.html).
- **[S12] Message fields and semantics:** [Flower Framework Message reference](https://flower.ai/docs/framework/ref-api/flwr.app.Message.html).
- **[S13] Strategy API and customization:** [Use strategies](https://flower.ai/docs/framework/how-to-use-strategies.html); [Strategy abstraction](https://flower.ai/docs/framework/explanation-flower-strategy-abstraction.html); [strategy API index](https://flower.ai/docs/framework/ref-api/flwr.serverapp.strategy.html).
- **[S14] Simulation runtime behavior:** [Run simulations](https://flower.ai/docs/framework/how-to-run-simulations.html).
- **[S15] Local run via managed SuperLink:** [Run Flower locally](https://flower.ai/docs/framework/how-to-run-flower-locally.html).
- **[S16] Deployment components:** [Flower Architecture](https://flower.ai/docs/framework/explanation-flower-architecture.html); [Deployment Runtime guide](https://flower.ai/docs/framework/how-to-run-flower-with-deployment-engine.html).
- **[S17] Docker/process deployment:** [Docker quickstart](https://flower.ai/docs/framework/docker/tutorial-quickstart-docker.html); [App subprocess/isolation guide](https://flower.ai/docs/framework/docker/run-as-subprocess.html).
- **[S18] Partitioner API and implementation:** [Flower Datasets partitioner tutorial](https://flower.ai/docs/datasets/tutorial-use-partitioners.html); [DirichletPartitioner source, lines 28–109](https://github.com/flwrlabs/flower/blob/1435ea5e8d734070c7a7d30d73823900ad587e83/datasets/flwr_datasets/partitioner/dirichlet_partitioner.py#L28-L109); [alpha normalization, lines 145–174](https://github.com/flwrlabs/flower/blob/1435ea5e8d734070c7a7d30d73823900ad587e83/datasets/flwr_datasets/partitioner/dirichlet_partitioner.py#L145-L174).
- **[S19] FedLLM-Bench datasets and download:** [FedLLM-Bench repository README, lines 1–33](https://github.com/rui-ye/FedLLM-Bench/blob/24556797d74a89ff09f0db62d4e10f272ac769a5/README.md#L1-L33).
- **[S20] FedLLM-Bench client/sample table:** [arXiv paper HTML, Table 1](https://arxiv.org/html/2406.04845v1).
- **[S21] Dolly-15k dataset description and license:** [Databricks Hugging Face dataset card](https://huggingface.co/datasets/databricks/databricks-dolly-15k).
- **[S22] Availability and capacity trace format:** [FedScale device trace README](https://github.com/SymbioticLab/FedScale/blob/master/benchmark/dataset/data/device_info/README.md).
- **[S23] PEFT 0.21.0 LoRA reference:** [PEFT v0.21.0 LoRA docs](https://huggingface.co/docs/peft/v0.21.0/en/package_reference/lora); [PEFT v0.21.0 config source, lines 452–529](https://github.com/huggingface/peft/blob/v0.21.0/src/peft/tuners/lora/config.py#L452-L529).
- **[S24] Architecture-specific target defaults:** [PEFT v0.21.0 constants, lines 63–96](https://github.com/huggingface/peft/blob/v0.21.0/src/peft/utils/constants.py#L63-L96).
