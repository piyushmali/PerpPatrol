import asyncio
import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
from .woofi_api import WOOFiProAPI
import os

class LiveDataManager:
    """Manages live data from WOOFi Pro API"""
    
    def __init__(self):
        self.api_available = bool(os.getenv('WOOFI_API_KEY') and os.getenv('WOOFI_API_SECRET'))
        self.last_fetch = None
        self.cache_duration = 30  # Cache for 30 seconds
        
    async def get_live_positions(self):
        """Get real positions from WOOFi Pro"""
        if not self.api_available:
            return self._get_mock_positions()
            
        try:
            async with WOOFiProAPI() as api:
                positions = await api.get_positions()
                if positions:
                    return self._format_positions(positions)
                else:
                    return self._get_mock_positions()
        except Exception as e:
            print(f"⚠️ API Error (using mock data): {e}")
            return self._get_mock_positions()
    
    async def get_live_trades(self, symbol=None, limit=50):
        """Get real trades from WOOFi Pro"""
        if not self.api_available:
            return self._get_mock_trades(limit)
            
        try:
            async with WOOFiProAPI() as api:
                trades = await api.get_trades(symbol, limit)
                if trades:
                    return self._format_trades(trades)
                else:
                    return self._get_mock_trades(limit)
        except Exception as e:
            print(f"⚠️ API Error (using mock data): {e}")
            return self._get_mock_trades(limit)
    
    async def get_live_orders(self, symbol=None):
        """Get real orders from WOOFi Pro"""
        if not self.api_available:
            return self._get_mock_orders()
            
        try:
            async with WOOFiProAPI() as api:
                orders = await api.get_orders(symbol)
                if orders:
                    return self._format_orders(orders)
                else:
                    return self._get_mock_orders()
        except Exception as e:
            print(f"⚠️ API Error (using mock data): {e}")
            return self._get_mock_orders()
    
    async def get_live_orderbook(self, symbol):
        """Get real orderbook from WOOFi Pro"""
        if not self.api_available:
            return self._get_mock_orderbook(symbol)
            
        try:
            async with WOOFiProAPI() as api:
                orderbook = await api.get_orderbook(symbol)
                if orderbook:
                    return self._format_orderbook(orderbook)
                else:
                    return self._get_mock_orderbook(symbol)
        except Exception as e:
            print(f"⚠️ API Error (using mock data): {e}")
            return self._get_mock_orderbook(symbol)
    
    async def get_account_info(self):
        """Get account information"""
        if not self.api_available:
            return self._get_mock_account()
            
        try:
            async with WOOFiProAPI() as api:
                account = await api.get_account_info()
                if account:
                    return account
                else:
                    return self._get_mock_account()
        except Exception as e:
            print(f"⚠️ API Error (using mock data): {e}")
            return self._get_mock_account()
    
    def _format_positions(self, positions):
        """Format positions data"""
        formatted = []
        for pos in positions:
            formatted.append({
                'symbol': pos.get('symbol', ''),
                'size': float(pos.get('holding', 0)),
                'notional': float(pos.get('notional', 0)),
                'unrealized_pnl': float(pos.get('unrealPnl', 0)),
                'entry_price': float(pos.get('averageOpenPrice', 0))
            })
        return formatted
    
    def _format_trades(self, trades):
        """Format trades data"""
        formatted = []
        for trade in trades:
            formatted.append({
                'timestamp': datetime.fromtimestamp(int(trade.get('timestamp', 0)) / 1000),
                'symbol': trade.get('symbol', ''),
                'side': trade.get('side', ''),
                'size': float(trade.get('executed_quantity', 0)),
                'price': float(trade.get('executed_price', 0)),
                'fee': float(trade.get('fee', 0)),
                'order_id': trade.get('order_id', '')
            })
        return sorted(formatted, key=lambda x: x['timestamp'], reverse=True)
    
    def _format_orders(self, orders):
        """Format orders data"""
        formatted = []
        for order in orders:
            formatted.append({
                'order_id': order.get('order_id', ''),
                'symbol': order.get('symbol', ''),
                'side': order.get('side', ''),
                'type': order.get('type', ''),
                'size': float(order.get('quantity', 0)),
                'price': float(order.get('price', 0)),
                'status': order.get('status', ''),
                'created_time': datetime.fromtimestamp(int(order.get('created_time', 0)) / 1000)
            })
        return formatted
    
    def _format_orderbook(self, orderbook):
        """Format orderbook data"""
        asks = []
        bids = []
        
        for ask in orderbook.get('asks', [])[:5]:
            asks.append({
                'Type': 'ASK',
                'Price': f"${float(ask[0]):.2f}",
                'Size': f"{float(ask[1]):.4f}"
            })
        
        for bid in orderbook.get('bids', [])[:5]:
            bids.append({
                'Type': 'BID',
                'Price': f"${float(bid[0]):.2f}",
                'Size': f"{float(bid[1]):.4f}"
            })
        
        return asks + bids
    
    # Mock data methods for fallback
    def _get_mock_positions(self):
        """Mock positions for demo"""
        import random
        return [{
            'symbol': 'BTC-PERP',
            'size': round(random.uniform(0.001, 0.1), 4),
            'notional': round(random.uniform(100, 1000), 2),
            'unrealized_pnl': round(random.uniform(-50, 150), 2),
            'entry_price': round(random.uniform(66000, 68000), 2)
        }]
    
    def _get_mock_trades(self, limit):
        """Mock trades for demo"""
        import random
        trades = []
        for i in range(min(limit, 10)):
            trades.append({
                'timestamp': datetime.now() - timedelta(minutes=i*5),
                'symbol': 'BTC-PERP',
                'side': random.choice(['BUY', 'SELL']),
                'size': round(random.uniform(0.001, 0.01), 4),
                'price': round(random.uniform(66000, 68000), 2),
                'fee': round(random.uniform(0.1, 2.0), 2),
                'order_id': f"mock_order_{i}"
            })
        return trades
    
    def _get_mock_orders(self):
        """Mock orders for demo"""
        import random
        return [{
            'order_id': f"mock_order_{i}",
            'symbol': 'BTC-PERP',
            'side': random.choice(['BUY', 'SELL']),
            'type': 'LIMIT',
            'size': round(random.uniform(0.001, 0.01), 4),
            'price': round(random.uniform(66000, 68000), 2),
            'status': 'NEW',
            'created_time': datetime.now() - timedelta(minutes=i)
        } for i in range(3)]
    
    def _get_mock_orderbook(self, symbol):
        """Mock orderbook for demo"""
        import random
        base_price = 67000
        spread = random.uniform(0.01, 0.05)
        
        orderbook_data = []
        
        # Asks
        for i in range(5):
            ask_price = base_price + spread/2 + (i * spread/10)
            orderbook_data.append({
                'Type': 'ASK',
                'Price': f"${ask_price:.2f}",
                'Size': f"{random.uniform(0.1, 2.0):.4f}"
            })
        
        # Bids
        for i in range(5):
            bid_price = base_price - spread/2 - (i * spread/10)
            orderbook_data.append({
                'Type': 'BID',
                'Price': f"${bid_price:.2f}",
                'Size': f"{random.uniform(0.1, 2.0):.4f}"
            })
        
        return orderbook_data
    
    def _get_mock_account(self):
        """Mock account info for demo"""
        return {
            'application_id': 'mock_app',
            'account': 'mock_account',
            'alias': 'PerpPatrol Bot',
            'account_mode': 'FUTURES',
            'leverage': '10',
            'taker_fee_rate': '0.0005',
            'maker_fee_rate': '0.0002',
            'futures_leverage': '10',
            'futures_taker_fee_rate': '0.0005',
            'futures_maker_fee_rate': '0.0002'
        }

# Global instance
live_data_manager = LiveDataManager()
