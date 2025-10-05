"""Authentication module for Polymarket API."""

import time
import hmac
import hashlib
from typing import Dict, Optional
from eth_account import Account
from eth_account.messages import encode_typed_data
from .exceptions import AuthenticationError


class PolymarketAuth:
    """Handles L1 (EIP-712) and L2 (API key) authentication for Polymarket."""
    
    def __init__(
        self,
        private_key: Optional[str] = None,
        proxy_wallet_address: Optional[str] = None,
        api_key: Optional[str] = None,
        secret: Optional[str] = None,
        passphrase: Optional[str] = None,
    ):
        """
        Initialize authentication handler.
        
        Args:
            private_key: Ethereum wallet private key (for L1 signing)
            proxy_wallet_address: Proxy wallet address
            api_key: API key for L2 authentication
            secret: API secret for L2 authentication
            passphrase: API passphrase for L2 authentication
        """
        self.private_key = private_key
        self.proxy_wallet_address = proxy_wallet_address
        self.api_key = api_key
        self.secret = secret
        self.passphrase = passphrase
        
        if private_key:
            self.account = Account.from_key(private_key)
            self.address = self.account.address
        else:
            self.account = None
            self.address = None
    
    def sign_eip712_message(self, message: Dict) -> str:
        """
        Sign an EIP-712 message (L1 authentication).
        
        Args:
            message: EIP-712 structured data
            
        Returns:
            Signature as hex string
        """
        if not self.account:
            raise AuthenticationError("Private key not provided for L1 signing")
        
        encoded_message = encode_typed_data(full_message=message)
        signed_message = self.account.sign_message(encoded_message)
        return signed_message.signature.hex()
    
    def sign_order(self, order_data: Dict) -> str:
        """
        Sign an order using EIP-712.
        
        Args:
            order_data: Order data to sign
            
        Returns:
            Signature as hex string
        """
        eip712_message = {
            "types": {
                "EIP712Domain": [
                    {"name": "name", "type": "string"},
                    {"name": "version", "type": "string"},
                    {"name": "chainId", "type": "uint256"},
                    {"name": "verifyingContract", "type": "address"},
                ],
                "Order": [
                    {"name": "salt", "type": "uint256"},
                    {"name": "maker", "type": "address"},
                    {"name": "signer", "type": "address"},
                    {"name": "taker", "type": "address"},
                    {"name": "tokenId", "type": "uint256"},
                    {"name": "makerAmount", "type": "uint256"},
                    {"name": "takerAmount", "type": "uint256"},
                    {"name": "expiration", "type": "uint256"},
                    {"name": "nonce", "type": "uint256"},
                    {"name": "feeRateBps", "type": "uint256"},
                    {"name": "side", "type": "uint8"},
                    {"name": "signatureType", "type": "uint8"},
                ],
            },
            "domain": {
                "name": "Polymarket CTF Exchange",
                "version": "1",
                "chainId": 137,  # Polygon mainnet
                "verifyingContract": "0x4bFb41d5B3570DeFd03C39a9A4D8dE6Bd8B8982E",
            },
            "primaryType": "Order",
            "message": order_data,
        }
        
        return self.sign_eip712_message(eip712_message)
    
    def get_l2_headers(
        self,
        method: str,
        path: str,
        body: str = "",
    ) -> Dict[str, str]:
        """
        Generate L2 authentication headers for CLOB API.
        
        Args:
            method: HTTP method (GET, POST, DELETE)
            path: API endpoint path
            body: Request body (for POST/DELETE)
            
        Returns:
            Dictionary of authentication headers
        """
        if not all([self.api_key, self.secret, self.passphrase]):
            raise AuthenticationError("API key, secret, and passphrase required for L2 authentication")
        
        timestamp = str(int(time.time()))
        nonce = str(int(time.time() * 1000))
        
        # Create signature: HMAC-SHA256 of timestamp + method + path + body
        message = f"{timestamp}{method.upper()}{path}{body}"
        signature = hmac.new(
            self.secret.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return {
            "POLY_ADDRESS": self.proxy_wallet_address or "",
            "POLY_SIGNATURE": signature,
            "POLY_TIMESTAMP": timestamp,
            "POLY_NONCE": nonce,
            "POLY_API_KEY": self.api_key,
            "POLY_PASSPHRASE": self.passphrase,
            "Content-Type": "application/json",
        }
    
    def derive_api_key(self, clob_url: str) -> Dict[str, str]:
        """
        Derive API key from L1 signature (call /auth/api-key endpoint).
        
        Args:
            clob_url: CLOB API base URL
            
        Returns:
            Dictionary with 'apiKey', 'secret', 'passphrase'
        """
        import requests
        
        if not self.account:
            raise AuthenticationError("Private key required to derive API key")
        
        # Create EIP-712 message for API key derivation
        timestamp = int(time.time())
        message = {
            "types": {
                "EIP712Domain": [
                    {"name": "name", "type": "string"},
                ],
                "Polymarket": [
                    {"name": "timestamp", "type": "uint256"},
                ],
            },
            "domain": {
                "name": "Polymarket",
            },
            "primaryType": "Polymarket",
            "message": {
                "timestamp": timestamp,
            },
        }
        
        signature = self.sign_eip712_message(message)
        
        response = requests.post(
            f"{clob_url}/auth/api-key",
            json={
                "address": self.address,
                "timestamp": timestamp,
                "signature": signature,
            }
        )
        
        if response.status_code != 200:
            raise AuthenticationError(f"Failed to derive API key: {response.text}")
        
        data = response.json()
        
        # Update credentials
        self.api_key = data["apiKey"]
        self.secret = data["secret"]
        self.passphrase = data["passphrase"]
        
        return data
