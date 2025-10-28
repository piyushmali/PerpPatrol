class PnLTracker:
    def __init__(self): self.p=0.0
    def update_fill(self, fill): pass
    def daily(self)->float: return self.p
