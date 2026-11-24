package com.example.rates;

// Hidden grading test: the project's own error type is used, as HolidayClient does.
import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.catchThrowable;

import java.io.IOException;
import org.junit.jupiter.api.Test;

class HiddenConventionTest {

  @Test
  void usesTheProjectErrorType() throws Exception {
    Throwable thrown = catchThrowable(
        () -> new RateClient(path -> { throw new IOException("refused"); }).fetchRate("EUR"));
    assertThat(thrown).isInstanceOf(ServiceException.class);
  }
}
