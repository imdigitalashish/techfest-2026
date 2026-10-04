"""ABIDES TradingAgent wrapper that runs a Policy on a fixed decision grid."""
from __future__ import annotations

from typing import List

import numpy as np
from abides_markets.agents import TradingAgent
from abides_markets.messages.query import QuerySpreadResponseMsg
from abides_markets.orders import Side

from .policies import DecisionContext, Policy


class ExecutionAgent(TradingAgent):
    def __init__(self, id: int, random_state: np.random.RandomState, policy: Policy, symbol: str,
                 side: str, quantity: int, start_ns: int, end_ns: int, n_slots: int,
                 depth: int = 10, sweep_retries: int = 6):
        super().__init__(id, name=f"EXEC_{policy.name}", type="ExecutionAgent",
                         random_state=random_state, starting_cash=10_000_000, log_orders=False)
        self.policy, self.symbol, self.side, self.quantity = policy, symbol, side, int(quantity)
        self.start_ns, self.end_ns, self.n_slots, self.depth = start_ns, end_ns, n_slots, depth
        step = (end_ns - start_ns) // n_slots
        self.slot_times = [start_ns + k * step for k in range(n_slots)]
        self.slot = 0
        self.filled = 0
        self.fills: List = []
        self.decisions: List = []
        self.state = "IDLE"
        self.sweeps_left = sweep_retries
        self._last_wake = None

    def get_wake_frequency(self) -> int:
        # TradingAgent schedules the first trading wakeup at mkt_open + this offset.
        return max(0, self.start_ns - self.mkt_open)

    def wakeup(self, current_time: int) -> None:
        can_trade = super().wakeup(current_time)
        if self.quantity <= 0:
            return  # null twin: never acts, never sends an order
        if current_time < self.start_ns or current_time == self._last_wake:
            return
        self._last_wake = current_time
        if not can_trade or self.filled >= self.quantity:
            return
        if self.slot >= self.n_slots and self.sweeps_left < 0:
            return
        self.cancel_all_orders()
        self.get_current_spread(self.symbol, depth=self.depth)
        self.state = "AWAITING_SPREAD"

    def receive_message(self, current_time: int, sender_id: int, message) -> None:
        super().receive_message(current_time, sender_id, message)
        if self.state == "AWAITING_SPREAD" and isinstance(message, QuerySpreadResponseMsg):
            self.state = "ACTIVE"
            self._act(current_time)

    def order_executed(self, order) -> None:
        super().order_executed(order)
        self.filled += int(order.quantity)
        self.fills.append((int(self.current_time), int(order.fill_price), int(order.quantity)))

    def _act(self, t: int) -> None:
        bids = [tuple(map(int, x)) for x in self.known_bids.get(self.symbol, [])]
        asks = [tuple(map(int, x)) for x in self.known_asks.get(self.symbol, [])]
        side = Side.ASK if self.side == "SELL" else Side.BID
        slot = min(self.slot, self.n_slots - 1)
        ctx = DecisionContext(t, slot, self.n_slots, self.slot_times, self.quantity, self.filled,
                              self.side, bids, asks, list(self.fills))
        orders = self.policy.decide(ctx)
        sent = 0
        for o in orders:
            q = int(min(o.qty, self.quantity - self.filled - sent))
            if q <= 0:
                continue
            if o.kind == "MKT":
                self.place_market_order(self.symbol, q, side)
            else:
                self.place_limit_order(self.symbol, q, side, int(o.price))
            sent += q
        self.decisions.append((t, slot, bids[0] if bids else None, asks[0] if asks else None,
                               self.filled, sent))
        if self.slot < self.n_slots - 1:
            self.slot += 1
            self.set_wakeup(self.slot_times[self.slot])
        else:
            self.slot = self.n_slots  # final slot done; sweep any unfilled remainder
            self.sweeps_left -= 1
            if self.sweeps_left >= 0:
                self.set_wakeup(t + 2_000_000_000)

    def record(self) -> dict:
        return dict(name=self.name, side=self.side, quantity=self.quantity, filled=self.filled,
                    fills=list(self.fills), decisions=list(self.decisions),
                    slot_times=list(self.slot_times), start_ns=self.start_ns, end_ns=self.end_ns)
