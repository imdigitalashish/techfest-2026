# Pre-trade risk controls — primary text

## SEC Rule 15c3-5 (17 CFR 240.15c3-5), "Risk management controls for brokers or dealers with market access"
- Source: https://www.law.cornell.edu/cfr/text/17/240.15c3-5 (Cornell LII rendering of the CFR), accessed 2026-10-04 by the lead (curl + HTML strip).
- Verbatim, paragraph (c)(1)–(c)(2) as extracted:

> (1) Financial risk management controls and supervisory procedures. The risk management controls and supervisory procedures shall be reasonably designed to systematically limit the financial exposure of the broker or dealer that could arise as a result of market access, including being reasonably designed to: (i) Prevent the entry of orders that exceed appropriate pre-set credit or capital thresholds in the aggregate for each customer and the broker or dealer and, where appropriate, more finely-tuned by sector, security, or otherwise by rejecting orders if such orders would exceed the applicable credit or capital thresholds; and (ii) Prevent the entry of erroneous orders, by rejecting orders that exceed appropriate price or size parameters, on an order-by-order basis or over a short period of time, or that indicate duplicative orders. (2) Regulatory risk management controls and supervisory procedures. The risk management controls and supervisory procedures shall be reasonably designed to ensure compliance with all regulatory requirements, including being reasonably designed to: (i) Prevent the entry of orders unless there has been compliance with all regulatory requirements that must be satisfied on a pre-order entry basis; (ii) Prevent the entry of orders for securities for a broker or dealer, customer , or other person if such person is restricted from trading those securities; (iii) Restrict access to trading systems and technology that provide market access to persons and accounts pre-approved and authorized by the broker or dealer; and (iv) Assure that appropriate surveillance personnel receive immediate post-trade execution reports that result from market access. (d) The financial and regulatory risk management controls and supervisory procedures described in paragraph (c) of this section shall be under the direct and exclusive control of the broker or dealer that is subject to paragraph (b) of this section. (1) Notwithstanding

## Mapping used in our design (lead's analysis, not a quote)
| 15c3-5 control | Agent-action analogue in our checker |
|---|---|
| (c)(1)(i) credit/capital thresholds per customer | account max order value and available cash (P-3.4), transfer limits (P-5.2) |
| (c)(1)(ii) price or size parameters (erroneous orders) | price collar vs KB reference price (P-3.1), max order size (P-3.2), market-order size (P-3.5) |
| (c)(1)(ii) duplicative orders | idempotency check against the session record (P-4.1) |
| (c)(2)(ii) persons restricted from trading those securities | restricted list (P-2.2) |
| (c)(2)(iii) access only for pre-approved, authorized persons/accounts | principal must own the account (P-1.1, P-5.1) |
| "prevent the entry" (checks run before the order reaches the market) | the guard runs before the tool executes |

Not yet opened (UNVERIFIED, next step): MiFID II RTS 6 (Delegated Regulation (EU) 2017/589) Art. 15 pre-trade controls and Art. 12 kill functionality; SEC order in the Knight Capital matter (2013); SEBI 2025 retail algo framework.
