from src.bot.risk.limits import RiskManager

def test_pretrade():
    rm = RiskManager({"risk":{}}, None)
    assert rm.pretrade_ok("BTC-PERP", object())
