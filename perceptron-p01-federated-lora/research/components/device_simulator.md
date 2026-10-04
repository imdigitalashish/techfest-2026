# C2 Device simulator — component research

**Contract:** `DeviceProfile[]`, rounds, seed, scenario → `allowed_steps[(round, device)]`. **Isolated metric:** |realised − target| offline and cut-off rates over 1,000 simulated rounds.

- **Today:** 5 profiles (workstation r16/16 steps, laptop r8/8, phone r4/4, Raspberry-Pi r2/2, tablet r4/4 with a forced 5-round outage); Bernoulli offline (0–20 %), Bernoulli deadline cut-off (0–30 %) leaving 25–75 % of the planned steps. Schedule depends only on the seed → strategies are compared on identical dropouts (paired design). Budgets are *assumptions*, not device measurements.
- **SOTA:** FedScale (ICML 2022, 2105.11367) provides system-performance benchmarking with device behaviour; real availability is diurnal and correlated (to verify against FedScale traces).
- **Candidates:** Markov on/off availability; trace replay from FedScale; correlated outages (all phones offline at night); bandwidth-limited upload deadlines derived from payload bytes.
