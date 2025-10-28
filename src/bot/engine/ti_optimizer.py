class TIOPT:
    def __init__(self, cfg, log, metrics):
        self.cfg, self.log, self.m = cfg, log, metrics

    def nudge(self, symbol, ob, quote, executor):
        # Simple heuristic tuner for demo purposes
        maker = self.m.maker_ratio(symbol)
        cancelpf = self.m.cancels_per_fill(symbol)
        if maker < self.cfg["ti_proxy"]["target_maker_ratio"]:
            # widen a bit
            quote.bid_px *= 0.999
            quote.ask_px *= 1.001
        if cancelpf > self.cfg["ti_proxy"]["max_cancel_per_fill"]:
            # raise refresh interval via executor hint
            executor.jitter_up()
        return quote
