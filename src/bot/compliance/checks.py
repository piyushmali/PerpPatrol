class Compliance:
    def __init__(self, cfg, log, client):
        self.cfg, self.log, self.client = cfg, log, client
    def pretrade_ok(self, symbol, quote)->bool:
        # Self-match and loop checks would require order ownership/fill feed; stubbed here
        return True
