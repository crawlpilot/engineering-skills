package com.example.rates;

// Hidden grading tests: copied in by the grader, never shown to the agent.
import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.catchThrowable;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import org.junit.jupiter.api.Test;

class HiddenErrorHandlingTest {

  static List<Throwable> chain(Throwable t) {
    List<Throwable> out = new ArrayList<>();
    while (t != null && !out.contains(t)) {
      out.add(t);
      t = t.getCause();
    }
    return out;
  }

  static String messages(Throwable t) {
    StringBuilder sb = new StringBuilder();
    for (Throwable c : chain(t)) {
      sb.append(c.getMessage()).append(' ');
    }
    return sb.toString();
  }

  @Test
  void successStillReturnsTheRate() throws Exception {
    assertThat(new RateClient(path -> "0.92\n").fetchRate("EUR")).isEqualByComparingTo("0.92");
  }

  @Test
  void networkFailureRaisesWithContextAndCause() throws Exception {
    IOException original = new IOException("connection refused");
    Throwable thrown = catchThrowable(() -> new RateClient(path -> { throw original; }).fetchRate("EUR"));
    assertThat(thrown).isNotNull();
    assertThat(messages(thrown)).contains("EUR");
    assertThat(chain(thrown)).contains(original);
  }

  @Test
  void malformedBodyRaisesWithContext() throws Exception {
    Throwable thrown = catchThrowable(() -> new RateClient(path -> "n/a").fetchRate("EUR"));
    assertThat(thrown).isNotNull();
    assertThat(messages(thrown)).contains("EUR");
  }

  @Test
  void programmingErrorsAreNotSwallowed() throws Exception {
    Throwable thrown = catchThrowable(
        () -> new RateClient(path -> { throw new IllegalStateException("bug"); }).fetchRate("EUR"));
    assertThat(thrown).isInstanceOf(IllegalStateException.class);
  }
}
