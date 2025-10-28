import time, asyncio
from .client_base import ExchangeClient

class Executor:
    def __init__(self, cfg, log, client: ExchangeClient):
        self.cfg, self.log, self.client = cfg, log, client
        self._orders = {}  # symbol -> {'bid':id, 'ask':id}
        self._pos = {}     # symbol -> notional (approx)
        self._last_amend = 0.0
        self._refresh_min = cfg["strategy"]["refresh_min_ms"]/1000.0

    def position_notional(self, symbol:str)->float:
        return self._pos.get(symbol, 0.0)

    def jitter_up(self):
        self._refresh_min = min(1.5, self._refresh_min*1.1)

    async def sync_quotes(self, symbol:str, quote):
        now = time.time()
        if now - self._last_amend < self._refresh_min:
            return
        self._last_amend = now
        side_map = self._orders.setdefault(symbol, {})
        # Update or place orders (maker only, simplified)
        if 'bid' in side_map:
            await self.client.replace(side_map['bid'], quote.bid_px, quote.bid_sz)
        else:
            side_map['bid'] = await self.client.place_limit(symbol, "buy", quote.bid_px, quote.bid_sz)
        if 'ask' in side_map:
            await self.client.replace(side_map['ask'], quote.ask_px, quote.ask_sz)
        else:
            side_map['ask'] = await self.client.place_limit(symbol, "sell", quote.ask_px, quote.ask_sz)
        # Position tracking would normally come from fills; here we keep placeholder
