"""Data API client for Polymarket."""

from typing import Dict, List, Optional, Any
import requests
from .exceptions import APIError


class DataAPIClient:
    """Client for Polymarket Data API (positions, trades, holders, portfolio)."""
    
    def __init__(self, data_url: str):
        """
        Initialize Data API client.
        
        Args:
            data_url: Data API base URL
        """
        self.base_url = data_url.rstrip('/')
        self.session = requests.Session()
    
    def _request(
        self,
        method: str,
        path: str,
        params: Optional[Dict] = None,
    ) -> Any:
        """
        Make API request.
        
        Args:
            method: HTTP method
            path: API endpoint path
            params: Query parameters
            
        Returns:
            Response data
        """
        url = f"{self.base_url}{path}"
        
        response = self.session.request(
            method=method,
            url=url,
            params=params,
        )
        
        if response.status_code >= 400:
            raise APIError(
                f"API request failed: {response.text}",
                status_code=response.status_code
            )
        
        return response.json()
    
    def get_positions(
        self,
        user: str,
        market: Optional[str] = None,
        event: Optional[str] = None,
        closed: Optional[bool] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        Get user positions.
        
        Args:
            user: Proxy wallet address
            market: Market slug or ID (optional)
            event: Event ID or slug (optional)
            closed: Filter by closed positions (optional)
            limit: Number of results
            offset: Pagination offset
            
        Returns:
            List of position objects with:
            - proxyWallet, asset, conditionId, size, avgPrice
            - initialValue, currentValue, cashPnl, percentPnl
            - totalBought, realizedPnl, curPrice
            - redeemable, mergeable
            - event and market metadata
        """
        params = {
            "user": user,
            "limit": limit,
            "offset": offset,
        }
        
        if market:
            params["market"] = market
        if event:
            params["event"] = event
        if closed is not None:
            params["closed"] = str(closed).lower()
        
        return self._request("GET", "/positions", params=params)
    
    def get_trades(
        self,
        user: Optional[str] = None,
        market: Optional[str] = None,
        event: Optional[str] = None,
        from_timestamp: Optional[int] = None,
        to_timestamp: Optional[int] = None,
        side: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        Get trade history.
        
        Args:
            user: Proxy wallet address (optional)
            market: Market slug or ID (optional)
            event: Event ID or slug (optional)
            from_timestamp: Start timestamp (optional)
            to_timestamp: End timestamp (optional)
            side: "buy" or "sell" (optional)
            limit: Number of results
            offset: Pagination offset
            
        Returns:
            List of trade objects with:
            - proxyWallet, taker, maker, asset, conditionId
            - size, price, timestamp, transactionHash
            - event and market metadata
            - status, side
            - makerOrders (list of matched orders)
        """
        params = {
            "limit": limit,
            "offset": offset,
        }
        
        if user:
            params["user"] = user
        if market:
            params["market"] = market
        if event:
            params["event"] = event
        if from_timestamp:
            params["from"] = from_timestamp
        if to_timestamp:
            params["to"] = to_timestamp
        if side:
            params["side"] = side.lower()
        
        return self._request("GET", "/trades", params=params)
    
    def get_holders(
        self,
        market: str,
        limit: int = 100,
        min_balance: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Get token holders for a market.
        
        Args:
            market: Condition ID (token ID) or market slug
            limit: Number of holders to return
            min_balance: Minimum balance filter (optional)
            
        Returns:
            Dictionary with:
            - token: Condition ID
            - holders: Array of holder objects with:
              - proxyWallet, amount, pseudonym
              - displayUsernamePublic, profileImage, name
        """
        params = {
            "market": market,
            "limit": limit,
        }
        
        if min_balance:
            params["minBalance"] = min_balance
        
        return self._request("GET", "/holders", params=params)
    
    def get_portfolio_value(
        self,
        user: str,
        markets: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Get total portfolio value for a user.
        
        Args:
            user: Proxy wallet address
            markets: Optional list of market slugs/IDs to filter
            
        Returns:
            Dictionary with:
            - user: Wallet address
            - value: Sum of current values of all positions
        """
        params = {
            "user": user,
        }
        
        if markets:
            params["market"] = markets
        
        return self._request("GET", "/value", params=params)
    
    def get_activity(
        self,
        user: str,
        market: Optional[str] = None,
        event: Optional[str] = None,
        activity_type: Optional[str] = None,
        side: Optional[str] = None,
        from_timestamp: Optional[int] = None,
        to_timestamp: Optional[int] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        Get user activity (trades, conversions, splits, merges).
        
        Args:
            user: Proxy wallet address
            market: Market slug or ID (optional)
            event: Event ID or slug (optional)
            activity_type: "TRADE", "CONVERT", "SPLIT", "MERGE" (optional)
            side: "BUY" or "SELL" (optional)
            from_timestamp: Start timestamp (optional)
            to_timestamp: End timestamp (optional)
            limit: Number of results
            offset: Pagination offset
            
        Returns:
            List of activity records with:
            - timestamp, conditionId, type, size, usdcSize
            - transactionHash, price, asset, side
            - event and market metadata
            - user profile fields
        """
        params = {
            "user": user,
            "limit": limit,
            "offset": offset,
        }
        
        if market:
            params["market"] = market
        if event:
            params["event"] = event
        if activity_type:
            params["type"] = activity_type.upper()
        if side:
            params["side"] = side.upper()
        if from_timestamp:
            params["from"] = from_timestamp
        if to_timestamp:
            params["to"] = to_timestamp
        
        return self._request("GET", "/activity", params=params)
