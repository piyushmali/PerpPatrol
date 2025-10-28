from collections import defaultdict

class Metrics:
    def __init__(self, cfg, log):
        self.cfg, self.log = cfg, log
        self._maker = defaultdict(lambda: 0.7)
        self._cancelpf = defaultdict(lambda: 3.0)
    def observe(self, symbol, ob, executor): pass
    def maker_ratio(self, symbol): return self._maker[symbol]
    def cancels_per_fill(self, symbol): return self._cancelpf[symbol]
