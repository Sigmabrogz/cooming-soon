"""WebSocket clients for Polymarket real-time data."""

import json
import threading
import time
from typing import Callable, List, Optional, Dict, Any
import websocket
from .exceptions import WebSocketError


class BaseWebSocket:
    """Base WebSocket client."""
    
    def __init__(self, url: str):
        """
        Initialize WebSocket client.
        
        Args:
            url: WebSocket URL
        """
        self.url = url
        self.ws = None
        self.running = False
        self.thread = None
        self.callbacks = {}
    
    def connect(self):
        """Establish WebSocket connection."""
        self.ws = websocket.WebSocketApp(
            self.url,
            on_open=self._on_open,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close,
        )
    
    def _on_open(self, ws):
        """Handle connection open."""
        print(f"WebSocket connected to {self.url}")
        self.running = True
    
    def _on_message(self, ws, message):
        """Handle incoming message."""
        try:
            data = json.loads(message)
            self._handle_message(data)
        except json.JSONDecodeError as e:
            print(f"Failed to parse message: {e}")
    
    def _on_error(self, ws, error):
        """Handle error."""
        print(f"WebSocket error: {error}")
    
    def _on_close(self, ws, close_status_code, close_msg):
        """Handle connection close."""
        print(f"WebSocket closed: {close_status_code} - {close_msg}")
        self.running = False
    
    def _handle_message(self, data: Dict[str, Any]):
        """
        Handle parsed message (override in subclass).
        
        Args:
            data: Parsed message data
        """
        pass
    
    def send(self, data: Dict[str, Any]):
        """
        Send message to WebSocket.
        
        Args:
            data: Message data
        """
        if self.ws:
            self.ws.send(json.dumps(data))
    
    def run(self, run_forever: bool = True):
        """
        Run WebSocket connection.
        
        Args:
            run_forever: Whether to run in blocking mode
        """
        if not self.ws:
            self.connect()
        
        if run_forever:
            self.ws.run_forever()
        else:
            self.thread = threading.Thread(target=self.ws.run_forever)
            self.thread.daemon = True
            self.thread.start()
    
    def close(self):
        """Close WebSocket connection."""
        self.running = False
        if self.ws:
            self.ws.close()
        if self.thread:
            self.thread.join(timeout=5)


class CLOBUserWebSocket(BaseWebSocket):
    """WebSocket client for CLOB user channel."""
    
    def __init__(
        self,
        api_key: str,
        secret: str,
        passphrase: str,
        url: str = "wss://ws-subscriptions-clob.polymarket.com/ws/",
    ):
        """
        Initialize user channel WebSocket.
        
        Args:
            api_key: API key
            secret: API secret
            passphrase: API passphrase
            url: WebSocket URL
        """
        super().__init__(url)
        self.api_key = api_key
        self.secret = secret
        self.passphrase = passphrase
        self.order_callback = None
        self.trade_callback = None
    
    def _on_open(self, ws):
        """Handle connection open and authenticate."""
        super()._on_open(ws)
        # Send authentication
        auth_msg = {
            "auth": {
                "apiKey": self.api_key,
                "secret": self.secret,
                "passphrase": self.passphrase,
            }
        }
        self.send(auth_msg)
    
    def _handle_message(self, data: Dict[str, Any]):
        """Handle user channel messages."""
        msg_type = data.get("type")
        
        if msg_type == "order":
            if self.order_callback:
                self.order_callback(data)
        elif msg_type == "trade":
            if self.trade_callback:
                self.trade_callback(data)
    
    def subscribe(
        self,
        markets: List[str],
        on_order: Optional[Callable] = None,
        on_trade: Optional[Callable] = None,
    ):
        """
        Subscribe to user channel.
        
        Args:
            markets: List of market IDs or ["all"]
            on_order: Callback for order updates
            on_trade: Callback for trade updates
        """
        self.order_callback = on_order
        self.trade_callback = on_trade
        
        subscribe_msg = {
            "channel": "user",
            "markets": markets,
        }
        self.send(subscribe_msg)


