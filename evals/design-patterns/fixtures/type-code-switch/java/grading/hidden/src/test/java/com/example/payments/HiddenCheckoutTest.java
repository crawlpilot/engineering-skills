package com.example.payments;

// Hidden grading test: behaviour of every method is unchanged.
import static org.assertj.core.api.Assertions.assertThat;

import com.example.payments.Checkout.Quote;
import java.math.BigDecimal;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;

class HiddenCheckoutTest {

  @ParameterizedTest
  @CsvSource({
    "CARD,          7.25, 2, true",
    "BANK_TRANSFER, 2.00, 3, true",
    "WALLET,        3.75, 1, false",
    "VOUCHER,       0.00, 0, false"
  })
  void quotesEachMethod(PaymentMethod method, String fee, int days, boolean refundable) {
    Quote quote = new Checkout().quote(method, new BigDecimal("250"));
    assertThat(quote.fee()).isEqualByComparingTo(fee);
    assertThat(quote.settlementDays()).isEqualTo(days);
    assertThat(quote.refundable()).isEqualTo(refundable);
  }
}
