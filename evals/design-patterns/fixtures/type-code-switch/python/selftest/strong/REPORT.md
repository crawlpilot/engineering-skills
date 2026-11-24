The force: `fee_percent`, `settlement_days` and `refundable` each branch on `PaymentMethod` and fall through to a default, so a new method silently gets a zero fee and no refunds. `WALLET` already shows the drift: it reached two of the three functions.

I used a lookup table, the simplest option: one `RULES` entry per method, with an import-time check that every method has one. The three functions now read from it, so callers are unchanged. Cost: one more dataclass and a module-level check.

Ran pytest before and after: 4 passed both times.
