import asyncio, random
from .orderbook import OrderBook

class MarketDataService:
    def __init__(self, cfg, log):
        self.cfg, self.log = cfg, log
        self._books = {}

    async def start(self): pass
    async def stop(self): pass
    async def subscribe_orderbook(self, symbol: str):
        # Placeholder: in live mode, subscribe WS; in simulator, synthetic updates happen elsewhere
        self._books[symbol] = OrderBook(bids=[(100.0,1.0)], asks=[(100.5,1.0)])

    def get_orderbook(self, symbol:str)->OrderBook|None:
        # In simulator mode, let the simulator mutate this; live would be updated by WS listener
        return self._books.get(symbol)
