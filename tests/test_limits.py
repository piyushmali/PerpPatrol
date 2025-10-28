from src.bot.risk.limits import RiskManager

def test_pretrade():
    cfg = {
        "risk": {
            "max_symbol_notional": 2000,
            "daily_loss_limit_usd": 200
        },
        "strategy": {
            "min_quote_notional": 20
        }
    }
    
    class MockQuote:
        def __init__(self):
            self.bid_px = 100.0
            self.ask_px = 101.0
            self.bid_sz = 0.5
            self.ask_sz = 0.5
    
    rm = RiskManager(cfg, None)
    quote = MockQuote()
    assert rm.pretrade_ok("BTC-PERP", quote)
