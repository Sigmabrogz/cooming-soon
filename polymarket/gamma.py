"""Gamma API client for Polymarket."""

from typing import Dict, List, Optional, Any
import requests
from .exceptions import APIError


class GammaAPIClient:
    """Client for Polymarket Gamma API (markets, events, tags)."""
    
    def __init__(self, gamma_url: str):
        """
        Initialize Gamma API client.
        
        Args:
            gamma_url: Gamma API base URL
        """
        self.base_url = gamma_url.rstrip('/')
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
    
    def get_events(
        self,
        limit: int = 100,
        offset: int = 0,
        order: str = "id",
        ascending: bool = False,
        closed: Optional[bool] = None,
        tag_id: Optional[str] = None,
        sport: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        List events.
        
        Args:
            limit: Number of results
            offset: Pagination offset
            order: Sort field ("id", "liquidity", "volume")
            ascending: Sort order
            closed: Filter by closed status
            tag_id: Filter by tag ID
            sport: Filter by sport
            
        Returns:
            List of event objects with:
            - id, name, slug, description
            - startDate, endDate
            - liquidity, volume
            - negRisk, enableNegRisk, negRiskAugmented
            - markets array
        """
        params = {
            "limit": limit,
            "offset": offset,
            "order": order,
            "ascending": str(ascending).lower(),
        }
        
        if closed is not None:
            params["closed"] = str(closed).lower()
        if tag_id:
            params["tag_id"] = tag_id
        if sport:
            params["sport"] = sport
        
        return self._request("GET", "/events", params=params)
    
    def get_event_by_slug(self, slug: str) -> Dict[str, Any]:
        """
        Get event by slug.
        
        Args:
            slug: Event slug
            
        Returns:
            Event object
        """
        return self._request("GET", f"/events/{slug}")
    
    def get_markets(
        self,
        limit: int = 100,
        offset: int = 0,
        closed: Optional[bool] = None,
        event: Optional[str] = None,
        tag_id: Optional[str] = None,
        sport: Optional[str] = None,
        order: str = "id",
        ascending: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        List markets.
        
        Args:
            limit: Number of results
            offset: Pagination offset
            closed: Filter by closed status
            event: Filter by event ID or slug
            tag_id: Filter by tag ID
            sport: Filter by sport
            order: Sort field
            ascending: Sort order
            
        Returns:
            List of market objects with:
            - id, questionId, conditionId
            - token0Id, token1Id
            - category, title, slug, type
            - endDate, liquidity, volume, status
            - minOrderSize, tickSize
            - rewardRateMin, rewardRateMax
            - incentiveParameters
        """
        params = {
            "limit": limit,
            "offset": offset,
            "order": order,
            "ascending": str(ascending).lower(),
        }
        
        if closed is not None:
            params["closed"] = str(closed).lower()
        if event:
            params["event"] = event
        if tag_id:
            params["tag_id"] = tag_id
        if sport:
            params["sport"] = sport
        
        return self._request("GET", "/markets", params=params)
    
    def get_market_by_slug(self, slug: str) -> Dict[str, Any]:
        """
        Get market by slug.
        
        Args:
            slug: Market slug
            
        Returns:
            Market object
        """
        return self._request("GET", f"/markets/{slug}")
    
    def get_tags(self) -> List[Dict[str, Any]]:
        """
        Get all tags.
        
        Returns:
            List of tag objects with:
            - id, label, slug, forceShow
        """
        return self._request("GET", "/tags")
    
    def get_tag_by_id(self, tag_id: str) -> Dict[str, Any]:
        """
        Get tag by ID.
        
        Args:
            tag_id: Tag ID
            
        Returns:
            Tag object
        """
        return self._request("GET", f"/tags/{tag_id}")
    
    def get_tag_by_slug(self, slug: str) -> Dict[str, Any]:
        """
        Get tag by slug.
        
        Args:
            slug: Tag slug
            
        Returns:
            Tag object
        """
        return self._request("GET", f"/tags/slug/{slug}")
    
    def get_sports(self) -> List[Dict[str, Any]]:
        """
        Get sports metadata.
        
        Returns:
            List of sport objects
        """
        return self._request("GET", "/sports")
    
    def get_teams(self) -> List[Dict[str, Any]]:
        """
        Get teams.
        
        Returns:
            List of team objects with:
            - id, name, league, logo, record
        """
        return self._request("GET", "/teams")
