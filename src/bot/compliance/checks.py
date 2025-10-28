import time
from .loop_detector import LoopDetector

class Compliance:
    def __init__(self, cfg, log, client):
        self.cfg, self.log, self.client = cfg, log, client
        self.loop_detector = LoopDetector(cfg["compliance"]["loop_min_holding_ms"])
        self.last_fill_time = {}  # symbol -> timestamp
        self.amend_count = {}     # symbol -> count in current second
        self.last_amend_reset = time.time()
        
    def pretrade_ok(self, symbol, quote) -> bool:
        """Pre-trade compliance checks as documented"""
        now_ms = int(time.time() * 1000)
        
        # Loop prevention via minimum holding time
        if symbol in self.last_fill_time:
            if not self.loop_detector.ok(self.last_fill_time[symbol], now_ms):
                self.log.warning(f"Loop detector blocked trade for {symbol}")
                return False
        
        # Rate limiting for amends (no ping-pong)
        now = time.time()
        if now - self.last_amend_reset > 1.0:  # Reset every second
            self.amend_count.clear()
            self.last_amend_reset = now
            
        current_amends = self.amend_count.get(symbol, 0)
        max_amends = self.cfg["compliance"]["max_amends_per_sec"]
        if current_amends >= max_amends:
            self.log.warning(f"Rate limit exceeded for {symbol}: {current_amends}/{max_amends}")
            return False
            
        return True
        
    def record_fill(self, symbol: str, timestamp_ms: int):
        """Record a fill for loop detection"""
        self.last_fill_time[symbol] = timestamp_ms
        
    def record_amend(self, symbol: str):
        """Record an amend for rate limiting"""
        self.amend_count[symbol] = self.amend_count.get(symbol, 0) + 1
        
    def check_self_match(self, symbol: str, side: str, price: float) -> bool:
        """Check for potential self-match (simplified)"""
        # In a real implementation, this would check against our own orders
        # For now, we assume no self-match risk in maker-only strategy
        return True
