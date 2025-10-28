import aiohttp
import asyncio
import time
import json
from .client_base import ExchangeClient

class WOOFiClient(ExchangeClient):
    def __init__(self, cfg, log):
        super().__init__(cfg, log)
        self.connected = False
        self.session = None
        self.api_key = cfg["exchange"]["api_key"]
        self.api_secret = cfg["exchange"]["api_secret"]
        self.base_url = cfg["exchange"]["base_url"]
        self.mode = cfg["run"]["mode"]
        
    async def connect(self):
        """Connect to WOOFi Pro API"""
        self.session = aiohttp.ClientSession()
        
        if self.mode == "simulator":
            self.connected = True
            self.log.info("WOOFiClient connected (simulator mode)")
        else:
            # For hackathon: implement basic connection test
            try:
                # Test public endpoint first
                async with self.session.get(f"{self.base_url}/v1/public/info") as resp:
                    if resp.status == 200:
                        self.connected = True
                        self.log.info("WOOFi Pro API connection established")
                    else:
                        self.log.error(f"Failed to connect to WOOFi Pro API: {resp.status}")
            except Exception as e:
                self.log.error(f"WOOFi Pro connection error: {e}")
                self.connected = False
        
    async def place_limit(self, symbol, side, price, size):
        """Place limit order"""
        if self.mode == "simulator":
            oid = f"sim-{symbol}-{side}-{price:.2f}-{size:.6f}-{int(time.time())}"
            self.log.info(f"[SIM] Place order: {oid}")
            return oid
        else:
            # For hackathon: implement order placement
            # This would need proper ed25519 signing implementation
            self.log.info(f"[LIVE] Would place: {symbol} {side} {size}@{price}")
            return f"live-{symbol}-{side}-{int(time.time())}"
    
    async def cancel(self, order_id):
        """Cancel order"""
        if self.mode == "simulator":
            self.log.info(f"[SIM] Cancel order: {order_id}")
        else:
            self.log.info(f"[LIVE] Would cancel: {order_id}")
    
    async def replace(self, order_id, price, size):
        """Replace/amend order"""
        if self.mode == "simulator":
            new_oid = f"sim-replace-{order_id}-{price:.2f}-{size:.6f}"
            self.log.info(f"[SIM] Replace order: {order_id} -> {new_oid}")
            return new_oid
        else:
            self.log.info(f"[LIVE] Would replace: {order_id} -> {price:.2f}/{size:.6f}")
            return order_id
    
    async def positions(self)->dict:
        """Get current positions"""
        if self.mode == "simulator":
            # Return mock positions for demo
            return {
                "BTC-PERP": {
                    "size": 0.001,
                    "notional": 100.0,
                    "unrealized_pnl": 5.0
                }
            }
        else:
            # For hackathon: would implement real position fetching
            return {}
    
    async def close(self):
        """Close connection"""
        self.connected = False
        if self.session:
            await self.session.close()
        self.log.info("WOOFi Pro client disconnected")
