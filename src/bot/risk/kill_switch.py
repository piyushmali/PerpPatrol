import time

class KillSwitches:
    def __init__(self, cfg, log):
        self.cfg, self.log = cfg, log
        self.error_count = 0
        self.last_error_time = 0
        self.last_spread_check = 0
        
    def tripped(self, executor) -> bool:
        """Check if kill switches should be triggered"""
        now = time.time()
        
        # Check error rate (simplified)
        if self.error_count > 10 and (now - self.last_error_time) < 60:
            self.log.error("Kill switch: High error rate detected")
            return True
            
        # Check if we haven't received market data recently (data gap)
        if hasattr(executor, '_last_market_update'):
            if now - executor._last_market_update > 30:  # 30 seconds
                self.log.error("Kill switch: Market data gap detected")
                return True
                
        return False
        
    def record_error(self):
        """Record an error for rate tracking"""
        self.error_count += 1
        self.last_error_time = time.time()
        
    def reset_errors(self):
        """Reset error tracking"""
        self.error_count = 0
