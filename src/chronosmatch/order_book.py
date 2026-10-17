"""Basic price-time priority order book."""

from dataclasses import dataclass
from collections import defaultdict
from typing import Literal

Side = Literal["BUY", "SELL"]


@dataclass
class Order:
    order_id: int
    side: Side
    price: int
    quantity: int
    timestamp: int


class OrderBook:
    def __init__(self):
        self.bids = defaultdict(list)
        self.asks = defaultdict(list)
        self.trades = []

    def add_order(self, order: Order):
        opposite = self.asks if order.side == "BUY" else self.bids

        while order.quantity > 0 and opposite:
            best_price = min(opposite) if order.side == "BUY" else max(opposite)

            if order.side == "BUY" and order.price < best_price:
                break
            if order.side == "SELL" and order.price > best_price:
                break

            resting_orders = opposite[best_price]
            resting = resting_orders[0]
            quantity = min(order.quantity, resting.quantity)

            self.trades.append({
                "price": best_price,
                "quantity": quantity,
                "buy_order_id": order.order_id if order.side == "BUY" else resting.order_id,
                "sell_order_id": resting.order_id if order.side == "BUY" else order.order_id,
            })

            order.quantity -= quantity
            resting.quantity -= quantity

            if resting.quantity == 0:
                resting_orders.pop(0)
            if not resting_orders:
                del opposite[best_price]

        if order.quantity > 0:
            book = self.bids if order.side == "BUY" else self.asks
            book[order.price].append(order)
