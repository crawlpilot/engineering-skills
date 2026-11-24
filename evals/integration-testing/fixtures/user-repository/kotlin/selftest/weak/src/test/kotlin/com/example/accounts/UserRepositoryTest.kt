package com.example.accounts

import kotlin.test.Test
import kotlin.test.assertEquals

class UserRepositoryTest {
    @Test
    fun `user keeps its email`() {
        assertEquals("a@example.com", User(1, "a@example.com", "A").email)
    }
}
