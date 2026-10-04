# Spike research: C2 twin_runner (synchronised counterfactual twins) and C4 impact_model (ghost book)

> v1, 4 Oct 2026 10:00 IST. Evidence comes from committed runs in `eval/results/`; literature from [`../landscape.md`](../landscape.md) (sources opened 4 Oct 2026).

## C2: why naive twins fail, and what synchronisation does
- **Setup.** For each seed: world A (our agent sells 4,000 shares, 09:35–09:55) and world B (null agent, quantity 0). Both arms append exactly one agent, so the latency model is identical. Every background agent has its own seeded `RandomState` drawn in fixed order from the master seed (`rmsc04.py`).
- **Naive twins** are bit-identical before our first order: 80/80 runs (E1), 300/300 (E3). Afterwards, any state-dependent branch in a background agent consumes a *different number* of random draws, which shifts its whole future random stream. That decorrelates the twins chaotically. E1: std of the twin mid gap was 4.7¢ at +60 s, 33¢ at +20 min and 64¢ at +30 min, against a 3–5¢ mean impact.
- **Synchronisation (`per_wakeup`).** Each background agent's decision RNG is re-keyed at every wake-up from (seed, agent id, wake-up count). Wake-time draws come from a dedicated timing stream (`components/sim_env/sim_env/world.py::_synchronise_rng`). Extra or missing draws in one cycle can no longer shift later cycles, so the twins differ only through *causal* responses to our orders. Marginal distributions are unchanged: each draw is still from the same distribution with a fresh, independent key.
- **Evidence (E4, TWAP, val seeds 100–129):**
  - NSR at the end of execution fell 4.7 → 1.4.
  - The own-impact term's per-seed std fell 0.971 → 0.164 bps.
  - Instant cost (0.130 vs 0.129 bps) and window volume (34.4k vs 33.9k shares) were unchanged.
- **Evidence on test seeds:** paired-ΔIS CI half-width fell ≈ 0.39 → 0.05 bps, 7.5× tighter (E3 vs E5, the same 60 seeds). A pre-registered effect was confirmed on 200 fresh seeds (E6).
- **Independent check:** a code-review sub-agent verified the wrappers bind per agent, found no seed collisions across seeds 1000–1259, and confirmed the global RNG isn't consumed during the window except by megashocks (expected count about 6e-6 per session). See `eval/results/code-review-2026-10-04.md`.
- **Open issues and next ideas:**
  1. At +60 s the synced std is *higher* than naive (4.77 vs 2.83¢); unexplained so far.
  2. The decision RNG could also be keyed per *message* (not just per wake-up) for agents that draw in `receive_message`.
  3. Control variates: regress ΔIS on the twin's drift.
  4. Antithetic seeds.
  5. Check that synchronisation preserves stylised facts (realism scorecard, `eval/realism.py`).
- **Prior art:** common random numbers are standard variance reduction in stochastic simulation. Balch et al. (arXiv:1906.12010) frame replay vs interactive evaluation. I found no paper that quantifies twin decorrelation in LOB agent-based models or fixes it by re-keying (arXiv searches on 4 Oct only; absence **UNVERIFIED** beyond that).

## C4: the ghost book (deployable own-impact estimator)
- **Target.** Ĩ(t) ≈ twin mid − treatment mid, computed from observables only (our fills and the book), so a live desk could run it. The ghost mid = observed mid + Ĩ(t) (for a SELL).
- **v0 model:** exponential propagator I(t) = Σ qᵢ·(g_perm + g_tr·e^{−(t−tᵢ)/τ}), fitted to twin paths weighted by 1/var. Naive-twin fit (E1, train seeds): τ = 60 s, g_tr = 0.0059¢/sh, g_perm = 0.0022¢/sh. Out-of-sample R² < 0, i.e. not identifiable through naive-twin noise.
- **Next measurement:** refit on synced train-seed twins (E9) and report the out-of-sample R²/RMSE on held-out train seeds. That is the C4 isolated metric.
- **Candidates:** a nonparametric kernel (a binned G(τ)); a state-dependent kernel (scaled by touch depth or spread); a small sequence model mapping (own fills, book features) to the twin gap; Hawkes-type cross-excitation with momentum flow (cf. Muhle-Karbe, Ouazzani Chahdi, Rosenbaum, arXiv:2601.23172).
- **Why it matters for the pitch:** the twins are the lab instrument; the ghost book is what transfers to a live venue. Certify it by its RMSE against exact counterfactuals.
