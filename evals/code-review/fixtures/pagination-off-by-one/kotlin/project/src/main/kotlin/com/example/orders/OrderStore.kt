package com.example.orders

/** An order. Status is "open", "shipped" or "cancelled". */
data class Order(val id: Int, val customer: String, val status: String)

/** In-memory order store. */
class OrderStore {
    private val orders = mutableListOf<Order>()

    fun add(order: Order) {
        orders += order
    }

    fun get(id: Int): Order? = orders.firstOrNull { it.id == id }

    /** Returns every order, oldest first. */
    fun all(): List<Order> = orders.toList()
}
