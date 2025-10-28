from collections import defaultdict
import time

class Metrics:
    def __init__(self, cfg, log):
        self.cfg, self.log = cfg, log
        # TI Metrics as documented
        self._maker_fills = defaultdict(int)
        self._taker_fills = defaultdict(int)
        self._holding_times = defaultdict(list)
        self._slippage_data = defaultdict(list)
        self._spread_at_fill = defaultdict(list)
        self._cancels = defaultdict(int)
        self._fills = defaultdict(int)
        self._counterparties = defaultdict(set)
        
    def observe(self, symbol, ob, executor):
        """Observe market state for metrics"""
        # Record current spread for later fill analysis
        if ob.ready():
            spread_bps = (ob.spread() / ob.mid()) * 10000
            self._current_spread = {symbol: spread_bps}
            
    def record_fill(self, symbol: str, side: str, price: float, size: float, 
                   is_maker: bool, counterparty_id: str = None):
        """Record a fill for TI metrics"""
        if is_maker:
            self._maker_fills[symbol] += 1
        else:
            self._taker_fills[symbol] += 1
            
        self._fills[symbol] += 1
        
        if counterparty_id:
            self._counterparties[symbol].add(counterparty_id)
            
    def record_cancel(self, symbol: str):
        """Record a cancel for cancel/fill ratio"""
        self._cancels[symbol] += 1
        
    def record_holding_time(self, symbol: str, holding_time_ms: int):
        """Record holding time for average calculation"""
        self._holding_times[symbol].append(holding_time_ms)
        # Keep only recent data (last 100 fills)
        if len(self._holding_times[symbol]) > 100:
            self._holding_times[symbol] = self._holding_times[symbol][-100:]
            
    def maker_ratio(self, symbol: str) -> float:
        """Get maker ratio for symbol"""
        total_fills = self._maker_fills[symbol] + self._taker_fills[symbol]
        if total_fills == 0:
            return 0.7  # Default assumption
        return self._maker_fills[symbol] / total_fills
        
    def cancels_per_fill(self, symbol: str) -> float:
        """Get cancel/fill ratio for symbol"""
        fills = self._fills[symbol]
        if fills == 0:
            return 3.0  # Default assumption
        return self._cancels[symbol] / fills
        
    def avg_holding_time(self, symbol: str) -> float:
        """Get average holding time in ms"""
        times = self._holding_times[symbol]
        if not times:
            return 2000.0  # Default 2 seconds
        return sum(times) / len(times)
        
    def distinct_counterparties(self, symbol: str) -> int:
        """Get number of distinct counterparties"""
        return len(self._counterparties[symbol])
