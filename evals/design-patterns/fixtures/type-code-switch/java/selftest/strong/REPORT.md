The force: `feePercent`, `settlementDays` and `refundable` in `PaymentRules` each switch on `PaymentMethod` with a `default`, so a new method silently gets a zero fee and no refunds. `WALLET` already shows the drift: it was added to two of the three switches.

I considered a lookup table first. Putting the three rules on the enum constants is about as small and makes the compiler reject a new method that doesn't state all three. `PaymentRules` now delegates, so callers are unchanged. Cost: the enum now carries data and a constructor.

Ran `mvn -q test` before and after: CheckoutTest passes for all four methods.