class CLOBMarketWebSocket(BaseWebSocket):
    """WebSocket client for CLOB market channel."""
    
    def __init__(
        self,
        url: str = "wss://ws-subscriptions-clob.polymarket.com/ws/",
    ):
        """
        Initialize market channel WebSocket.
        
        Args:
            url: WebSocket URL
        """
        super().__init__(url)
        self.book_callback = None
        self.price_change_callback = None
        self.last_trade_callback = None
        self.tick_size_callback = None
    
    def _handle_message(self, data: Dict[str, Any]):
        """Handle market channel messages."""
        msg_type = data.get("type")
        
        if msg_type == "book":
            if self.book_callback:
                self.book_callback(data)
        elif msg_type == "price_change":
            if self.price_change_callback:
                self.price_change_callback(data)
        elif msg_type == "last_trade":
            if self.last_trade_callback:
                self.last_trade_callback(data)
        elif msg_type == "tick_size_change":
            if self.tick_size_callback:
                self.tick_size_callback(data)
    
    def subscribe_market(
        self,
        markets: Optional[List[str]] = None,
        asset_ids: Optional[List[str]] = None,
        on_book: Optional[Callable] = None,
        on_price_change: Optional[Callable] = None,
        on_last_trade: Optional[Callable] = None,
        on_tick_size_change: Optional[Callable] = None,
    ):
        """
        Subscribe to market channel.
        
        Args:
            markets: List of market IDs (optional)
            asset_ids: List of asset/token IDs (optional)
            on_book: Callback for full orderbook updates
            on_price_change: Callback for price level changes
            on_last_trade: Callback for last trade price
            on_tick_size_change: Callback for tick size changes
        """
        self.book_callback = on_book
        self.price_change_callback = on_price_change
        self.last_trade_callback = on_last_trade
        self.tick_size_callback = on_tick_size_change
        
        subscribe_msg = {
            "channel": "market",
        }
        
        if markets:
            subscribe_msg["markets"] = markets
        if asset_ids:
            subscribe_msg["asset_ids"] = asset_ids
        
        self.send(subscribe_msg)


class RTDSWebSocket(BaseWebSocket):
    """WebSocket client for Real-Time Data Socket (crypto prices, comments)."""
    
    def __init__(
        self,
        url: str = "wss://ws-live-data.polymarket.com",
    ):
        """
        Initialize RTDS WebSocket.
        
        Args:
            url: WebSocket URL
        """
        super().__init__(url)
        self.crypto_callback = None
        self.comment_callback = None
    
    def _handle_message(self, data: Dict[str, Any]):
        """Handle RTDS messages."""
        topic = data.get("topic")
        msg_type = data.get("type")
        
        if topic in ["crypto_prices", "crypto_prices_chainlink"]:
            if self.crypto_callback:
                self.crypto_callback(data)
        elif topic == "comments":
            if self.comment_callback:
                self.comment_callback(data)
    
    def subscribe_crypto_prices(
        self,
        source: str = "binance",
        pairs: Optional[List[str]] = None,
        callback: Optional[Callable] = None,
    ):
        """
        Subscribe to crypto price updates.
        
        Args:
            source: "binance" or "chainlink"
            pairs: List of trading pairs (e.g., ["btc/usdt", "eth/usdt"])
            callback: Callback for price updates
        """
        self.crypto_callback = callback
        
        topic = "crypto_prices" if source == "binance" else "crypto_prices_chainlink"
        
        subscribe_msg = {
            "action": "subscribe",
            "topic": topic,
        }
        
        if pairs:
            subscribe_msg["filters"] = pairs
        
        self.send(subscribe_msg)
    
    def subscribe_comments(
        self,
        callback: Optional[Callable] = None,
    ):
        """
        Subscribe to comment updates.
        
        Args:
            callback: Callback for comment events
        """
        self.comment_callback = callback
        
        subscribe_msg = {
            "action": "subscribe",
            "topic": "comments",
        }
        
        self.send(subscribe_msg)
    
    def unsubscribe(self, topic: str):
        """
        Unsubscribe from a topic.
        
        Args:
            topic: Topic to unsubscribe from
        """
        unsubscribe_msg = {
            "action": "unsubscribe",
            "topic": topic,
        }
        self.send(unsubscribe_msg)
