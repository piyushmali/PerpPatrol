from .client_base import ExchangeClient

class WOOFiClient(ExchangeClient):
    def __init__(self, cfg, log):
        super().__init__(cfg, log)
        self.connected = False
    async def connect(self):
        # TODO: Implement auth and WS connect
        self.connected = True
        self.log.info("WOOFiClient connected (stub)")
    async def place_limit(self, symbol, side, price, size):
        # TODO: Call REST place order
        oid = f"stub-{symbol}-{side}-{price:.2f}-{size:.6f}"
        self.log.debug(f"place {oid}")
        return oid
    async def cancel(self, order_id):
        # TODO: REST cancel
        self.log.debug(f"cancel {order_id}")
    async def replace(self, order_id, price, size):
        # TODO: REST amend/replace
        self.log.debug(f"replace {order_id} -> {price:.2f}/{size:.6f}")
        return order_id
    async def positions(self)->dict:
        # TODO: REST positions
        return {}
    async def close(self):
        self.connected = False
