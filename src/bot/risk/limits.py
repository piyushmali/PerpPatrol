class RiskManager:
    def __init__(self, cfg, log):
        self.cfg, self.log = cfg, log
        self.daily_loss = 0.0
    def pretrade_ok(self, symbol:str, quote)->bool:
        # Example checks: min notional already handled by engine
        return True
