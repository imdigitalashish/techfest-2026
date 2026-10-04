# C10 Flower adapter — component research

**Contract:** wraps C6/C7 so each device runs as a Flower `ClientApp` process and the aggregator as a custom strategy in a `ServerApp`. **Isolated metric:** parity — same seed ⇒ same metrics as the in-process simulator; overhead per round.

- **Status:** not started. `flwr` 1.39.0 is on PyPI (seen 2026-10-04) but its dependency `grpcio` could not be downloaded overnight (network at ~0 B/s for PyPI); the cached uv wheels lacked it. Flower API details for 1.39 (Message API, strategy interface) are UNVERIFIED until the docs load.
- **Plan:** Deployment Engine (SuperLink + one SuperNode per device as separate processes) so the finals demo can kill a device process mid-round and show the anchor's memory/partial-work keeping the loss curve flat.
