# API Reference

Comprehensive reference for the Polymarket SDK.

## Table of Contents

- [PolymarketClient](#polymarketclient)
- [Authentication](#authentication)
- [CLOB API](#clob-api)
- [Data API](#data-api)
- [Gamma API](#gamma-api)
- [WebSocket Clients](#websocket-clients)

---

## PolymarketClient

Main client class for accessing all Polymarket APIs.

### Constructor

```python
PolymarketClient(
    private_key: str = None,
    proxy_wallet_address: str = None,
    api_key: str = None,
    secret: str = None,
    passphrase: str = None,
    clob_url: str = "https://clob.polymarket.com",
    data_url: str = "https://data-api.polymarket.com",
    gamma_url: str = "https://gamma-api.polymarket.com",
)
```

**Parameters:**
- `private_key`: Wallet private key (for L1 authentication and order signing)
- `proxy_wallet_address`: Proxy wallet address
- `api_key`: API key (for L2 authentication)
- `secret`: API secret (for L2 authentication)
- `passphrase`: API passphrase (for L2 authentication)
- `clob_url`: CLOB API base URL (optional)
- `data_url`: Data API base URL (optional)
- `gamma_url`: Gamma API base URL (optional)

**Properties:**
- `client.auth`: Authentication handler
- `client.clob`: CLOB API client
- `client.data`: Data API client
- `client.gamma`: Gamma API client

---

## Authentication

### PolymarketAuth

Handles L1 (EIP-712) and L2 (API key) authentication.

#### Methods

##### `sign_eip712_message(message: Dict) -> str`
Sign an EIP-712 message.

##### `sign_order(order_data: Dict) -> str`
Sign an order using EIP-712.

##### `get_l2_headers(method: str, path: str, body: str = "") -> Dict[str, str]`
Generate L2 authentication headers for CLOB API.

##### `derive_api_key(clob_url: str) -> Dict[str, str]`
Derive API credentials from L1 signature.

**Returns:** Dictionary with `apiKey`, `secret`, `passphrase`

---

## CLOB API

Central Limit Order Book API for order placement and management.

### CLOBClient

#### Order Placement

##### `place_order()`
```python
place_order(
    token_id: str,
    price: float,
    size: float,
    side: str,
    order_type: str = "GTC",
    expiration: Optional[int] = None,
    nonce: Optional[int] = None,
    fee_rate_bps: int = 0,
) -> Dict[str, Any]
```

Place a single order.

**Parameters:**
- `token_id`: Token/asset ID
- `price`: Order price (0-1 for binary markets)
- `size`: Order size (amount)
- `side`: "BUY" or "SELL"
- `order_type`: "GTC", "GTD", "FOK", or "FAK"
- `expiration`: Expiration timestamp (optional, defaults to 30 days)
- `nonce`: Order nonce (optional, auto-generated)
- `fee_rate_bps`: Fee rate in basis points

**Returns:** Order response with `orderId`, `orderHash`, `success`

**Raises:** `OrderError` if order fails

##### `place_batch_orders()`
```python
place_batch_orders(orders: List[Dict[str, Any]]) -> Dict[str, Any]
```

Place up to 15 orders at once.

**Parameters:**
- `orders`: List of order dictionaries with same structure as `place_order()`

**Returns:** Batch order response

#### Order Management

##### `get_order()`
```python
get_order(order_hash: str) -> Dict[str, Any]
```

Get order details by hash.

##### `get_active_orders()`
```python
get_active_orders(
    market: Optional[str] = None,
    asset_id: Optional[str] = None,
    order_id: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
) -> List[Dict[str, Any]]
```

Get active orders with optional filters.

##### `check_order_scoring()`
```python
check_order_scoring(order_ids: List[str]) -> Dict[str, bool]
```

Check if orders count toward liquidity rewards.

#### Order Cancellation

##### `cancel_order()`
```python
cancel_order(order_id: str) -> Dict[str, Any]
```

Cancel a single order.

##### `cancel_orders()`
```python
cancel_orders(order_ids: List[str]) -> Dict[str, Any]
```

Cancel multiple orders.

##### `cancel_all_orders()`
```python
cancel_all_orders() -> Dict[str, Any]
```

Cancel all orders.

##### `cancel_market_orders()`
```python
cancel_market_orders(market: str) -> Dict[str, Any]
```

Cancel all orders for a specific market.

---

## Data API

Read-only API for positions, trades, holders, and portfolio data.

### DataAPIClient

#### `get_positions()`
```python
get_positions(
    user: str,
    market: Optional[str] = None,
    event: Optional[str] = None,
    closed: Optional[bool] = None,
    limit: int = 100,
    offset: int = 0,
) -> List[Dict[str, Any]]
```

Get user positions.

**Returns:** List of position objects with:
- `proxyWallet`, `asset`, `conditionId`
- `size`, `avgPrice`, `curPrice`
- `initialValue`, `currentValue`
- `cashPnl`, `percentPnl`, `realizedPnl`
- `redeemable`, `mergeable`
- Event and market metadata

#### `get_trades()`
```python
get_trades(
    user: Optional[str] = None,
    market: Optional[str] = None,
    event: Optional[str] = None,
    from_timestamp: Optional[int] = None,
    to_timestamp: Optional[int] = None,
    side: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
) -> List[Dict[str, Any]]
```

Get trade history.

**Returns:** List of trade objects with:
- `proxyWallet`, `taker`, `maker`
- `asset`, `conditionId`
- `size`, `price`, `timestamp`
- `transactionHash`, `status`, `side`
- Event and market metadata

#### `get_holders()`
```python
get_holders(
    market: str,
    limit: int = 100,
    min_balance: Optional[float] = None,
) -> Dict[str, Any]
```

Get token holders for a market.

**Returns:** Dictionary with:
- `token`: Condition ID
- `holders`: Array of holder objects

#### `get_portfolio_value()`
```python
get_portfolio_value(
    user: str,
    markets: Optional[List[str]] = None,
) -> Dict[str, Any]
```

Get total portfolio value.

**Returns:** Dictionary with `user` and `value`

#### `get_activity()`
```python
get_activity(
    user: str,
    market: Optional[str] = None,
    event: Optional[str] = None,
    activity_type: Optional[str] = None,
    side: Optional[str] = None,
    from_timestamp: Optional[int] = None,
    to_timestamp: Optional[int] = None,
    limit: int = 100,
    offset: int = 0,
) -> List[Dict[str, Any]]
```

Get user activity (trades, conversions, splits, merges).

**Parameters:**
- `activity_type`: "TRADE", "CONVERT", "SPLIT", "MERGE"
- `side`: "BUY" or "SELL"

---

## Gamma API

Read-only API for markets, events, tags, and sports.

### GammaAPIClient

#### `get_events()`
```python
get_events(
    limit: int = 100,
    offset: int = 0,
    order: str = "id",
    ascending: bool = False,
    closed: Optional[bool] = None,
    tag_id: Optional[str] = None,
    sport: Optional[str] = None,
) -> List[Dict[str, Any]]
```

List events.

**Parameters:**
- `order`: Sort field ("id", "liquidity", "volume")

#### `get_event_by_slug()`
```python
get_event_by_slug(slug: str) -> Dict[str, Any]
```

Get event by slug.

#### `get_markets()`
```python
get_markets(
    limit: int = 100,
    offset: int = 0,
    closed: Optional[bool] = None,
    event: Optional[str] = None,
    tag_id: Optional[str] = None,
    sport: Optional[str] = None,
    order: str = "id",
    ascending: bool = False,
) -> List[Dict[str, Any]]
```

List markets.

#### `get_market_by_slug()`
```python
get_market_by_slug(slug: str) -> Dict[str, Any]
```

Get market by slug.

#### `get_tags()`
```python
get_tags() -> List[Dict[str, Any]]
```

Get all tags.

#### `get_tag_by_id()` / `get_tag_by_slug()`
```python
get_tag_by_id(tag_id: str) -> Dict[str, Any]
get_tag_by_slug(slug: str) -> Dict[str, Any]
```

Get tag by ID or slug.

#### `get_sports()`
```python
get_sports() -> List[Dict[str, Any]]
```

Get sports metadata.

#### `get_teams()`
```python
get_teams() -> List[Dict[str, Any]]
```

Get teams data.

---

## WebSocket Clients

Real-time data streaming clients.

### CLOBUserWebSocket

Subscribe to user-specific order and trade updates.

```python
CLOBUserWebSocket(
    api_key: str,
    secret: str,
    passphrase: str,
    url: str = "wss://ws-subscriptions-clob.polymarket.com/ws/",
)
```

#### Methods

##### `subscribe()`
```python
subscribe(
    markets: List[str],
    on_order: Optional[Callable] = None,
    on_trade: Optional[Callable] = None,
)
```

Subscribe to user channel.

**Parameters:**
- `markets`: List of market IDs or `["all"]`
- `on_order`: Callback for order updates
- `on_trade`: Callback for trade updates

### CLOBMarketWebSocket

Subscribe to market orderbook and price updates.

```python
CLOBMarketWebSocket(
    url: str = "wss://ws-subscriptions-clob.polymarket.com/ws/",
)
```

#### Methods

##### `subscribe_market()`
```python
subscribe_market(
    markets: Optional[List[str]] = None,
    asset_ids: Optional[List[str]] = None,
    on_book: Optional[Callable] = None,
    on_price_change: Optional[Callable] = None,
    on_last_trade: Optional[Callable] = None,
    on_tick_size_change: Optional[Callable] = None,
)
```

Subscribe to market channel.

### RTDSWebSocket

Real-Time Data Socket for crypto prices and comments.

```python
RTDSWebSocket(
    url: str = "wss://ws-live-data.polymarket.com",
)
```

#### Methods

##### `subscribe_crypto_prices()`
```python
subscribe_crypto_prices(
    source: str = "binance",
    pairs: Optional[List[str]] = None,
    callback: Optional[Callable] = None,
)
```

Subscribe to crypto price updates.

**Parameters:**
- `source`: "binance" or "chainlink"
- `pairs`: List of trading pairs (e.g., `["btc/usdt", "eth/usdt"]`)

##### `subscribe_comments()`
```python
subscribe_comments(callback: Optional[Callable] = None)
```

Subscribe to comment updates.

##### `unsubscribe()`
```python
unsubscribe(topic: str)
```

Unsubscribe from a topic.

---

## Error Handling

### Exceptions

All custom exceptions inherit from `PolymarketError`.

- **`PolymarketError`**: Base exception
- **`AuthenticationError`**: Authentication failures
- **`OrderError`**: Order placement/management failures
  - Properties: `error_code`
- **`APIError`**: API request failures
  - Properties: `status_code`
- **`WebSocketError`**: WebSocket connection failures

### Example

```python
from polymarket import PolymarketClient
from polymarket.exceptions import OrderError, AuthenticationError

try:
    client = PolymarketClient(...)
    order = client.clob.place_order(...)
except AuthenticationError as e:
    print(f"Authentication failed: {e}")
except OrderError as e:
    print(f"Order failed: {e} (code: {e.error_code})")
```

---

## Models

Pydantic models for type safety and validation.

- `Order`
- `Position`
- `Trade`
- `Market`
- `Event`
- `Holder`
- `OrderBook`
- `PriceUpdate`
- `CommentEvent`

### Enums

- `OrderSide`: BUY, SELL
- `OrderType`: GTC, GTD, FOK, FAK
- `OrderStatus`: LIVE, MATCHED, CANCELLED, EXPIRED
- `ActivityType`: TRADE, CONVERT, SPLIT, MERGE
