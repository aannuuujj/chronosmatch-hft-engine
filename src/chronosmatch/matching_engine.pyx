# cython: language_level=3, boundscheck=False, wraparound=False

"""Initial Cython price-time priority matching engine."""

cdef struct Order:
    long long order_id
    long long price
    long long quantity
    long long timestamp
    int side


cpdef long long match_quantity(long long buy_price,
                               long long sell_price,
                               long long buy_quantity,
                               long long sell_quantity):
    """Return the executable quantity for a crossing buy and sell."""
    if buy_price < sell_price:
        return 0
    if buy_quantity <= 0 or sell_quantity <= 0:
        return 0

    if buy_quantity < sell_quantity:
        return buy_quantity
    return sell_quantity
