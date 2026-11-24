package com.example.rates

// Hidden grading tests: copied in by the grader, never shown to the agent.
import java.io.IOException
import java.math.BigDecimal
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertFailsWith
import kotlin.test.assertTrue

class HiddenErrorHandlingTest {

    private fun chain(t: Throwable): List<Throwable> = generateSequence(t) { it.cause }.take(20).toList()

    private fun messages(t: Throwable) = chain(t).joinToString(" ") { it.message.orEmpty() }

    @Test
    fun `success still returns the rate`() {
        assertEquals(BigDecimal("0.92"), RateClient { "0.92\n" }.fetchRate("EUR"))
    }

    @Test
    fun `network failure raises with context and cause`() {
        val original = IOException("connection refused")
        val thrown = assertFailsWith<Throwable> { RateClient { throw original }.fetchRate("EUR") }
        assertTrue("EUR" in messages(thrown), messages(thrown))
        assertTrue(original in chain(thrown))
    }

    @Test
    fun `malformed body raises with context`() {
        val thrown = assertFailsWith<Throwable> { RateClient { "n/a" }.fetchRate("EUR") }
        assertTrue("EUR" in messages(thrown), messages(thrown))
    }

    @Test
    fun `programming errors are not swallowed`() {
        assertFailsWith<IllegalStateException> {
            RateClient { throw IllegalStateException("bug") }.fetchRate("EUR")
        }
    }
}
