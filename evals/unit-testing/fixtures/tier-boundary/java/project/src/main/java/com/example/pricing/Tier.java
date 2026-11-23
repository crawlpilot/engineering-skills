package com.example.pricing;

/** Price tier for an order, chosen by the number of items in it. */
public enum Tier {
  FREE,
  STANDARD,
  BULK;

  /** Orders of this many items or more are priced as bulk. */
  static final int BULK_THRESHOLD = 50;

  /**
   * Returns the tier for an order quantity.
   *
   * <ul>
   *   <li>0 items: {@link #FREE}
   *   <li>1 to 49 items: {@link #STANDARD}
   *   <li>50 items or more: {@link #BULK}
   * </ul>
   *
   * @throws IllegalArgumentException if quantity is negative
   */
  public static Tier forQuantity(int quantity) {
    if (quantity < 0) {
      throw new IllegalArgumentException("quantity must not be negative: " + quantity);
    }
    if (quantity == 0) {
      return FREE;
    }
    if (quantity > BULK_THRESHOLD) {
      return BULK;
    }
    return STANDARD;
  }
}
