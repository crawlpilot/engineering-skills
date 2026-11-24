package com.example.accounts

import kotlin.test.Test
import kotlin.test.assertEquals

class UserTest {
    @Test
    fun `users compare by value`() {
        assertEquals(User(1, "a@example.com", "A"), User(1, "a@example.com", "A"))
    }
}
