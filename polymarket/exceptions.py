"""Custom exceptions for Polymarket SDK."""


class PolymarketError(Exception):
    """Base exception for Polymarket SDK."""
    pass


class AuthenticationError(PolymarketError):
    """Raised when authentication fails."""
    pass


class OrderError(PolymarketError):
    """Raised when order placement or management fails."""
    
    def __init__(self, message: str, error_code: str = None):
        super().__init__(message)
        self.error_code = error_code


class APIError(PolymarketError):
    """Raised when API request fails."""
    
    def __init__(self, message: str, status_code: int = None):
        super().__init__(message)
        self.status_code = status_code


class WebSocketError(PolymarketError):
    """Raised when WebSocket connection fails."""
    pass
