import random
from dataclasses import dataclass
from ..bot.data.orderbook import OrderBook

@dataclass
class SimState:
    mid: float = 100.0
    vol: float = 0.0005

class SimExchange:
    def __init__(self):
        self.state = SimState()

    def step(self)->OrderBook:
        # Geometric random walk for mid; simple spread model
        drift = 0.0
        shock = random.gauss(0, self.state.vol)
        self.state.mid *= (1.0 + drift + shock)
        spread = max(0.1, 0.6 * self.state.mid * self.state.vol)
        ob = OrderBook(bids=[(self.state.mid - spread/2, 1.2)], asks=[(self.state.mid + spread/2, 1.1)])
        return ob
