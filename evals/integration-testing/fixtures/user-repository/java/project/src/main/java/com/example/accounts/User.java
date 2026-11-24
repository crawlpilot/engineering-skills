package com.example.accounts;

/** A stored user. Emails are lower-cased. */
public record User(long id, String email, String name) {}
