"""CLOB (Central Limit Order Book) API client."""

import json
import time
import secrets
from typing import Dict, List, Optional, Any
import requests
from .auth import PolymarketAuth
from .exceptions import OrderError, APIError


class CLOBClient:
    """Client for interacting with Polymarket CLOB API."""
    
    def __init__(self, clob_url: str, auth: PolymarketAuth):
        """
        Initialize CLOB client.
        
        Args:
            clob_url: CLOB API base URL
            auth: Authentication handler
        """
        self.base_url = clob_url.rstrip('/')
        self.auth = auth
        self.session = requests.Session()
    
    def _request(
        self,
        method: str,
        path: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None,
        auth_required: bool = True,
    ) -> Dict[str, Any]:
        """
        Make authenticated API request.
        
        Args:
            method: HTTP method
            path: API endpoint path
            data: Request body data
            params: Query parameters
            auth_required: Whether L2 authentication is required
            
        Returns:
            Response JSON data
        """
        url = f"{self.base_url}{path}"
        body = json.dumps(data) if data else ""
        
        headers = {}
        if auth_required:
            headers = self.auth.get_l2_headers(method, path, body)
        else:
            headers = {"Content-Type": "application/json"}
        
        response = self.session.request(
            method=method,
            url=url,
            headers=headers,
            data=body if data else None,
            params=params,
        )
        
        if response.status_code >= 400:
            raise APIError(
                f"API request failed: {response.text}",
                status_code=response.status_code
            )
        
        return response.json()
    
    def place_order(
        self,
        token_id: str,
        price: float,
        size: float,
        side: str,
        order_type: str = "GTC",
        expiration: Optional[int] = None,
        nonce: Optional[int] = None,
        fee_rate_bps: int = 0,
    ) -> Dict[str, Any]:
        """
        Place a single order.
        
        Args:
            token_id: Token ID (asset ID)
            price: Order price (0-1 for binary markets)
            size: Order size (amount)
            side: "BUY" or "SELL"
            order_type: "GTC", "GTD", "FOK", or "FAK"
            expiration: Expiration timestamp (required for GTD)
            nonce: Order nonce (random uint256)
            fee_rate_bps: Fee rate in basis points
            
        Returns:
            Order response with orderId and orderHash
        """
        if not self.auth.proxy_wallet_address:
            raise OrderError("Proxy wallet address required")
        
        # Convert side to numeric (0=buy, 1=sell)
        side_num = 0 if side.upper() == "BUY" else 1
        
        # Generate salt and nonce
        salt = secrets.randbits(256)
        if nonce is None:
            nonce = int(time.time() * 1000)
        
        # Default expiration: 30 days
        if expiration is None:
            expiration = int(time.time()) + (30 * 24 * 60 * 60)
        
        # Convert price and size to integers (assuming 6 decimals for USDC)
        maker_amount = int(size * 1e6)
        taker_amount = int((size * price) * 1e6) if side_num == 1 else int((size / price) * 1e6)
        
        order_data = {
            "salt": salt,
            "maker": self.auth.proxy_wallet_address,
            "signer": self.auth.address or self.auth.proxy_wallet_address,
            "taker": "0x0000000000000000000000000000000000000000",
            "tokenId": int(token_id),
            "makerAmount": maker_amount,
            "takerAmount": taker_amount,
            "expiration": expiration,
            "nonce": nonce,
            "feeRateBps": fee_rate_bps,
            "side": side_num,
            "signatureType": 0,  # EOA signature
        }
        
        # Sign the order
        signature = self.auth.sign_order(order_data)
        order_data["signature"] = signature
        
        payload = {
            "order": order_data,
            "orderType": order_type,
            "owner": self.auth.proxy_wallet_address,
        }
        
        try:
            response = self._request("POST", "/order", data=payload)
            
            if not response.get("success"):
                error_code = response.get("errorCode", "UNKNOWN")
                raise OrderError(f"Order failed: {response}", error_code=error_code)
            
            return response
        except APIError as e:
            raise OrderError(f"Failed to place order: {e}")
    
    def place_batch_orders(
        self,
        orders: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Place multiple orders (up to 15).
        
        Args:
            orders: List of order dictionaries with same structure as place_order
            
        Returns:
            Batch order response
        """
        if len(orders) > 15:
            raise OrderError("Maximum 15 orders per batch")
        
        payload = []
        for order_params in orders:
            # Build each order similar to place_order
            token_id = order_params["token_id"]
            price = order_params["price"]
            size = order_params["size"]
            side = order_params["side"]
            order_type = order_params.get("order_type", "GTC")
            
            side_num = 0 if side.upper() == "BUY" else 1
            salt = secrets.randbits(256)
            nonce = int(time.time() * 1000)
            expiration = order_params.get("expiration", int(time.time()) + (30 * 24 * 60 * 60))
            
            maker_amount = int(size * 1e6)
            taker_amount = int((size * price) * 1e6) if side_num == 1 else int((size / price) * 1e6)
            
            order_data = {
                "salt": salt,
                "maker": self.auth.proxy_wallet_address,
                "signer": self.auth.address or self.auth.proxy_wallet_address,
                "taker": "0x0000000000000000000000000000000000000000",
                "tokenId": int(token_id),
                "makerAmount": maker_amount,
                "takerAmount": taker_amount,
                "expiration": expiration,
                "nonce": nonce,
                "feeRateBps": order_params.get("fee_rate_bps", 0),
                "side": side_num,
                "signatureType": 0,
            }
            
            signature = self.auth.sign_order(order_data)
            order_data["signature"] = signature
            
            payload.append({
                "order": order_data,
                "orderType": order_type,
                "owner": self.auth.proxy_wallet_address,
            })
        
        try:
            response = self._request("POST", "/orders", data=payload)
            return response
        except APIError as e:
            raise OrderError(f"Failed to place batch orders: {e}")
    
    def get_order(self, order_hash: str) -> Dict[str, Any]:
        """
        Get order details by hash.
        
        Args:
            order_hash: Order hash
            
        Returns:
            Order details
        """
        return self._request("GET", f"/data/order/{order_hash}")
    
    def get_active_orders(
        self,
        market: Optional[str] = None,
        asset_id: Optional[str] = None,
        order_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        Get active orders.
        
        Args:
            market: Market slug or ID
            asset_id: Asset/token ID
            order_id: Specific order ID
            limit: Number of orders to return
            offset: Pagination offset
            
        Returns:
            List of active orders
        """
        params = {
            "limit": limit,
            "offset": offset,
        }
        
        if market:
            params["market"] = market
        if asset_id:
            params["asset_id"] = asset_id
        if order_id:
            params["order_id"] = order_id
        
        return self._request("GET", "/data/orders", params=params)
    
    def check_order_scoring(
        self,
        order_ids: List[str],
    ) -> Dict[str, bool]:
        """
        Check if orders count toward liquidity rewards.
        
        Args:
            order_ids: List of order IDs
            
        Returns:
            Dictionary mapping order ID to scoring status
        """
        if len(order_ids) == 1:
            response = self._request("GET", "/order-scoring", params={"order_id": order_ids[0]})
            return {order_ids[0]: response.get("scoring", False)}
        else:
            response = self._request("POST", "/orders-scoring", data={"order_ids": order_ids})
            return response
    
    def cancel_order(self, order_id: str) -> Dict[str, Any]:
        """
        Cancel a single order.
        
        Args:
            order_id: Order ID to cancel
            
        Returns:
            Cancellation response
        """
        return self._request("DELETE", "/order", data={"id": order_id})
    
    def cancel_orders(self, order_ids: List[str]) -> Dict[str, Any]:
        """
        Cancel multiple orders.
        
        Args:
            order_ids: List of order IDs to cancel
            
        Returns:
            Cancellation response with cancelled and notCancelled arrays
        """
        return self._request("DELETE", "/orders", data={"order_ids": order_ids})
    
    def cancel_all_orders(self) -> Dict[str, Any]:
        """
        Cancel all orders.
        
        Returns:
            Cancellation response
        """
        return self._request("DELETE", "/cancel-all")
    
    def cancel_market_orders(self, market: str) -> Dict[str, Any]:
        """
        Cancel all orders for a specific market.
        
        Args:
            market: Market slug
            
        Returns:
            Cancellation response
        """
        return self._request("DELETE", "/cancel-market-orders", params={"market": market})
