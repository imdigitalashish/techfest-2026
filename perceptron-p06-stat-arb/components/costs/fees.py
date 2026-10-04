"""C5 costs — taker fees by venue and tier.

STATUS: the `retail`/`vip` numbers below are PLACEHOLDER ASSUMPTIONS until research/notes/fees.md
(verified against official fee pages) lands. Every headline result is reported for all tiers,
including `mm` = 0 bps (the zero-fee upper bound), so no conclusion rests on an unverified fee.
"""
from __future__ import annotations

# taker fee in bps per leg: {venue: (retail, vip)} — PLACEHOLDERS, see module docstring
FEES_BPS: dict[str, tuple[float, float]] = {
    "binance": (10.0, 1.0),
    "binance-futures": (5.0, 1.7),
    "coinbase": (60.0, 5.0),
    "kraken": (40.0, 8.0),
    "okex": (10.0, 1.5),
    "okex-swap": (5.0, 1.5),
    "bybit": (5.5, 3.0),
    "bybit-spot": (10.0, 3.0),
    "bitstamp": (40.0, 3.0),
    "deribit": (5.0, 5.0),
    "hyperliquid": (4.5, 2.4),
    "gateio": (10.0, 2.0),
    "bitget": (10.0, 4.0),
}
FEES_VERIFIED = False
# Headline results use uniform per-leg fee levels ("f<bps>"), which need no venue-specific claim:
# f0 = zero-fee bound (top market makers), f1/f2 = plausible top-tier taker levels, f5 = mid tier.
TIERS = ("f0", "f1", "f2", "f5")


def taker_bps(venue: str, tier: str) -> float:
    if tier.startswith("f"):
        return float(tier[1:])
    if tier == "mm":
        return 0.0
    r, v = FEES_BPS[venue]
    return r if tier == "retail" else v


def leg_venue(leg: str) -> str:
    return leg.split(":", 1)[0]
