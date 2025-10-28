from dataclasses import dataclass
from ..data.orderbook import OrderBook
from .vol_estimator import VolEstimator

@dataclass
class Quote:
    bid_px: float
    ask_px: float
    bid_sz: float
    ask_sz: float

class QuoteEngine:
    def __init__(self, cfg, log):
        self.cfg, self.log = cfg, log
        self.vol = VolEstimator()
        self.state = {}

    def compute_quotes(self, symbol:str, ob:OrderBook, inventory: float)->Quote:
        mid = ob.mid()
        self.vol.update(mid)
        rv = self.vol.realized()
        width = max(1e-6, self.cfg["strategy"]["width_vol_mult"] * rv * mid)
        imb = ob.imbalance()
        inv_skew = self.cfg["strategy"]["inv_skew_strength"] * (inventory / max(1e-9, self.cfg["strategy"]["max_inventory_usd"]))
        imb_skew = self.cfg["strategy"]["imbalance_skew_strength"] * (-imb)
        skew = inv_skew + imb_skew
        bid = mid - width*(1+skew)
        ask = mid + width*(1-skew)
        base_size = self.cfg["strategy"]["base_order_size"]
        min_notional = self.cfg["strategy"]["min_quote_notional"]
        bid_sz = max(base_size, min_notional/max(bid,1e-6))
        ask_sz = max(base_size, min_notional/max(ask,1e-6))
        return Quote(bid, ask, bid_sz, ask_sz)
