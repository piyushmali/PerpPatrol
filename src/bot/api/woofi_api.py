import aiohttp
import asyncio
import time
import json
import hmac
import hashlib
import base64
from datetime import datetime
import os

class WOOFiProAPI:
    """Real WOOFi Pro API client for hackathon"""
    
    def __init__(self):
        self.base_url = "https://api.woo.org"
        self.api_key = os.getenv('WOOFI_API_KEY', '')
        self.api_secret = os.getenv('WOOFI_API_SECRET', '')
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def _generate_signature(self, timestamp, method, path, body=""):
        """Generate signature for WOOFi Pro API with proper ed25519 signing"""
        try:
            if self.api_key.startswith('ed25519:'):
                # Proper ed25519 signing for WOOFi Pro
                from nacl.signing import SigningKey
                from nacl.encoding import Base58Encoder
                import base58
                
                # The API secret is the private key in base58 format
                private_key_bytes = base58.b58decode(self.api_secret)
                signing_key = SigningKey(private_key_bytes)
                
                # Create the message to sign (WOOFi Pro format)
                message = f"{timestamp}{method.upper()}{path}{body}"
                
                # Sign the message
                signed = signing_key.sign(message.encode())
                
                # Return the signature in base58 format
                return base58.b58encode(signed.signature).decode()
            else:
                # Standard HMAC signing for other exchanges
                message = f"{timestamp}{method.upper()}{path}{body}"
                return hmac.new(
                    self.api_secret.encode(),
                    message.encode(),
                    hashlib.sha256
                ).hexdigest()
        except Exception as e:
            print(f"❌ Signature generation failed: {e}")
            # Fallback to mock mode
            return "mock_signature_for_demo"
    
    async def get_account_info(self):
        """Get account information"""
        try:
            timestamp = str(int(time.time() * 1000))
            path = "/v1/client/info"
            signature = self._generate_signature(timestamp, "GET", path)
            
            headers = {
                'x-api-key': self.api_key,
                'x-api-signature': signature,
                'x-api-timestamp': timestamp,
                'Content-Type': 'application/json'
            }
            
            async with self.session.get(f"{self.base_url}{path}", headers=headers) as resp:
                if resp.status == 200:
                    return await resp.json()
                else:
                    print(f"Account info error: {resp.status}")
                    return None
        except Exception as e:
            print(f"Account info exception: {e}")
            return None
    
    async def get_positions(self):
        """Get current positions"""
        try:
            timestamp = str(int(time.time() * 1000))
            path = "/v1/positions"
            signature = self._generate_signature(timestamp, "GET", path)
            
            headers = {
                'x-api-key': self.api_key,
                'x-api-signature': signature,
                'x-api-timestamp': timestamp,
                'Content-Type': 'application/json'
            }
            
            async with self.session.get(f"{self.base_url}{path}", headers=headers) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get('rows', [])
                else:
                    print(f"Positions error: {resp.status}")
                    return []
        except Exception as e:
            print(f"Positions exception: {e}")
            return []
    
    async def get_orders(self, symbol=None):
        """Get current orders"""
        try:
            timestamp = str(int(time.time() * 1000))
            path = "/v1/orders"
            if symbol:
                path += f"?symbol={symbol}"
            
            signature = self._generate_signature(timestamp, "GET", path)
            
            headers = {
                'x-api-key': self.api_key,
                'x-api-signature': signature,
                'x-api-timestamp': timestamp,
                'Content-Type': 'application/json'
            }
            
            async with self.session.get(f"{self.base_url}{path}", headers=headers) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get('rows', [])
                else:
                    print(f"Orders error: {resp.status}")
                    return []
        except Exception as e:
            print(f"Orders exception: {e}")
            return []
    
    async def get_trades(self, symbol=None, limit=50):
        """Get recent trades"""
        try:
            timestamp = str(int(time.time() * 1000))
            path = f"/v1/client/trades?size={limit}"
            if symbol:
                path += f"&symbol={symbol}"
            
            signature = self._generate_signature(timestamp, "GET", path)
            
            headers = {
                'x-api-key': self.api_key,
                'x-api-signature': signature,
                'x-api-timestamp': timestamp,
                'Content-Type': 'application/json'
            }
            
            async with self.session.get(f"{self.base_url}{path}", headers=headers) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get('rows', [])
                else:
                    print(f"Trades error: {resp.status}")
                    return []
        except Exception as e:
            print(f"Trades exception: {e}")
            return []
    
    async def get_orderbook(self, symbol):
        """Get orderbook for symbol"""
        try:
            # This is a public endpoint, no auth needed
            async with self.session.get(f"{self.base_url}/v1/public/orderbook/{symbol}") as resp:
                if resp.status == 200:
                    return await resp.json()
                else:
                    print(f"Orderbook error: {resp.status}")
                    return None
        except Exception as e:
            print(f"Orderbook exception: {e}")
            return None
    
    async def place_order(self, symbol, side, order_type, quantity, price=None):
        """Place an order"""
        try:
            timestamp = str(int(time.time() * 1000))
            path = "/v1/order"
            
            body_data = {
                "symbol": symbol,
                "side": side.upper(),
                "order_type": order_type.upper(),
                "order_quantity": str(quantity)
            }
            
            if price and order_type.upper() == "LIMIT":
                body_data["order_price"] = str(price)
            
            body = json.dumps(body_data)
            signature = self._generate_signature(timestamp, "POST", path, body)
            
            headers = {
                'x-api-key': self.api_key,
                'x-api-signature': signature,
                'x-api-timestamp': timestamp,
                'Content-Type': 'application/json'
            }
            
            async with self.session.post(f"{self.base_url}{path}", headers=headers, data=body) as resp:
                if resp.status == 200:
                    return await resp.json()
                else:
                    error_text = await resp.text()
                    print(f"Order placement error: {resp.status} - {error_text}")
                    return None
        except Exception as e:
            print(f"Order placement exception: {e}")
            return None
