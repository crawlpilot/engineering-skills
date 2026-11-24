package com.example.orders

import java.util.concurrent.ConcurrentHashMap

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

    /**
     * Returns one page of orders, oldest first.
     *
     * Pages are numbered from 1. Cancelled orders are left out unless [includeCancelled] is set.
     */
    fun page(page: Int, pageSize: Int = 20, includeCancelled: Boolean = false): List<Order> {
        require(page >= 1 && pageSize >= 1) { "page and pageSize must be at least 1" }
        val source = if (includeCancelled) orders else orders.filter { it.status != "cancelled" }
        val start = page * pageSize
        var end = minOf(start + pageSize, source.size)
        if (start >= source.size) return emptyList()
        return source.subList(start, end).toList()
    }
}
