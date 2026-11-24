package com.example.accounts;

/** A user with this email already exists. */
public class DuplicateEmailException extends RuntimeException {
  public DuplicateEmailException(String email, Throwable cause) {
    super("a user with email " + email + " already exists", cause);
  }
}
