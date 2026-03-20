"""
Binance Exchange Client
"""

import asyncio
import hmac
import hashlib
from typing import Dict, List, Optional
from urllib.parse import urlencode

import aiohttp
import websockets


class BinanceClient:
    """Binance API client with WebSocket support"""
    
    def __init__(self, testnet: bool = True, api_key: str = None, api_secret: str = None):
        self.testnet = testnet
        self.api_key = api_key
        self.api_secret = api_secret
        
        # Base URLs
        if testnet:
            self.base_url = "https://testnet.binance.vision"
            self.ws_url = "wss://testnet.binance.vision/ws"
        else:
            self.base_url = "https://api.binance.com"
            self.ws_url = "wss://stream.binance.com:9443/ws"
        
        self.session: Optional[aiohttp.ClientSession] = None
        self.ws_connections: Dict[str, websockets.WebSocketClientProtocol] = {}
    
    async def connect(self):
        """Initialize HTTP session"""
        headers = {}
        if self.api_key:
            headers["X-MBX-APIKEY"] = self.api_key
        
        self.session = aiohttp.ClientSession(headers=headers)
    
    async def disconnect(self):
        """Close all connections"""
        if self.session:
            await self.session.close()
        
        for ws in self.ws_connections.values():
            await ws.close()
    
    def _generate_signature(self, params: Dict) -> str:
        """Generate HMAC signature for authenticated requests"""
        query_string = urlencode(params)
        signature = hmac.new(
            self.api_secret.encode(),
            query_string.encode(),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    async def get_ticker(self, symbol: str) -> Dict:
        """Get 24h ticker data"""
        url = f"{self.base_url}/api/v3/ticker/24hr"
        params = {"symbol": symbol}
        
        async with self.session.get(url, params=params) as response:
            data = await response.json()
            return {
                "symbol": data["symbol"],
                "price": float(data["lastPrice"]),
                "change_24h": float(data["priceChangePercent"]),
                "volume": float(data["volume"]),
                "high": float(data["highPrice"]),
                "low": float(data["lowPrice"])
            }
    
    async def get_klines(
        self,
        symbol: str,
        interval: str = "1h",
        limit: int = 100
    ) -> List[Dict]:
        """Get historical candlestick data"""
        url = f"{self.base_url}/api/v3/klines"
        params = {
            "symbol": symbol,
            "interval": interval,
            "limit": limit
        }
        
        async with self.session.get(url, params=params) as response:
            data = await response.json()
            return [
                {
                    "timestamp": k[0],
                    "open": float(k[1]),
                    "high": float(k[2]),
                    "low": float(k[3]),
                    "close": float(k[4]),
                    "volume": float(k[5])
                }
                for k in data
            ]
    
    async def place_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        order_type: str = "MARKET"
    ) -> Dict:
        """Place a new order"""
        url = f"{self.base_url}/api/v3/order"
        params = {
            "symbol": symbol,
            "side": side,
            "type": order_type,
            "quantity": quantity,
            "timestamp": int(asyncio.get_event_loop().time() * 1000)
        }
        
        params["signature"] = self._generate_signature(params)
        
        async with self.session.post(url, params=params) as response:
            return await response.json()
    
    async def get_balances(self) -> Dict[str, Dict]:
        """Get account balances"""
        url = f"{self.base_url}/api/v3/account"
        params = {"timestamp": int(asyncio.get_event_loop().time() * 1000)}
        params["signature"] = self._generate_signature(params)
        
        async with self.session.get(url, params=params) as response:
            data = await response.json()
            return {
                b["asset"]: {
                    "free": float(b["free"]),
                    "locked": float(b["locked"])
                }
                for b in data.get("balances", [])
                if float(b["free"]) > 0 or float(b["locked"]) > 0
            }
    
    async def subscribe_ticker(self, symbol: str, callback):
        """Subscribe to real-time ticker updates via WebSocket"""
        stream = f"{symbol.lower()}@ticker"
        ws_url = f"{self.ws_url}/{stream}"
        
        async with websockets.connect(ws_url) as ws:
            self.ws_connections[symbol] = ws
            
            async for message in ws:
                data = json.loads(message)
                await callback(data)
