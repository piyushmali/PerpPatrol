from src.bot.engine.quote_engine import QuoteEngine
from src.bot.data.orderbook import OrderBook

def test_quotes_basic():
    cfg = {
        "strategy": {
            "width_vol_mult": 1.5,
            "inv_skew_strength": 0.3,
            "imbalance_skew_strength": 0.2,
            "base_order_size": 0.001,
            "max_inventory_usd": 1000,
            "min_quote_notional": 20
        }
    }
    qe = QuoteEngine(cfg, None)
    ob = OrderBook(bids=[(100,1)], asks=[(101,1)])
    q = qe.compute_quotes("BTC-PERP", ob, inventory=0.0)
    assert q.ask_px > q.bid_px
