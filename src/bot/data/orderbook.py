from dataclasses import dataclass, field
from typing import List, Tuple

@dataclass
class OrderBook:
    bids: List[Tuple[float,float]] = field(default_factory=list)  # (price, size)
    asks: List[Tuple[float,float]] = field(default_factory=list)

    def mid(self)->float:
        if not self.bids or not self.asks: return 0.0
        return (self.bids[0][0] + self.asks[0][0]) / 2

    def spread(self)->float:
        if not self.bids or not self.asks: return float("inf")
        return max(0.0, self.asks[0][0] - self.bids[0][0])

    def imbalance(self)->float:
        bid_sz = sum(s for _,s in self.bids[:5])
        ask_sz = sum(s for _,s in self.asks[:5])
        tot = bid_sz + ask_sz
        return 0.0 if tot==0 else (bid_sz - ask_sz)/tot

    def ready(self)->bool:
        return bool(self.bids and self.asks)
