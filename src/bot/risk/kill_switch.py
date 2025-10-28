class KillSwitches:
    def __init__(self, cfg, log):
        self.cfg, self.log = cfg, log
    def tripped(self, executor)->bool:
        # Wire up conditions: loss limits, error rates, spread blowouts
        return False
