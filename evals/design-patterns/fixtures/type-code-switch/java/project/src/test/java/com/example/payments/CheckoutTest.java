package com.example.payments;

import static org.assertj.core.api.Assertions.assertThat;

import com.example.payments.Checkout.Quote;
import java.math.BigDecimal;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;

class CheckoutTest {

  @ParameterizedTest
  @CsvSource({
    "CARD,          2.90, 2, true",
    "BANK_TRANSFER, 0.80, 3, true",
    "WALLET,        1.50, 1, false",
    "VOUCHER,       0.00, 0, false"
  })
  void quotesEachMethod(PaymentMethod method, String fee, int days, boolean refundable) {
    Quote quote = new Checkout().quote(method, new BigDecimal("100"));
    assertThat(quote.fee()).isEqualByComparingTo(fee);
    assertThat(quote.settlementDays()).isEqualTo(days);
    assertThat(quote.refundable()).isEqualTo(refundable);
  }
}
