# cython: language_level=3, boundscheck=False, wraparound=False

"""Cython order book with typed resting-order objects."""

from libc.stdint cimport int64_t


cdef class RestingOrder:
    cdef public int64_t order_id
    cdef public int side
    cdef public int64_t price
    cdef public int64_t quantity
    cdef public int64_t timestamp

    def __cinit__(
        self,
        int64_t order_id,
        int side,
        int64_t price,
        int64_t quantity,
        int64_t timestamp,
    ):
        self.order_id = order_id
        self.side = side
        self.price = price
        self.quantity = quantity
        self.timestamp = timestamp


cpdef long long match_quantity(
    long long buy_price,
    long long sell_price,
    long long buy_quantity,
    long long sell_quantity,
):
    """Return executable quantity for crossing orders."""
    if buy_price < sell_price:
        return 0
    if buy_quantity <= 0 or sell_quantity <= 0:
        return 0
    return buy_quantity if buy_quantity < sell_quantity else sell_quantity


cdef class CythonOrderBook:
    """Price-time priority book using typed resting-order objects."""

    cdef dict bids
    cdef dict asks
    cdef list trades

    def __cinit__(self):
        self.bids = {}
        self.asks = {}
        self.trades = []

    cpdef list add_order(
        self,
        long long order_id,
        int side,
        long long price,
        long long quantity,
        long long timestamp,
    ):
        cdef dict opposite
        cdef dict own
        cdef list resting_orders
        cdef RestingOrder resting
        cdef long long best_price
        cdef long long traded
        cdef list new_trades = []

        if side not in (0, 1):
            raise ValueError("side must be 0 (BUY) or 1 (SELL)")
        if quantity <= 0:
            raise ValueError("quantity must be positive")

        opposite = self.asks if side == 0 else self.bids
        own = self.bids if side == 0 else self.asks

        while quantity > 0 and opposite:
            best_price = min(opposite) if side == 0 else max(opposite)

            if side == 0 and price < best_price:
                break
            if side == 1 and price > best_price:
                break

            resting_orders = opposite[best_price]
            resting = resting_orders[0]
            traded = quantity if quantity < resting.quantity else resting.quantity

            new_trades.append({
                "price": best_price,
                "quantity": traded,
                "buy_order_id": order_id if side == 0 else resting.order_id,
                "sell_order_id": resting.order_id if side == 0 else order_id,
                "timestamp": timestamp,
            })

            quantity -= traded
            resting.quantity -= traded

            if resting.quantity == 0:
                resting_orders.pop(0)
            if not resting_orders:
                del opposite[best_price]

        if quantity > 0:
            if price not in own:
                own[price] = []
            own[price].append(
                RestingOrder(order_id, side, price, quantity, timestamp)
            )

        self.trades.extend(new_trades)
        return new_trades

    cpdef int get_trade_count(self):
        return len(self.trades)
