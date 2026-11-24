The force: `feePercent`, `settlementDays` and `refundable` each `when` on `PaymentMethod` with an `else`, so a new method silently gets a zero fee and no refunds. `WALLET` already shows the drift: it reached two of the three.

The lightest fix is to drop the `else` branches and list every method: Kotlin then rejects a new method that one of the three forgets. No new types. Cost: each `when` names VOUCHER explicitly, a few more lines.

Ran `mvn -q test` before and after: CheckoutTest passes for all four methods.
