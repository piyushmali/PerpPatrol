class RiskManager:
    def __init__(self, cfg, log):
        self.cfg, self.log = cfg, log
        self.daily_loss = 0.0
        self.positions = {}  # symbol -> notional
        
    def pretrade_ok(self, symbol: str, quote) -> bool:
        """Pre-trade risk checks as documented"""
        # Per-symbol notional caps
        current_notional = abs(self.positions.get(symbol, 0.0))
        max_notional = self.cfg["risk"]["max_symbol_notional"]
        if current_notional >= max_notional:
            self.log.warning(f"Symbol {symbol} at notional limit: {current_notional}/{max_notional}")
            return False
            
        # Daily loss limits (hard stop)
        daily_limit = self.cfg["risk"]["daily_loss_limit_usd"]
        if self.daily_loss >= daily_limit:
            self.log.error(f"Daily loss limit exceeded: {self.daily_loss}/{daily_limit}")
            return False
            
        # Min quote notional check
        min_notional = self.cfg["strategy"]["min_quote_notional"]
        bid_notional = quote.bid_px * quote.bid_sz
        ask_notional = quote.ask_px * quote.ask_sz
        
        if bid_notional < min_notional or ask_notional < min_notional:
            self.log.warning(f"Quote below min notional: bid={bid_notional}, ask={ask_notional}, min={min_notional}")
            return False
            
        return True
        
    def update_position(self, symbol: str, notional: float):
        """Update position for risk tracking"""
        self.positions[symbol] = notional
        
    def update_daily_pnl(self, pnl: float):
        """Update daily P&L for loss limit tracking"""
        self.daily_loss = max(0, -pnl)  # Track losses only
