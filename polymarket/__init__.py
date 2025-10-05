"""Polymarket SDK - Python client for Polymarket APIs."""

from .auth import PolymarketAuth
from .clob import CLOBClient
from .data_api import DataAPIClient
from .gamma import GammaAPIClient
from .exceptions import PolymarketError, AuthenticationError, OrderError

__version__ = "0.1.0"

__all__ = [
    "PolymarketClient",
    "PolymarketAuth",
    "CLOBClient",
    "DataAPIClient",
    "GammaAPIClient",
    "PolymarketError",
    "AuthenticationError",
    "OrderError",
]


class PolymarketClient:
    """Main client for interacting with Polymarket APIs."""
    
    def __init__(
        self,
        private_key: str = None,
        proxy_wallet_address: str = None,
        api_key: str = None,
        secret: str = None,
        passphrase: str = None,
        clob_url: str = "https://clob.polymarket.com",
        data_url: str = "https://data-api.polymarket.com",
        gamma_url: str = "https://gamma-api.polymarket.com",
    ):
        """
        Initialize Polymarket client.
        
        Args:
            private_key: Wallet private key (for L1 authentication)
            proxy_wallet_address: Proxy wallet address
            api_key: API key (for L2 authentication)
            secret: API secret (for L2 authentication)
            passphrase: API passphrase (for L2 authentication)
            clob_url: CLOB API base URL
            data_url: Data API base URL
            gamma_url: Gamma API base URL
        """
        self.auth = PolymarketAuth(
            private_key=private_key,
            proxy_wallet_address=proxy_wallet_address,
            api_key=api_key,
            secret=secret,
            passphrase=passphrase,
        )
        
        self.clob = CLOBClient(
            clob_url=clob_url,
            auth=self.auth
        )
        
        self.data = DataAPIClient(
            data_url=data_url
        )
        
        self.gamma = GammaAPIClient(
            gamma_url=gamma_url
        )
