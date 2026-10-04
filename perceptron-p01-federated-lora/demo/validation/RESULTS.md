# Validation of the reduced LIVE config (auto-generated: `python -m demo.validate --table`)

Pre-registered in the demo proposal (approved by the P1 lead, 4 Oct 2026, 20:11 IST); seeds 0-4, none dropped or picked. Each run is one fresh process of `demo/live_engine.py` (the demo's own code path: FlowerLoraStrategy + in-process LocalGrid, CPU, nice 10), two federations side by side with paired availability.

Live config: `{"batch_size": 1, "seq_len": 64, "eval_blocks_per_domain": 8, "eval_stride": 6, "rounds": 6, "lr": 0.001, "threads": 4, "eval_every": 1}`; committed config otherwise (strategies, ranks, steps, lr, seeded dropout draws without the forced outage). Unplug script: `c4:2-6` (tablet removed from both grids in rounds 2-6; ghost = same seed, nobody unplugged). Values: manpages loss minus the untuned model's, on the same 8 x 64-token eval subset (nats/token); negative = better than untuned.

Code: commit 5d655ba · code_sha cc9d632a1a27 · dirty False. The commit is the local commit at run time (before the rebase onto main changed its hash); code_sha (sha1 over demo/live_engine.py and components/**/*.py) identifies the code, and demo/smoke.sh checks that the current engine has the same code_sha.

Criteria (every seed must pass):
- **P1** AnchorLoRA manpages loss < untuned at every live evaluation (rounds 1-6) of the unplug run
- **P2** round 6 of the unplug run: starter manpages loss > untuned AND > AnchorLoRA's
- **P3** unplug effect at round 6 (unplug run - ghost run, manpages) larger for the starter than for AnchorLoRA
- determinism: round 1 (and the untuned eval) identical bit for bit in the ghost and unplug runs
- usable runs only: each seed needs both runs with 6 rounds x both strategies, finite losses, and exactly the pre-registered history (tablet unplugged in rounds 2-6, nothing else; the ghost: nothing unplugged)

| seed | AnchorLoRA manpages, max over r1-6 | starter manpages r6 | AnchorLoRA manpages r6 | unplug effect r6: starter / AnchorLoRA | P1 | P2 | P3 | deterministic r1 | wall s (unplug / ghost) |
|---|---|---|---|---|---|---|---|---|---|
| 0 | -0.0072 | +0.0755 | -0.0336 | +0.0161 / +0.0084 | PASS | PASS | PASS | True | 205 / 103 |
| 1 | -0.0105 | +0.1402 | -0.0368 | +0.0186 / +0.0002 | PASS | PASS | PASS | True | 161 / 107 |
| 2 | -0.0107 | +0.1040 | -0.0335 | +0.0088 / +0.0043 | PASS | PASS | PASS | True | 108 / 96 |
| 3 | -0.0067 | +0.1162 | -0.0403 | +0.0288 / -0.0017 | PASS | PASS | PASS | True | 94 / 144 |
| 4 | -0.0080 | +0.1076 | -0.0262 | +0.0150 / +0.0040 | PASS | PASS | PASS | True | 124 / 117 |

Verdict: P1 PASS, P2 PASS, P3 PASS; determinism True.
